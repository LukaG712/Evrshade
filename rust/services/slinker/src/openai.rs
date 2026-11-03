//! OpenAI-compatible routes for Slinker — delegates to Shrewd service.

use axum::{extract::State, http::StatusCode, response::Response, Json};
use serde::Deserialize;

use crate::{adapters::gen_id, AppState};

#[derive(Deserialize)]
pub struct ChatCompletionRequest {
    #[serde(default = "default_model")]
    pub model: String,
    pub messages: Vec<ChatMessage>,
    #[serde(default = "default_temperature")]
    pub temperature: f64,
    #[serde(default)]
    pub max_tokens: Option<usize>,
    #[serde(default)]
    pub stream: bool,
}

fn default_model() -> String {
    "gpt-4".to_string()
}
fn default_temperature() -> f64 {
    0.7
}

#[derive(Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

/// List available models.
pub async fn list_models_handler() -> Json<serde_json::Value> {
    let models = vec![
        serde_json::json!({"id": "gpt-4", "object": "model", "created": chrono::Utc::now().timestamp(), "owned_by": "slinker"}),
        serde_json::json!({"id": "gpt-3.5-turbo", "object": "model", "created": chrono::Utc::now().timestamp(), "owned_by": "slinker"}),
        serde_json::json!({"id": "slinker-agent", "object": "model", "created": chrono::Utc::now().timestamp(), "owned_by": "slinker"}),
    ];
    Json(serde_json::json!({"object": "list", "data": models}))
}

/// Handle chat completions — delegates to Shrewd service.
pub async fn chat_completions(
    State(_state): State<AppState>,
    Json(request): Json<ChatCompletionRequest>,
) -> Result<Response, StatusCode> {
    let shrewd_url = std::env::var("SHREWD_URL").unwrap_or_default();

    if shrewd_url.is_empty() {
        let completion_id = format!("chatcmpl-{}", gen_id().chars().take(12).collect::<String>());
        let response = serde_json::json!({
            "id": completion_id,
            "object": "chat.completion",
            "created": chrono::Utc::now().timestamp(),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Shrewd service is not configured. Set SHREWD_URL to enable LLM routing."},
                "finish_reason": "stop",
            }],
        });
        return Ok(Json(response).into_response());
    }

    if request.stream {
        let completion_id = format!("chatcmpl-{}", gen_id().chars().take(12).collect::<String>());
        let response = serde_json::json!({
            "id": completion_id,
            "object": "chat.completion",
            "created": chrono::Utc::now().timestamp(),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Streaming not yet supported in Rust version"},
                "finish_reason": "stop",
            }],
        });
        return Ok(Json(response).into_response());
    }

    let client = match reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(120))
        .build()
    {
        Ok(c) => c,
        Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
    };

    let shrewd_api_key = std::env::var("API_KEY").unwrap_or_default();
    let mut req_builder = client
        .post(format!("{}/v1/chat/completions", shrewd_url))
        .json(&request);

    if !shrewd_api_key.is_empty() {
        req_builder = req_builder.bearer(&shrewd_api_key);
    }

    match req_builder.send().await {
        Ok(resp) if resp.status().is_success() => match resp.json::<serde_json::Value>().await {
            Ok(data) => Ok(Json(data).into_response()),
            Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
        },
        Ok(_) => Err(StatusCode::BAD_GATEWAY),
        Err(e) => {
            tracing::error!("Chat completion error: {}", e);
            let completion_id =
                format!("chatcmpl-{}", gen_id().chars().take(12).collect::<String>());
            let response = serde_json::json!({
                "id": completion_id,
                "object": "chat.completion",
                "created": chrono::Utc::now().timestamp(),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "Provider error"},
                    "finish_reason": "error",
                }],
            });
            Ok(Json(response).into_response())
        }
    }
}
