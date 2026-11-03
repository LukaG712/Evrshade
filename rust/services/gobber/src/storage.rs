//! SQLite storage backend for the Knowledge Graph module in Gobber.

use anyhow::Result;
use chrono::Utc;
use sea_orm::{ConnectionTrait, DatabaseConnection, QueryResult, Statement};
use std::collections::HashMap;

use crate::models::{Note, SearchResult};

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    links TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS note_links (
    source_note_id TEXT NOT NULL,
    target_note_id TEXT NOT NULL,
    PRIMARY KEY (source_note_id, target_note_id),
    FOREIGN KEY (source_note_id) REFERENCES notes(id),
    FOREIGN KEY (target_note_id) REFERENCES notes(id)
);

CREATE TABLE IF NOT EXISTS note_embeddings (
    note_id TEXT PRIMARY KEY,
    embedding TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (note_id) REFERENCES notes(id)
);

CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);
CREATE INDEX IF NOT EXISTS idx_note_links_source ON note_links(source_note_id);
CREATE INDEX IF NOT EXISTS idx_note_links_target ON note_links(target_note_id);
"#;

pub async fn init_db(db: &DatabaseConnection) -> Result<()> {
    db.execute(Statement::from_string(
        db.get_database_backend(),
        SCHEMA_SQL.to_string(),
    ))
    .await?;
    Ok(())
}

/// Compute cosine similarity between two vectors.
pub fn cosine_similarity(a: &[f64], b: &[f64]) -> f64 {
    if a.len() != b.len() {
        return 0.0;
    }
    let dot: f64 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
    let norm_a: f64 = a.iter().map(|x| x * x).sum::<f64>().sqrt();
    let norm_b: f64 = b.iter().map(|x| x * x).sum::<f64>().sqrt();
    if norm_a == 0.0 || norm_b == 0.0 {
        return 0.0;
    }
    dot / (norm_a * norm_b)
}

/// Extract a relevant excerpt from the note content.
pub fn extract_relevant_context(content: &str, max_length: usize) -> Option<String> {
    if content.trim().is_empty() {
        return None;
    }
    let sentences: Vec<&str> = content
        .split(['.', '!', '?'])
        .collect();
    for sentence in sentences {
        let trimmed = sentence.trim();
        if trimmed.len() > 10 {
            let context = if trimmed.len() > max_length {
                format!("{}...", &trimmed[..max_length])
            } else {
                trimmed.to_string()
            };
            return Some(context);
        }
    }
    if content.len() > max_length {
        Some(format!("{}...", &content[..max_length]))
    } else {
        Some(content.to_string())
    }
}

/// Knowledge graph storage operations.
pub struct KnowledgeGraphStorage {
    db: DatabaseConnection,
}

impl KnowledgeGraphStorage {
    pub fn new(db: DatabaseConnection) -> Self {
        Self { db }
    }

