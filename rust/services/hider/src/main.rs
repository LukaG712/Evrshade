//! Hider — Secrets management service.
//!
//! Provides encrypted secrets storage using AES-256-GCM, versioned config,
//! and audit logging for all secret access.

use axum::{
    Router, routing::{get, post, put, delete}, Json, middleware::from_fn,
    http::StatusCode, response::IntoResponse,
};
use sea_orm::{DatabaseConnection, Statement, ConnectionTrait};
use serde::Deserialize;
use std::sync::Arc;
use tracing::info;
use uuid::Uuid;

mod encryption;
mod secrets;
mod config;

use encryption::Encryption;

/// Application state shared across handlers.
#[derive(Clone)]
struct AppState {
    db: DatabaseConnection,
    encryption: Arc<Encryption>,
    api_key: String,
}

/// Secret creation request.
#[derive(Deserialize)]
struct SecretCreate {
    name: String,
    value: String,
    #[serde(default)]
    description: String,
}

/// Secret update request.
#[derive(Deserialize)]
struct SecretUpdate {
    value: String,
}

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS secrets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    encrypted_value TEXT NOT NULL,
    iv TEXT NOT NULL,
    tag TEXT NOT NULL,
    description TEXT DEFAULT '',
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS secret_history (
    id TEXT PRIMARY KEY,
    secret_id TEXT NOT NULL,
    encrypted_value TEXT NOT NULL,
    iv TEXT NOT NULL,
    tag TEXT NOT NULL,
    version INTEGER NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('created', 'updated', 'deleted')),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (secret_id) REFERENCES secrets(id)
);

CREATE TABLE IF NOT EXISTS config_entries (
    id TEXT PRIMARY KEY,
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    is_encrypted INTEGER DEFAULT 0,
    description TEXT DEFAULT '',
    version INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_secret_history_secret_id ON secret_history(secret_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource_id ON audit_log(resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);
"#;

fn gen_id() -> String {
    Uuid::new_v4().to_string()
}

async fn log_audit(db: &DatabaseConnection, action: &str, resource_type: &str, resource_id: &str) {
    let id = gen_id();
    db.execute(Statement::from_string(
        db.get_database_backend(),
        format!(
            "INSERT INTO audit_log (id, action, resource_type, resource_id) VALUES ('{}', '{}', '{}', '{}')",
            id, action, resource_type, resource_id
        ),
    )).await.ok();
}

/// API key authentication middleware.
async fn auth_middleware(
    state: axum::extract::State<AppState>,
    req: axum::http::Request<axum::body::Body>,
    next: axum::middleware::Next,
) -> axum::response::Response {
    let path = req.uri().path().to_string();
    let public_paths = ["/health", "/ready", "/metrics", "/api/status", "/docs", "/openapi.json"];
    if public_paths.contains(&path.as_str()) {
        return next.run(req).await;
    }

    let auth_header = req.headers().get("Authorization");
    let token = if let Some(auth) = auth_header {
        if let Ok(auth_str) = auth.to_str() {
            if auth_str.starts_with("Bearer ") {
                Some(auth_str[7..].to_string())
            } else {
                None
            }
        } else {
            None
        }
    } else {
        None
    };

    let token = match token {
        Some(t) => t,
        None => {
            return (StatusCode::UNAUTHORIZED, Json(serde_json::json!({"detail": "Missing or invalid Authorization header"}))).into_response();
        }
    };

    if !use_equal(&token, &state.api_key) {
        return (StatusCode::UNAUTHORIZED, Json(serde_json::json!({"detail": "Invalid API key"}))).into_response();
    }

    next.run(req).await
}

fn use_equal(a: &str, b: &str) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut result = 0u8;
    for (x, y) in a.bytes().zip(b.bytes()) {
        result |= x ^ y;
    }
    result == 0
}

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "Hider", "version": "2.0.0"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Hider"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Hider",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP hider_uptime_seconds Service uptime in seconds.\n\
     # TYPE hider_uptime_seconds gauge\n\
     hider_uptime_seconds 0.0\n\
     # HELP hider_ready Service readiness.\n\
     # TYPE hider_ready gauge\n\
     hider_ready 1\n".to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Hider",
        "version": "2.0.0",
        "capabilities": [
            "secrets_encryption",
            "secrets_storage",
            "versioned_config",
            "audit_logging",
            "service_tokens",
        ],
        "integrations": {
            "opentelemetry": {"enabled": false},
            "sqlite": {"enabled": true},
        },
    }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Hider.");
        std::process::exit(1);
    }

    let encryption = Arc::new(Encryption::new().expect("Failed to initialize encryption"));

    let db_url = std::env::var("DB_URL").unwrap_or_else(|_| "sqlite:///./data/hider.db".to_string());
    let db = evershade_db::init_db(&db_url).await.expect("Failed to connect to database");

    db.execute(Statement::from_string(
        db.get_database_backend(),
        SCHEMA_SQL.to_string(),
    )).await.expect("Failed to create tables");

    let state = AppState { db, encryption, api_key };

    let app = Router::new()
        // Health endpoints (public)
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        // Secrets endpoints
        .route("/api/secrets/", post(secrets::create_secret))
        .route("/api/secrets/", get(secrets::list_secrets))
        .route("/api/secrets/{secret_id}", get(secrets::get_secret))
        .route("/api/secrets/{secret_id}", put(secrets::update_secret))
        .route("/api/secrets/{secret_id}", delete(secrets::delete_secret))
        // Config endpoints
        .route("/api/config/", post(config::create_config))
        .route("/api/config/", get(config::list_config))
        .route("/api/config/{config_key}", get(config::get_config))
        .route("/api/config/{config_key}", put(config::update_config))
        .route("/api/config/{config_key}", delete(config::delete_config))
        // Capabilities
        .route("/api/capabilities", get(capabilities_handler))
        .with_state(state.clone())
        .layer(from_fn(move |req, next| auth_middleware(axum::extract::State(state.clone()), req, next)));

    let addr = "0.0.0.0:8087";
    info!("Hider listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
