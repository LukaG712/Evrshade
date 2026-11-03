//! LLM provider implementations for Shrewd.
//!
//! Each provider handles authentication, request formatting, and response
//! parsing for a specific LLM API using reqwest for async HTTP calls.

use anyhow::{Result, bail};
use reqwest::{Client, header};
use serde_json::Value;
use tracing::warn;

use crate::models::{ChatMessage, ChatResponse, Provider};

/// Timeout for LLM API requests in seconds.
const DEFAULT_TIMEOUT_SECS: u64 = 60;

/// Abstract base trait for LLM providers.
#[async_trait::async_trait]
pub trait LlmProvider: Send + Sync {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse>;

    fn check_available(&self) -> bool;
}

fn get_timeout() -> u64 {
    std::env::var("SHREWD_REQUEST_TIMEOUT")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(DEFAULT_TIMEOUT_SECS)
}

fn create_client() -> Client {
    Client::builder()
        .timeout(std::time::Duration::from_secs(get_timeout()))
        .build()
        .unwrap_or_else(|_| Client::new())
}

// ─── OpenAI Provider ───────────────────────────────────────────

pub struct OpenAIProvider {
    api_key: String,
    base_url: String,
    client: Client,
}

impl OpenAIProvider {
    pub fn new() -> Self {
        Self {
            api_key: std::env::var("OPENAI_API_KEY").unwrap_or_default(),
            base_url: std::env::var("OPENAI_BASE_URL")
                .unwrap_or_else(|_| "https://api.openai.com/v1".to_string()),
            client: create_client(),
        }
    }
}

#[async_trait::async_trait]
impl LlmProvider for OpenAIProvider {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse> {
        let url = format!("{}/chat/completions", self.base_url);
        let payload = serde_json::json!({
            "model": model,
            "messages": messages.iter().map(|m| {
                serde_json::json!({"role": m.role, "content": m.content})
            }).collect::<Vec<_>>(),
            "temperature": temperature,
            "max_tokens": max_tokens,
        });

        let mut headers = header::HeaderMap::new();
        headers.insert(
            "Authorization",
            format!("Bearer {}", self.api_key).parse().unwrap(),
        );
        headers.insert("Content-Type", "application/json".parse().unwrap());

        let resp = self.client.post(&url).headers(headers).json(&payload).send().await?;
        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            bail!("OpenAI API error {}: {}", status, body);
        }

        let data: Value = resp.json().await?;
        let choice = &data["choices"][0];
        let usage = &data["usage"];
        let content = choice["message"]["content"].as_str().unwrap_or("").to_string();
        let prompt_tokens = usage["prompt_tokens"].as_u64().unwrap_or(0) as usize;
        let completion_tokens = usage["completion_tokens"].as_u64().unwrap_or(0) as usize;

        Ok(ChatResponse::new(
            content,
            Provider::OpenAI,
            model.to_string(),
            prompt_tokens,
            completion_tokens,
        ))
    }

    fn check_available(&self) -> bool {
        !self.api_key.is_empty()
    }
}

// ─── Anthropic Provider ────────────────────────────────────────

pub struct AnthropicProvider {
    api_key: String,
    base_url: String,
    client: Client,
}

impl AnthropicProvider {
    pub fn new() -> Self {
        Self {
            api_key: std::env::var("ANTHROPIC_API_KEY").unwrap_or_default(),
            base_url: std::env::var("ANTHROPIC_BASE_URL")
                .unwrap_or_else(|_| "https://api.anthropic.com/v1".to_string()),
            client: create_client(),
        }
    }
}

#[async_trait::async_trait]
impl LlmProvider for AnthropicProvider {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse> {
        let url = format!("{}/messages", self.base_url);

        let mut system_msg: Option<String> = None;
        let mut other_messages = Vec::new();
        for m in messages {
            if m.role == "system" {
                system_msg = Some(m.content.clone());
            } else {
                other_messages.push(serde_json::json!({
                    "role": m.role,
                    "content": m.content,
                }));
            }
        }

        let mut payload = serde_json::json!({
            "model": model,
            "messages": other_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        });
        if let Some(sys) = system_msg {
            payload["system"] = serde_json::json!(sys);
        }

        let mut headers = header::HeaderMap::new();
        headers.insert("x-api-key", self.api_key.parse().unwrap());
        headers.insert("anthropic-version", "2023-06-01".parse().unwrap());
        headers.insert("Content-Type", "application/json".parse().unwrap());

        let resp = self.client.post(&url).headers(headers).json(&payload).send().await?;
        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            bail!("Anthropic API error {}: {}", status, body);
        }

        let data: Value = resp.json().await?;
        let usage = &data["usage"];
        let content_blocks = &data["content"];
        let mut content_text = String::new();
        if let Some(blocks) = content_blocks.as_array() {
            for block in blocks {
                if block.get("type").and_then(|v| v.as_str()) == Some("text") {
                    if let Some(text) = block.get("text").and_then(|v| v.as_str()) {
                        content_text.push_str(text);
                    }
                }
            }
        }

        let prompt_tokens = usage["input_tokens"].as_u64().unwrap_or(0) as usize;
        let completion_tokens = usage["output_tokens"].as_u64().unwrap_or(0) as usize;

