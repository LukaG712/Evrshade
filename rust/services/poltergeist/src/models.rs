//! Data models for Poltergeist notification service.

use serde::{Deserialize, Serialize};

/// Notification record.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Notification {
    pub id: String,
    pub channel: String,
    pub recipient: String,
    pub title: String,
    pub body: String,
    pub status: String,
    pub error: Option<String>,
    pub created_at: String,
    pub sent_at: Option<String>,
}
