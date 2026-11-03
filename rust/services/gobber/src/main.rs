//! Gobber — Knowledge graph service.
//!
//! Provides knowledge graph storage, semantic search, and vault indexing
//! for Obsidian-style markdown notes.

use axum::{
    extract::{Path as AxumPath, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post},
    Json, Router,
};
use serde::Deserialize;
use std::sync::Arc;
use tracing::{error, info};

mod knowledge_graph;
mod models;
mod storage;

use knowledge_graph::KnowledgeGraph;
use storage::KnowledgeGraphStorage;

/// Application state.
#[derive(Clone)]
struct AppState {
    api_key: String,
    kg: Arc<KnowledgeGraph>,
}

/// Query params for search/list endpoints.
#[derive(Deserialize)]
struct SearchQuery {
    #[serde(default)]
    query: String,
    #[serde(default = "default_limit")]
    limit: usize,
    #[serde(default)]
    #[allow(dead_code)]
    offset: usize,
}

#[derive(Deserialize)]
struct ListQuery {
    #[serde(default = "default_limit")]
    limit: usize,
    #[serde(default)]
    offset: usize,
}

#[allow(dead_code)]
#[derive(Deserialize)]
struct IndexQuery {
    #[serde(default)]
    reindex: bool,
}

fn default_limit() -> usize {
    10
}

/// Verify Bearer token.
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
    Json(serde_json::json!({"status": "ok", "service": "Gobber"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Gobber"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Gobber",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP gobber_uptime_seconds Service uptime in seconds.\n\
     # TYPE gobber_uptime_seconds gauge\n\
     gobber_uptime_seconds 0.0\n\
     # HELP gobber_ready Service readiness.\n\
     # TYPE gobber_ready gauge\n\
     gobber_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Gobber",
        "version": "2.0.0",
        "capabilities": [
            "knowledge_graph",
            "semantic_search",
            "keyword_search",
            "vault_indexing",
            "embedding_storage",
            "note_links",
        ],
    }))
}

