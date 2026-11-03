//! Data models for the Knowledge Graph module in Gobber.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Represents a single Obsidian note in the knowledge graph.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Note {
    pub id: String,
    pub file_path: String,
    pub title: String,
    pub content: String,
    pub links: Vec<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Note {
    pub fn new(file_path: String, title: String, content: String, links: Vec<String>) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4().to_string(),
            file_path,
            title,
            content,
            links,
            created_at: now,
            updated_at: now,
        }
    }

    pub fn with_id(
        id: String,
        file_path: String,
        title: String,
        content: String,
        links: Vec<String>,
        created_at: DateTime<Utc>,
    ) -> Self {
        Self {
            id,
            file_path,
            title,
            content,
            links,
            created_at,
            updated_at: Utc::now(),
        }
    }
}

/// Represents a note found by semantic search.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub note: Note,
    pub score: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub context: Option<String>,
}