    /// Insert or update a note.
    pub async fn upsert_note(&self, note: &Note) -> Result<()> {
        let links_json = serde_json::to_string(&note.links)?;
        let sql = format!(
            "INSERT INTO notes (id, file_path, title, content, links, created_at, updated_at)
             VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')
             ON CONFLICT(file_path) DO UPDATE SET
                 id=excluded.id,
                 title=excluded.title,
                 content=excluded.content,
                 links=excluded.links,
                 updated_at=excluded.updated_at",
            escape_sql(&note.id),
            escape_sql(&note.file_path),
            escape_sql(&note.title),
            escape_sql(&note.content),
            links_json,
            note.created_at.format("%Y-%m-%dT%H:%M:%SZ"),
            note.updated_at.format("%Y-%m-%dT%H:%M:%SZ"),
        );
        self.db
            .execute(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        Ok(())
    }

    /// Get a note by ID.
    pub async fn get_note(&self, note_id: &str) -> Result<Option<Note>> {
        let sql = format!("SELECT * FROM notes WHERE id = '{}'", escape_sql(note_id));
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        if rows.is_empty() {
            return Ok(None);
        }
        let row = &rows[0];
        Ok(Some(row_to_note(row)))
    }

    /// Get a note by file path.
    pub async fn get_note_by_path(&self, file_path: &str) -> Result<Option<Note>> {
        let sql = format!(
            "SELECT * FROM notes WHERE file_path = '{}'",
            escape_sql(file_path)
        );
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        if rows.is_empty() {
            return Ok(None);
        }
        let row = &rows[0];
        Ok(Some(row_to_note(row)))
    }

    /// List all notes with pagination.
    pub async fn list_notes(&self, limit: usize, offset: usize) -> Result<Vec<Note>> {
        let sql = format!(
            "SELECT * FROM notes ORDER BY updated_at DESC LIMIT {} OFFSET {}",
            limit, offset
        );
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        Ok(rows.into_iter().map(|row| row_to_note(&row)).collect())
    }

    /// Delete a note and its associated data.
    pub async fn delete_note(&self, note_id: &str) -> Result<bool> {
        let id = escape_sql(note_id);
        self.db
            .execute(Statement::from_string(
                self.db.get_database_backend(),
                format!(
                    "DELETE FROM note_links WHERE source_note_id = '{}' OR target_note_id = '{}'",
                    id, id
                ),
            ))
            .await?;
        self.db
            .execute(Statement::from_string(
                self.db.get_database_backend(),
                format!("DELETE FROM note_embeddings WHERE note_id = '{}'", id),
            ))
            .await?;
        let result = self
            .db
            .execute(Statement::from_string(
                self.db.get_database_backend(),
                format!("DELETE FROM notes WHERE id = '{}'", id),
            ))
            .await?;
        Ok(result.rows_affected() > 0)
    }

    /// Count total notes.
    pub async fn count_notes(&self) -> Result<usize> {
        let rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT COUNT(*) as cnt FROM notes".to_string(),
            ))
            .await?;
        if let Some(row) = rows.first() {
            if let Ok(cnt) = row.try_get::<i64>("", "cnt") {
                return Ok(cnt as usize);
            }
        }
        Ok(0)
    }

    /// Update links for a note.
    pub async fn upsert_links(
        &self,
        source_note_id: &str,
        target_note_ids: &[String],
    ) -> Result<()> {
        let source = escape_sql(source_note_id);
        self.db
            .execute(Statement::from_string(
                self.db.get_database_backend(),
                format!("DELETE FROM note_links WHERE source_note_id = '{}'", source),
            ))
            .await?;
        for target_id in target_note_ids {
            let target = escape_sql(target_id);
            self.db.execute(Statement::from_string(
                self.db.get_database_backend(),
                format!(
                    "INSERT OR IGNORE INTO note_links (source_note_id, target_note_id) VALUES ('{}', '{}')",
                    source, target
                ),
            )).await?;
        }
        Ok(())
    }

    /// Get outgoing links from a note.
    pub async fn get_outgoing_links(&self, note_id: &str) -> Result<Vec<Note>> {
        let sql = format!(
            "SELECT n.* FROM notes n
             JOIN note_links nl ON n.id = nl.target_note_id
             WHERE nl.source_note_id = '{}'",
            escape_sql(note_id)
        );
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        Ok(rows.into_iter().map(|row| row_to_note(&row)).collect())
    }

    /// Get incoming links to a note.
    #[allow(dead_code)]
    pub async fn get_incoming_links(&self, note_id: &str) -> Result<Vec<Note>> {
        let sql = format!(
            "SELECT n.* FROM notes n
             JOIN note_links nl ON n.id = nl.source_note_id
             WHERE nl.target_note_id = '{}'",
            escape_sql(note_id)
        );
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        Ok(rows.into_iter().map(|row| row_to_note(&row)).collect())
    }

    /// Count total links.
    pub async fn count_links(&self) -> Result<usize> {
        let rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT COUNT(*) as cnt FROM note_links".to_string(),
            ))
            .await?;
        if let Some(row) = rows.first() {
            if let Ok(cnt) = row.try_get::<i64>("", "cnt") {
                return Ok(cnt as usize);
            }
        }
        Ok(0)
    }

    /// Store an embedding for a note.
    pub async fn store_embedding(&self, note_id: &str, embedding: &[f64]) -> Result<()> {
        let embedding_json = serde_json::to_string(embedding)?;
        let sql = format!(
            "INSERT INTO note_embeddings (note_id, embedding, dimensions, created_at)
             VALUES ('{}', '{}', {}, '{}')
             ON CONFLICT(note_id) DO UPDATE SET
                 embedding=excluded.embedding,
                 dimensions=excluded.dimensions,
                 created_at=excluded.created_at",
            escape_sql(note_id),
            embedding_json,
            embedding.len(),
            Utc::now().format("%Y-%m-%dT%H:%M:%SZ"),
        );
        self.db
            .execute(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        Ok(())
    }

    /// Get the embedding for a note.
    pub async fn get_embedding(&self, note_id: &str) -> Result<Option<Vec<f64>>> {
        let sql = format!(
            "SELECT embedding FROM note_embeddings WHERE note_id = '{}'",
            escape_sql(note_id)
        );
        let rows = self
            .db
            .query_all(Statement::from_string(self.db.get_database_backend(), sql))
            .await?;
        if rows.is_empty() {
            return Ok(None);
        }
        let row = &rows[0];
        let embedding_str: String = row.try_get("", "embedding")?;
        let embedding: Vec<f64> = serde_json::from_str(&embedding_str)?;
        Ok(Some(embedding))
    }

    /// Keyword search in title and content.
    pub async fn keyword_search(&self, query: &str, limit: usize) -> Result<Vec<(String, f64)>> {
        if query.trim().is_empty() {
            return Ok(Vec::new());
        }
        let query_lower = query.to_lowercase();
        let terms: Vec<&str> = regex::Regex::new(r"\w[\w-]*")?
            .find_iter(&query_lower)
            .map(|m| m.as_str())
            .collect();
        if terms.is_empty() {
            return Ok(Vec::new());
        }

        let rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT id, title, content FROM notes".to_string(),
            ))
            .await?;

        let mut results: HashMap<String, f64> = HashMap::new();
        for row in &rows {
            let note_id: String = row.try_get("", "id")?;
            let title: String = row.try_get("", "title")?;
            let content: String = row.try_get("", "content")?;
            let title_lower = title.to_lowercase();
            let content_lower = content.to_lowercase();

            let mut score = 0.0;
            for term in &terms {
                let title_count = title_lower.matches(term).count();
                if title_count > 0 {
                    score += title_count as f64 * 10.0;
                }
                if content_lower.contains(term) {
                    let content_count = content_lower.matches(term).count();
                    score += content_count as f64;
                }
                if let Ok(re) = regex::Regex::new(&format!(r"\b{}\b", regex::escape(term))) {
                    let whole_word_count = re.find_iter(&content_lower).count();
                    if whole_word_count > 0 {
                        score += whole_word_count as f64 * 2.0;
                    }
                }
            }
            if score > 0.0 {
                *results.entry(note_id).or_insert(0.0) += score;
            }
        }

        // Normalize scores
        let max_score = results
            .values()
            .cloned()
            .fold(0.0f64, |max, v| if v > max { v } else { max });
        if max_score > 0.0 {
            for v in results.values_mut() {
                *v /= max_score;
            }
        }

        let mut sorted: Vec<(String, f64)> = results.into_iter().collect();
        sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        Ok(sorted.into_iter().take(limit).collect())
    }

    /// Semantic search using cosine similarity.
    pub async fn semantic_search(
        &self,
        query_embedding: &[f64],
        limit: usize,
    ) -> Result<Vec<SearchResult>> {
        let rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT note_id, embedding FROM note_embeddings".to_string(),
            ))
            .await?;

        let mut results: Vec<(String, f64)> = Vec::new();
        for row in &rows {
            let note_id: String = row.try_get("", "note_id")?;
            let embedding_str: String = row.try_get("", "embedding")?;
            let note_embedding: Vec<f64> = match serde_json::from_str(&embedding_str) {
                Ok(e) => e,
                Err(_) => continue,
            };
            let score = cosine_similarity(query_embedding, &note_embedding);
            if score > 0.0 {
                results.push((note_id, score));
            }
        }

        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        let results = results.into_iter().take(limit).collect::<Vec<_>>();

        let mut search_results = Vec::new();
        for (note_id, score) in results {
            if let Some(note) = self.get_note(&note_id).await? {
                let context = if self.get_embedding(&note_id).await?.is_some() {
                    extract_relevant_context(&note.content, 200)
                } else {
                    None
                };
                search_results.push(SearchResult {
                    note,
                    score,
                    context,
                });
            }
        }
        Ok(search_results)
    }

    /// Hybrid search combining semantic and keyword results.
    pub async fn hybrid_search(
        &self,
        query: &str,
        query_embedding: &[f64],
        limit: usize,
        semantic_weight: f64,
        keyword_weight: f64,
    ) -> Result<Vec<SearchResult>> {
        // Semantic results
        let semantic_rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT note_id, embedding FROM note_embeddings".to_string(),
            ))
            .await?;

        let mut semantic_results: HashMap<String, f64> = HashMap::new();
        for row in &semantic_rows {
            let note_id: String = row.try_get("", "note_id")?;
            let embedding_str: String = row.try_get("", "embedding")?;
            let note_embedding: Vec<f64> = match serde_json::from_str(&embedding_str) {
                Ok(e) => e,
                Err(_) => continue,
            };
            let score = cosine_similarity(query_embedding, &note_embedding);
            if score > 0.0 {
                semantic_results.insert(note_id, score);
            }
        }

        // Keyword results
        let keyword_results = self.keyword_search(query, limit * 2).await?;
        let keyword_map: HashMap<String, f64> = keyword_results.into_iter().collect();

        // Merge results
        let all_ids: HashMap<String, ()> = semantic_results
            .keys()
            .chain(keyword_map.keys())
            .map(|k| (k.clone(), ()))
            .collect();

        let mut combined: HashMap<String, f64> = HashMap::new();
        for note_id in all_ids.keys() {
            let sem_score = *semantic_results.get(note_id).unwrap_or(&0.0);
            let kw_score = *keyword_map.get(note_id).unwrap_or(&0.0);
            let combined_score = sem_score * semantic_weight + kw_score * keyword_weight;
            if combined_score > 0.0 {
                combined.insert(note_id.clone(), combined_score);
            }
        }

        let mut sorted: Vec<(String, f64)> = combined.into_iter().collect();
        sorted.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        let sorted = sorted.into_iter().take(limit).collect::<Vec<_>>();

        let mut search_results = Vec::new();
        for (note_id, score) in sorted {
            if let Some(note) = self.get_note(&note_id).await? {
                let context = if self.get_embedding(&note_id).await?.is_some() {
                    extract_relevant_context(&note.content, 200)
                } else {
                    None
                };
                search_results.push(SearchResult {
                    note,
                    score,
                    context,
                });
            }
        }
        Ok(search_results)
    }

    /// Get related notes to a given note.
    pub async fn get_related_notes(
        &self,
        note_id: &str,
        limit: usize,
    ) -> Result<Vec<SearchResult>> {
        let embedding = match self.get_embedding(note_id).await? {
            Some(e) => e,
            None => return Ok(Vec::new()),
        };
        let results = self.semantic_search(&embedding, limit + 1).await?;
        Ok(results
            .into_iter()
            .filter(|r| r.note.id != note_id)
            .take(limit)
            .collect())
    }

    /// Get knowledge graph statistics.
    pub async fn get_stats(&self) -> Result<serde_json::Value> {
        let note_count = self.count_notes().await?;
        let link_count = self.count_links().await?;

        let rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT MAX(updated_at) as last_updated FROM notes".to_string(),
            ))
            .await?;
        let last_updated = rows
            .first()
            .and_then(|r| r.try_get::<String>("", "last_updated").ok());

        let emb_rows = self
            .db
            .query_all(Statement::from_string(
                self.db.get_database_backend(),
                "SELECT COUNT(*) as cnt FROM note_embeddings".to_string(),
            ))
            .await?;
        let embedded_count = emb_rows
            .first()
            .and_then(|r| r.try_get::<i64>("", "cnt").ok())
            .unwrap_or(0) as usize;

        Ok(serde_json::json!({
            "total_notes": note_count,
            "total_links": link_count,
            "embedded_notes": embedded_count,
            "last_updated": last_updated,
        }))
    }
}

fn escape_sql(s: &str) -> String {
    s.replace('\'', "''")
}

fn row_to_note(row: &QueryResult) -> Note {
    let id: String = row.try_get("", "id").unwrap_or_default();
    let file_path: String = row.try_get("", "file_path").unwrap_or_default();
    let title: String = row.try_get("", "title").unwrap_or_default();
    let content: String = row.try_get("", "content").unwrap_or_default();
    let links_str: String = row
        .try_get("", "links")
        .unwrap_or_else(|_| "[]".to_string());
    let links: Vec<String> = serde_json::from_str(&links_str).unwrap_or_default();
    let created_at_str: String = row.try_get("", "created_at").unwrap_or_default();
    let updated_at_str: String = row.try_get("", "updated_at").unwrap_or_default();

    let created_at = chrono::DateTime::parse_from_rfc3339(&created_at_str)
        .ok()
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or(Utc::now());
    let updated_at = chrono::DateTime::parse_from_rfc3339(&updated_at_str)
        .ok()
        .map(|dt| dt.with_timezone(&Utc))
        .unwrap_or(Utc::now());

    Note {
        id,
        file_path,
        title,
        content,
        links,
        created_at,
        updated_at,
    }
}
