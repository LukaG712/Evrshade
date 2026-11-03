//! Core knowledge graph logic: vault scanning, embedding generation, and index management.

use anyhow::Result;
use regex::Regex;
use reqwest::Client;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::path::Path;
use tokio::fs;
use tracing::{error, info, warn};

use crate::models::{Note, SearchResult};
use crate::storage::KnowledgeGraphStorage;

lazy_static::lazy_static! {
    static ref LINK_PATTERN: Regex = Regex::new(r"\[\[([^\]]+)\]\]").unwrap();
    static ref FRONTMATTER_PATTERN: Regex = Regex::new(r"^---\s*\n(.*?)\n---\s*\n").unwrap();
}

/// Knowledge graph manager.
pub struct KnowledgeGraph {
    pub vault_path: String,
    pub shrewd_url: String,
    pub shrewd_api_key: String,
    pub embedding_model: String,
    pub storage: KnowledgeGraphStorage,
    pub http_client: Client,
}

impl KnowledgeGraph {
    pub fn new(
        vault_path: Option<String>,
        shrewd_url: Option<String>,
        shrewd_api_key: Option<String>,
        embedding_model: Option<String>,
        storage: KnowledgeGraphStorage,
    ) -> Self {
        Self {
            vault_path: vault_path
                .or_else(|| std::env::var("OBSIDIAN_VAULT_PATH").ok())
                .unwrap_or_default(),
            shrewd_url: shrewd_url
                .or_else(|| std::env::var("SHREWD_URL").ok())
                .unwrap_or_else(|| "http://localhost:8089".to_string()),
            shrewd_api_key: shrewd_api_key
                .or_else(|| std::env::var("SHREWD_API_KEY").ok())
                .unwrap_or_default(),
            embedding_model: embedding_model
                .or_else(|| std::env::var("EMBEDDING_MODEL").ok())
                .unwrap_or_else(|| "nomic-embed-text".to_string()),
            storage,
            http_client: Client::builder()
                .timeout(std::time::Duration::from_secs(60))
                .build()
                .unwrap_or_else(|_| Client::new()),
        }
    }

    /// Scan the Obsidian vault directory for .md files and parse them.
    pub async fn scan_vault(&self) -> Result<Vec<Note>> {
        let vault_path = Path::new(&self.vault_path);
        if !vault_path.exists() {
            warn!("Vault path does not exist: {}", self.vault_path);
            return Ok(Vec::new());
        }

        let mut notes = Vec::new();
        let mut md_files = Vec::new();
        self.collect_md_files(vault_path, &mut md_files).await?;

        for md_file in &md_files {
            match self.parse_note(md_file).await {
                Ok(note) => notes.push(note),
                Err(e) => error!("Failed to parse {:?}: {}", md_file, e),
            }
        }

        info!(
            "Scanned {} notes from {} .md files",
            notes.len(),
            md_files.len()
        );
        Ok(notes)
    }

    async fn collect_md_files(
        &self,
        dir: &Path,
        files: &mut Vec<std::path::PathBuf>,
    ) -> Result<()> {
        let mut entries = fs::read_dir(dir).await?;
        while let Some(entry) = entries.next_entry().await? {
            let path = entry.path();
            if path.is_dir() {
                Box::pin(self.collect_md_files(&path, files)).await?;
            } else if path.extension().and_then(|s| s.to_str()) == Some("md") {
                files.push(path);
            }
        }
        Ok(())
    }

