//! Shrewd — LLM provider abstraction service.
//!
//! Routes chat requests to real LLM providers (OpenAI, Anthropic, Google, Ollama)
//! with cost tracking and privacy classification.

use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::Deserialize;
use tracing::{info, warn};

mod models;
mod providers;
mod routing;

use models::{ChatRequest, ChatResponse, Provider};
use routing::{get_cost_summary, list_models, list_providers, route_chat};

/// Application state.
#[derive(Clone)]
struct AppState {
    api_key: String,
}

/// Query params for /api/models.
#[derive(Deserialize)]
struct ListModelsQuery {
    #[serde(default)]
    provider: Option<String>,
}

/// Verify Bearer token in Authorization header.
fn verify_bearer(auth_header: Option<&str>, api_key: &str) -> Result<(), (StatusCode, String)> {
    let auth = auth_header.ok_or_else(|| {
        (
            StatusCode::UNAUTHORIZED,
            "Missing or invalid Authorization header. Use: Authorization: Bearer <key>".to_string(),
        )
    })?;

    let token = auth.strip_prefix("Bearer ").ok_or_else(|| {
        (
            StatusCode::UNAUTHORIZED,
            "Missing or invalid Authorization header. Use: Authorization: Bearer <key>".to_string(),
        )
    })?;

    // Constant-time comparison
    if !constant_time_eq(token, api_key) {
        return Err((StatusCode::UNAUTHORIZED, "Invalid API key".to_string()));
    }

    Ok(())
}

fn constant_time_eq(a: &str, b: &str) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut result: u8 = 0;
    for (x, y) in a.bytes().zip(b.bytes()) {
        result |= x ^ y;
    }
    result == 0
}

/// Auth middleware.
async fn auth_middleware(
    state: State<AppState>,
    req: axum::http::Request<axum::body::Body>,
    next: axum::middleware::Next,
) -> axum::response::Response {
    let path = req.uri().path().to_string();
    let public_paths = [
        "/health",
        "/ready",
        "/metrics",
        "/api/status",
        "/docs",
        "/openapi.json",
    ];
    if public_paths.contains(&path.as_str()) {
        return next.run(req).await;
    }

    let auth_header = req
        .headers()
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string());

    if let Err((status, msg)) = verify_bearer(auth_header.as_deref(), &state.api_key) {
        return (status, Json(serde_json::json!({"detail": msg}))).into_response();
    }

    next.run(req).await
}

// ─── Handlers ──────────────────────────────────────────────────

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "Shrewd"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Shrewd"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Shrewd",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP shrewd_uptime_seconds Service uptime in seconds.\n\
     # TYPE shrewd_uptime_seconds gauge\n\
     shrewd_uptime_seconds 0.0\n\
     # HELP shrewd_ready Service readiness.\n\
     # TYPE shrewd_ready gauge\n\
     shrewd_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Shrewd",
        "version": "2.0.0",
        "features": [
            "llm_routing",
            "cost_tracking",
            "privacy_classification",
            "openai",
            "anthropic",
            "google",
            "ollama",
            "prometheus_metrics",
            "opentelemetry",
        ],
    }))
}

async fn chat_handler(
    State(state): State<AppState>,
    Json(request): Json<ChatRequest>,
) -> impl IntoResponse {
    let _ = state; // auth already checked by middleware

    let model = request.model.as_deref();
    let temperature = request.temperature;
    let max_tokens = request.max_tokens;
    let require_private = request.require_private;

    match route_chat(
        &request.messages,
        model,
        temperature,
        max_tokens,
        require_private,
    )
    .await
    {
        Ok(response) => (StatusCode::OK, Json(response)).into_response(),
        Err(e) => {
            warn!("Provider error, falling back to simulation: {}", e);
            // Fallback response
            let fallback = ChatResponse::new(
                "[Simulated response] Provider unavailable. Please check configuration.".to_string(),
                Provider::Ollama,
                model.unwrap_or("llama3").to_string(),
                0,
                20,
            );
            (StatusCode::SERVICE_UNAVAILABLE, Json(fallback)).into_response()
        }
    }
}

async fn list_models_handler(Query(query): Query<ListModelsQuery>) -> Json<Vec<serde_json::Value>> {
    let provider_filter = query
        .provider
        .as_deref()
        .and_then(|p| match p.to_lowercase().as_str() {
            "openai" => Some(Provider::OpenAI),
            "anthropic" => Some(Provider::Anthropic),
            "google" => Some(Provider::Google),
            "ollama" => Some(Provider::Ollama),
            _ => None,
        });

    let models = list_models(provider_filter);
    let result: Vec<serde_json::Value> = models
        .into_iter()
        .map(|m| {
            serde_json::json!({
                "name": m.name,
                "provider": m.provider.as_str(),
                "context_window": m.context_window,
                "is_private": m.is_private,
                "is_available": m.is_available,
            })
        })
        .collect();

    Json(result)
}

async fn list_providers_handler() -> Json<Vec<serde_json::Value>> {
    let providers = list_providers();
    let result: Vec<serde_json::Value> = providers
        .into_iter()
        .map(|(p, available)| {
            serde_json::json!({
                "name": p.as_str(),
                "is_available": available,
            })
        })
        .collect();

    Json(result)
}

async fn cost_summary_handler() -> Json<serde_json::Value> {
    let summary = get_cost_summary();
    Json(serde_json::to_value(summary).unwrap_or_default())
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Shrewd without a configured API key.");
        std::process::exit(1);
    }

    let state = AppState { api_key };

    let app = Router::new()
        // Health endpoints (public)
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        // Capabilities
        .route("/api/capabilities", get(capabilities_handler))
        // Chat endpoint
        .route("/api/chat", post(chat_handler))
        // Models & providers
        .route("/api/models", get(list_models_handler))
        .route("/api/providers", get(list_providers_handler))
        // Cost tracking
        .route("/api/cost/summary", get(cost_summary_handler))
        .with_state(state.clone())
        .layer(axum::middleware::from_fn_with_state(
            state.clone(),
            auth_middleware,
        ));

    let addr = "0.0.0.0:8089";
    info!("Shrewd listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