        Ok(ChatResponse::new(
            content_text,
            Provider::Anthropic,
            model.to_string(),
            prompt_tokens,
            completion_tokens,
        ))
    }

    fn check_available(&self) -> bool {
        !self.api_key.is_empty()
    }
}

// ─── Google Provider ───────────────────────────────────────────

pub struct GoogleProvider {
    api_key: String,
    base_url: String,
    client: Client,
}

impl GoogleProvider {
    pub fn new() -> Self {
        Self {
            api_key: std::env::var("GOOGLE_API_KEY").unwrap_or_default(),
            base_url: std::env::var("GOOGLE_BASE_URL")
                .unwrap_or_else(|_| "https://generativelanguage.googleapis.com/v1beta".to_string()),
            client: create_client(),
        }
    }
}

#[async_trait::async_trait]
impl LlmProvider for GoogleProvider {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse> {
        let url = format!("{}/models/{}:generateContent?key={}", self.base_url, model, self.api_key);

        let mut system_msg: Option<String> = None;
        let mut other_messages = Vec::new();
        for m in messages {
            if m.role == "system" {
                system_msg = Some(m.content.clone());
            } else {
                let role = if m.role == "user" { "user" } else { "model" };
                other_messages.push(serde_json::json!({
                    "role": role,
                    "parts": [{"text": m.content}],
                }));
            }
        }

        let mut payload = serde_json::json!({
            "contents": other_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        });
        if let Some(sys) = system_msg {
            payload["systemInstruction"] = serde_json::json!({"parts": [{"text": sys}]});
        }

        let resp = self.client.post(&url).json(&payload).send().await?;
        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            bail!("Google API error {}: {}", status, body);
        }

        let data: Value = resp.json().await?;
        let mut content_text = String::new();
        if let Some(candidates) = data["candidates"].as_array() {
            if let Some(first) = candidates.first() {
                if let Some(parts) = first["content"]["parts"].as_array() {
                    for part in parts {
                        if let Some(text) = part.get("text").and_then(|v| v.as_str()) {
                            content_text.push_str(text);
                        }
                    }
                }
            }
        }

        let usage = &data["usageMetadata"];
        let prompt_tokens = usage["promptTokenCount"].as_u64().unwrap_or(0) as usize;
        let completion_tokens = usage["candidatesTokenCount"].as_u64().unwrap_or(0) as usize;

        Ok(ChatResponse::new(
            content_text,
            Provider::Google,
            model.to_string(),
            prompt_tokens,
            completion_tokens,
        ))
    }

    fn check_available(&self) -> bool {
        !self.api_key.is_empty()
    }
}

// ─── Ollama Provider ───────────────────────────────────────────

pub struct OllamaProvider {
    base_url: String,
    client: Client,
}

impl OllamaProvider {
    pub fn new() -> Self {
        Self {
            base_url: std::env::var("OLLAMA_BASE_URL")
                .unwrap_or_else(|_| "http://localhost:11434".to_string()),
            client: create_client(),
        }
    }
}

#[async_trait::async_trait]
impl LlmProvider for OllamaProvider {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse> {
        let url = format!("{}/api/chat", self.base_url);
        let payload = serde_json::json!({
            "model": model,
            "messages": messages.iter().map(|m| {
                serde_json::json!({"role": m.role, "content": m.content})
            }).collect::<Vec<_>>(),
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": false,
        });

        let resp = self.client.post(&url).json(&payload).send().await?;
        if !resp.status().is_success() {
            let status = resp.status();
            let body = resp.text().await.unwrap_or_default();
            bail!("Ollama API error {}: {}", status, body);
        }

        let data: Value = resp.json().await?;
        let content = data["message"]["content"].as_str().unwrap_or("").to_string();
        let prompt_tokens = data["prompt_eval_count"].as_u64().unwrap_or(0) as usize;
        let completion_tokens = data["eval_count"].as_u64().unwrap_or(0) as usize;

        Ok(ChatResponse::new(
            content,
            Provider::Ollama,
            model.to_string(),
            prompt_tokens,
            completion_tokens,
        ))
    }

    fn check_available(&self) -> bool {
        // Ollama is always "available" if the URL is set; real check happens on first call
        true
    }
}

// ─── Provider Factory ──────────────────────────────────────────

use std::sync::Arc;

#[async_trait::async_trait]
impl LlmProvider for Arc<dyn LlmProvider> {
    async fn chat(
        &self,
        messages: &[ChatMessage],
        model: &str,
        temperature: f64,
        max_tokens: usize,
    ) -> Result<ChatResponse> {
        self.as_ref().chat(messages, model, temperature, max_tokens).await
    }

    fn check_available(&self) -> bool {
        self.as_ref().check_available()
    }
}

/// Returns a boxed provider instance for the given provider type.
pub fn get_provider(provider: Provider) -> Box<dyn LlmProvider> {
    match provider {
        Provider::OpenAI => Box::new(OpenAIProvider::new()),
        Provider::Anthropic => Box::new(AnthropicProvider::new()),
        Provider::Google => Box::new(GoogleProvider::new()),
        Provider::Ollama => Box::new(OllamaProvider::new()),
    }
}
