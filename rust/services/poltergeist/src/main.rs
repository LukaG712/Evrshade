//! Poltergeist — Notification delivery service.
//!
//! Delivers notifications via Slack, Email, Telegram, and generic webhooks.
//! Includes SSRF protection for webhook URLs and rate limiting.

use axum::{
    http::StatusCode,
    middleware::from_fn,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use sea_orm::{ConnectionTrait, DatabaseConnection, Statement};
use serde::Deserialize;
use tracing::info;
use uuid::Uuid;

mod delivery;
mod models;

/// Application state.
#[derive(Clone)]
struct AppState {
    db: DatabaseConnection,
    api_key: String,
}

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    recipient TEXT NOT NULL,
    title TEXT DEFAULT '',
    body TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
"#;

fn gen_id() -> String {
    Uuid::new_v4().to_string()
}

/// Notification request.
#[derive(Deserialize)]
struct NotificationRequest {
    channel: String,
    recipient: String,
    #[serde(default)]
    title: String,
    body: String,
}

/// API key authentication middleware.
async fn auth_middleware(
    state: axum::extract::State<AppState>,
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

    let auth_header = req.headers().get("Authorization");
    let token = auth_header
        .and_then(|auth| auth.to_str().ok())
        .and_then(|auth_str| auth_str.strip_prefix("Bearer "))
        .map(|stripped| stripped.to_string());

    let token = match token {
        Some(t) => t,
        None => {
            return (
                StatusCode::UNAUTHORIZED,
                Json(serde_json::json!({"detail": "Missing or invalid Authorization header"})),
            )
                .into_response();
        }
    };

    if !use_equal(&token, &state.api_key) {
        return (
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({"detail": "Invalid API key"})),
        )
            .into_response();
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
    Json(serde_json::json!({"status": "ok", "service": "Poltergeist", "version": "2.0.0"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Poltergeist"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Poltergeist",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP poltergeist_uptime_seconds Service uptime in seconds.\n\
     # TYPE poltergeist_uptime_seconds gauge\n\
     poltergeist_uptime_seconds 0.0\n\
     # HELP poltergeist_ready Service readiness.\n\
     # TYPE poltergeist_ready gauge\n\
     poltergeist_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Poltergeist",
        "version": "2.0.0",
        "capabilities": [
            "slack_webhook",
            "email_smtp",
            "telegram_bot",
            "generic_webhook",
            "rate_limiting",
        ],
        "integrations": {
            "opentelemetry": {"enabled": false},
            "sqlite": {"enabled": true},
        },
    }))
}

/// Send a notification.
async fn send_notification(
    state: axum::extract::State<AppState>,
    Json(body): Json<NotificationRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let nid = gen_id();
    let now = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string();

    // Attempt delivery
    let result = delivery::deliver(&body.channel, &body.recipient, &body.title, &body.body).await;

    let (status, error, sent_at) = match result {
        Ok(_) => ("sent".to_string(), String::new(), Some(now.clone())),
        Err(e) => ("failed".to_string(), e, None),
    };

    // Store in database
    let sent_at_val = sent_at.as_deref().unwrap_or("");
    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "INSERT INTO notifications (id, channel, recipient, title, body, status, error, created_at, sent_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')",
            nid, body.channel, body.recipient, body.title, body.body, status, error, now, sent_at_val
        ),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"detail": e.to_string()}))))?;

    Ok(Json(serde_json::json!({
        "id": nid,
        "channel": body.channel,
        "status": status,
        "created_at": now,
    })))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Poltergeist.");
        std::process::exit(1);
    }

    let db_url =
        std::env::var("DB_URL").unwrap_or_else(|_| "sqlite:///./data/poltergeist.db".to_string());
    let db = evershade_db::init_db(&db_url)
        .await
        .expect("Failed to connect to database");

    db.execute(Statement::from_string(
        db.get_database_backend(),
        SCHEMA_SQL.to_string(),
    ))
    .await
    .expect("Failed to create tables");

    let state = AppState { db, api_key };

    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        .route("/api/capabilities", get(capabilities_handler))
        .route("/api/notifications", post(send_notification))
        .with_state(state.clone())
        .layer(from_fn(move |req, next| {
            auth_middleware(axum::extract::State(state.clone()), req, next)
        }));

    let addr = "0.0.0.0:8088";
    info!("Poltergeist listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