    /// Parse a single markdown file into a Note object.
    async fn parse_note(&self, file_path: &std::path::Path) -> Result<Note> {
        let content = fs::read_to_string(file_path).await?;
        let vault_path = Path::new(&self.vault_path);
        let relative_path = file_path
            .strip_prefix(vault_path)
            .unwrap_or(file_path)
            .to_string_lossy()
            .to_string();

        // Extract frontmatter title
        let mut title = file_path
            .file_stem()
            .map(|s| s.to_string_lossy().to_string())
            .unwrap_or_default();

        if let Some(captures) = FRONTMATTER_PATTERN.captures(&content) {
            if let Some(frontmatter) = captures.get(1) {
                for line in frontmatter.as_str().lines() {
                    if let Some(after_colon) = line.strip_prefix("title:") {
                        title = after_colon
                            .trim()
                            .trim_matches('"')
                            .trim_matches('\'')
                            .to_string();
                        break;
                    }
                }
            }
        }

        // Extract [[links]]
        let links: Vec<String> = LINK_PATTERN
            .captures_iter(&content)
            .filter_map(|c| c.get(1))
            .map(|m| m.as_str().to_string())
            .collect();

        // Remove frontmatter from content
        let clean_content = FRONTMATTER_PATTERN.replace(&content, "").trim().to_string();

        // Check if note already exists
        let existing = self.storage.get_note_by_path(&relative_path).await?;

        if let Some(existing) = existing {
            Ok(Note::with_id(
                existing.id,
                relative_path,
                title,
                clean_content,
                links,
                existing.created_at,
            ))
        } else {
            Ok(Note::new(relative_path, title, clean_content, links))
        }
    }

    /// Generate an embedding vector for the given text using Shrewd service.
    pub async fn generate_embedding(&self, text: &str) -> Result<Option<Vec<f64>>> {
        if text.trim().is_empty() {
            return Ok(None);
        }

        let mut headers = reqwest::header::HeaderMap::new();
        if !self.shrewd_api_key.is_empty() {
            if let Ok(val) = self.shrewd_api_key.parse() {
                headers.insert("X-API-Key", val);
            }
        }

        let url = format!("{}/api/embed", self.shrewd_url);
        let payload = serde_json::json!({
            "text": &text[..text.char_indices().take(8000).map(|(i, _)| i).last().unwrap_or(0)],
            "model": self.embedding_model,
        });

        match self
            .http_client
            .post(&url)
            .headers(headers)
            .json(&payload)
            .send()
            .await
        {
            Ok(resp) if resp.status().is_success() => {
                let data: serde_json::Value = resp.json().await?;
                let embedding = data
                    .get("embedding")
                    .or_else(|| data.get("vector"))
                    .and_then(|v| v.as_array())
                    .map(|arr| arr.iter().filter_map(|v| v.as_f64()).collect::<Vec<f64>>());
                Ok(embedding)
            }
            Ok(resp) => {
                warn!(
                    "Shrewd embedding failed: {} {}",
                    resp.status(),
                    resp.text().await.unwrap_or_default()
                );
                Ok(None)
            }
            Err(e) => {
                warn!("Failed to generate embedding via Shrewd: {}", e);
                Ok(None)
            }
        }
    }

    /// Generate a simple hash-based fallback embedding.
    pub fn generate_fallback_embedding(&self, text: &str, dimensions: usize) -> Vec<f64> {
        let text_lower = text.to_lowercase();
        let words: Vec<&str> = text_lower.split_whitespace().collect();
        let mut embedding = vec![0.0f64; dimensions];

        for word in &words {
            let mut hasher = std::collections::hash_map::DefaultHasher::default();
            Hash::hash(word, &mut hasher);
            let hash_value = Hasher::finish(&hasher);
            let hash_bytes = hash_value.to_le_bytes();
            for i in 0..dimensions {
                embedding[i] += (hash_bytes[i % hash_bytes.len()] as f64) / 255.0 - 0.5;
            }
        }

        // Normalize
        let magnitude: f64 = embedding.iter().map(|x| x * x).sum::<f64>().sqrt();
        if magnitude > 0.0 {
            for x in &mut embedding {
                *x /= magnitude;
            }
        }

        embedding
    }

