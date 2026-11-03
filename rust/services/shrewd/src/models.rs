//! Data models for Shrewd LLM abstraction service.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::fmt;
use uuid::Uuid;

/// LLM provider enum.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Provider {
    OpenAI,
    Anthropic,
    Google,
    Ollama,
}

impl Provider {
    pub fn as_str(&self) -> &'static str {
        match self {
            Provider::OpenAI => "openai",
            Provider::Anthropic => "anthropic",
            Provider::Google => "google",
            Provider::Ollama => "ollama",
        }
    }
}

impl fmt::Display for Provider {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// A single chat message.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

/// Chat completion request.
#[derive(Debug, Clone, Deserialize)]
pub struct ChatRequest {
    #[serde(default)]
    pub messages: Vec<ChatMessage>,
    pub model: Option<String>,
    pub provider: Option<Provider>,
    #[serde(default = "default_temperature")]
    pub temperature: f64,
    #[serde(default = "default_max_tokens")]
    pub max_tokens: usize,
    #[serde(default)]
    pub require_private: bool,
}

fn default_temperature() -> f64 {
    0.7
}

fn default_max_tokens() -> usize {
    1000
}

/// Chat completion response.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatResponse {
    pub id: String,
    pub content: String,
    pub provider: Provider,
    pub model: String,
    pub prompt_tokens: usize,
    pub completion_tokens: usize,
    pub cost_usd: f64,
    pub created_at: DateTime<Utc>,
}

impl ChatResponse {
    pub fn new(
        content: String,
        provider: Provider,
        model: String,
        prompt_tokens: usize,
        completion_tokens: usize,
    ) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            content,
            provider,
            model,
            prompt_tokens,
            completion_tokens,
            cost_usd: 0.0,
            created_at: Utc::now(),
        }
    }
}

/// Model metadata.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInfo {
    pub name: String,
    pub provider: Provider,
    pub context_window: usize,
    pub is_private: bool,
    pub is_available: bool,
}

/// Cost tracking entry.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostEntry {
    pub timestamp: DateTime<Utc>,
    pub model: String,
    pub provider: String,
    pub prompt_tokens: usize,
    pub completion_tokens: usize,
    pub total_tokens: usize,
    pub cost_usd: f64,
}

/// Cost summary response.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CostSummary {
    pub total_cost_usd: f64,
    pub total_tokens: usize,
    pub requests: usize,
    #[serde(rename = "by_provider")]
    pub by_provider: std::collections::HashMap<String, ProviderCost>,
    #[serde(rename = "by_model")]
    pub by_model: std::collections::HashMap<String, ModelCost>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProviderCost {
    pub cost_usd: f64,
    pub tokens: usize,
    pub requests: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelCost {
    pub cost_usd: f64,
    pub tokens: usize,
    pub requests: usize,
}