async fn search_handler(
    State(state): State<AppState>,
    Query(query): Query<SearchQuery>,
) -> impl IntoResponse {
    if query.query.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(serde_json::json!({"detail": "Query parameter is required"})),
        )
            .into_response();
    }

    match state.kg.search(&query.query, query.limit).await {
        Ok(results) => (StatusCode::OK, Json(results)).into_response(),
        Err(e) => {
            error!("Search error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Search error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn list_notes_handler(
    State(state): State<AppState>,
    Query(query): Query<ListQuery>,
) -> impl IntoResponse {
    match state.kg.list_notes(query.limit, query.offset).await {
        Ok(notes) => (StatusCode::OK, Json(notes)).into_response(),
        Err(e) => {
            error!("List notes error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn get_note_handler(
    State(state): State<AppState>,
    AxumPath(note_id): AxumPath<String>,
) -> impl IntoResponse {
    match state.kg.get_note(&note_id).await {
        Ok(Some(note)) => (StatusCode::OK, Json(note)).into_response(),
        Ok(None) => (
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({"detail": "Note not found"})),
        )
            .into_response(),
        Err(e) => {
            error!("Get note error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn get_note_links_handler(
    State(state): State<AppState>,
    AxumPath(note_id): AxumPath<String>,
) -> impl IntoResponse {
    match state.kg.get_note_links(&note_id).await {
        Ok(links) => (StatusCode::OK, Json(links)).into_response(),
        Err(e) => {
            error!("Get links error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn get_related_notes_handler(
    State(state): State<AppState>,
    AxumPath(note_id): AxumPath<String>,
) -> impl IntoResponse {
    match state.kg.get_related_notes(&note_id, 5).await {
        Ok(results) => (StatusCode::OK, Json(results)).into_response(),
        Err(e) => {
            error!("Get related notes error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn delete_note_handler(
    State(state): State<AppState>,
    AxumPath(note_id): AxumPath<String>,
) -> impl IntoResponse {
    match state.kg.delete_note(&note_id).await {
        Ok(true) => (StatusCode::OK, Json(serde_json::json!({"deleted": true}))).into_response(),
        Ok(false) => (
            StatusCode::NOT_FOUND,
            Json(serde_json::json!({"detail": "Note not found"})),
        )
            .into_response(),
        Err(e) => {
            error!("Delete note error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn index_vault_handler(State(state): State<AppState>) -> impl IntoResponse {
    match state.kg.index_vault().await {
        Ok(result) => (StatusCode::OK, Json(result)).into_response(),
        Err(e) => {
            error!("Index vault error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

async fn stats_handler(State(state): State<AppState>) -> impl IntoResponse {
    match state.kg.get_stats().await {
        Ok(stats) => (StatusCode::OK, Json(stats)).into_response(),
        Err(e) => {
            error!("Stats error: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(serde_json::json!({"detail": format!("Error: {}", e)})),
            )
                .into_response()
        }
    }
}

/// Validate webhook URL to prevent SSRF.
#[allow(dead_code)]
fn validate_webhook_url(url: &str) -> Result<(), String> {
    let parsed = url::Url::parse(url).map_err(|e| format!("Invalid URL: {}", e))?;

    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        return Err("Webhook URL must use http or https scheme".to_string());
    }

    let host = parsed.host_str().unwrap_or("");

    // Block cloud metadata endpoints
    if matches!(
        host,
        "169.254.169.254" | "metadata.google.internal" | "metadata.cloud.oracle.com"
    ) {
        return Err("Webhook URL points to a blocked host".to_string());
    }

    // Block private IP ranges
    if let Ok(ip) = host.parse::<std::net::IpAddr>() {
        let is_private = match ip {
            std::net::IpAddr::V4(v4) => v4.is_private() || v4.is_loopback() || v4.is_link_local(),
            std::net::IpAddr::V6(v6) => v6.is_loopback(),
        };
        if is_private {
            return Err("Webhook URL must not point to a private IP address".to_string());
        }
    }

    Ok(())
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Gobber.");
        std::process::exit(1);
    }

    let db_url =
        std::env::var("DB_URL").unwrap_or_else(|_| "sqlite:///./data/gobber.db".to_string());
    let db = evershade_db::init_db(&db_url)
        .await
        .expect("Failed to connect to database");

    // Initialize schema
    storage::init_db(&db)
        .await
        .expect("Failed to create tables");

    let storage = KnowledgeGraphStorage::new(db);
    let kg = Arc::new(KnowledgeGraph::new(
        std::env::var("OBSIDIAN_VAULT_PATH").ok(),
        std::env::var("SHREWD_URL").ok(),
        std::env::var("SHREWD_API_KEY").ok(),
        std::env::var("EMBEDDING_MODEL").ok(),
        storage,
    ));

    let state = AppState { api_key, kg };

    let app = Router::new()
        // Health endpoints (public)
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        // Capabilities
        .route("/api/capabilities", get(capabilities_handler))
        // Knowledge graph endpoints
        .route("/api/knowledge/search", get(search_handler))
        .route("/api/knowledge/notes", get(list_notes_handler))
        .route("/api/knowledge/notes/{note_id}", get(get_note_handler))
        .route(
            "/api/knowledge/notes/{note_id}",
            delete(delete_note_handler),
        )
        .route(
            "/api/knowledge/notes/{note_id}/links",
            get(get_note_links_handler),
        )
        .route(
            "/api/knowledge/notes/{note_id}/related",
            get(get_related_notes_handler),
        )
        .route("/api/knowledge/index", post(index_vault_handler))
        .route("/api/knowledge/stats", get(stats_handler))
        .with_state(state.clone())
        .layer(axum::middleware::from_fn_with_state(
            state.clone(),
            auth_middleware,
        ));

    let addr = "0.0.0.0:8085";
    info!("Gobber listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