    /// Index the entire vault.
    pub async fn index_vault(&self) -> Result<serde_json::Value> {
        if !Path::new(&self.vault_path).exists() {
            return Ok(serde_json::json!({
                "success": false,
                "error": format!("Vault path does not exist: {}", self.vault_path),
            }));
        }

        let mut notes_indexed: i64 = 0;
        let mut embeddings_generated: i64 = 0;
        let mut links_resolved: i64 = 0;
        let mut errors: i64 = 0;

        let notes = self.scan_vault().await?;
        if notes.is_empty() {
            return Ok(
                serde_json::json!({ "success": true, "notes_indexed": 0, "embeddings_generated": 0, "links_resolved": 0, "errors": 0 }),
            );
        }

        // Build title map for link resolution
        let mut title_map: HashMap<String, String> = HashMap::new();
        for note in &notes {
            title_map.insert(note.title.to_lowercase(), note.id.clone());
            let stem = note.file_path.replace(".md", "").to_lowercase();
            title_map.insert(stem, note.id.clone());
        }

        // Store each note and resolve links
        for note in &notes {
            match self.storage.upsert_note(note).await {
                Ok(()) => {
                    notes_indexed += 1;
                }
                Err(e) => {
                    error!("Failed to index note {}: {}", note.title, e);
                    errors += 1;
                    continue;
                }
            }

            // Resolve links
            let resolved_links: Vec<String> = note
                .links
                .iter()
                .filter_map(|link_title| {
                    let actual_title = link_title
                        .split('|')
                        .next()
                        .unwrap_or(link_title)
                        .trim()
                        .to_lowercase();
                    title_map.get(&actual_title).cloned()
                })
                .collect();

            if !resolved_links.is_empty() {
                if let Err(e) = self.storage.upsert_links(&note.id, &resolved_links).await {
                    error!("Failed to resolve links for {}: {}", note.title, e);
                } else {
                    links_resolved += resolved_links.len() as i64;
                }
            }
        }

        // Generate embeddings
        for note in &notes {
            let embedding = match self.generate_embedding(&note.content).await {
                Ok(Some(e)) => e,
                _ => {
                    info!("Using fallback embedding for {}", note.title);
                    self.generate_fallback_embedding(&note.content, 384)
                }
            };

            if let Err(e) = self.storage.store_embedding(&note.id, &embedding).await {
                error!("Failed to store embedding for {}: {}", note.title, e);
            } else {
                embeddings_generated += 1;
            }
        }

        Ok(
            serde_json::json!({ "success": true, "notes_indexed": notes_indexed, "embeddings_generated": embeddings_generated, "links_resolved": links_resolved, "errors": errors }),
        )
    }

    /// Search notes using hybrid semantic + keyword matching.
    pub async fn search(&self, query: &str, limit: usize) -> Result<Vec<SearchResult>> {
        let query_embedding = match self.generate_embedding(query).await {
            Ok(Some(e)) => e,
            _ => self.generate_fallback_embedding(query, 384),
        };

        self.storage
            .hybrid_search(query, &query_embedding, limit, 0.7, 0.3)
            .await
    }

    /// Get a note by ID.
    pub async fn get_note(&self, note_id: &str) -> Result<Option<Note>> {
        self.storage.get_note(note_id).await
    }

    /// List all indexed notes.
    pub async fn list_notes(&self, limit: usize, offset: usize) -> Result<Vec<Note>> {
        self.storage.list_notes(limit, offset).await
    }

    /// Get outgoing links from a note.
    pub async fn get_note_links(&self, note_id: &str) -> Result<Vec<Note>> {
        self.storage.get_outgoing_links(note_id).await
    }

    /// Get semantically related notes.
    pub async fn get_related_notes(
        &self,
        note_id: &str,
        limit: usize,
    ) -> Result<Vec<SearchResult>> {
        self.storage.get_related_notes(note_id, limit).await
    }

    /// Delete a note from the index.
    pub async fn delete_note(&self, note_id: &str) -> Result<bool> {
        self.storage.delete_note(note_id).await
    }

    /// Get knowledge graph statistics.
    pub async fn get_stats(&self) -> Result<serde_json::Value> {
        let mut stats = self.storage.get_stats().await?;
        if let Some(stats_obj) = stats.as_object_mut() {
            stats_obj.insert(
                "vault_path".to_string(),
                serde_json::Value::String(self.vault_path.clone()),
            );
            stats_obj.insert(
                "vault_exists".to_string(),
                serde_json::Value::Bool(Path::new(&self.vault_path).exists()),
            );
        }
        Ok(stats)
    }
}
