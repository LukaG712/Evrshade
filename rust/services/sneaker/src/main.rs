//! Sneaker — Observability/OTLP collector service.
//!
//! Receives OTLP traces, metrics, and logs; stores them in SQLite;
//! exposes Prometheus metrics and alerting rules.

use axum::{
    http::StatusCode,
    middleware::from_fn,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use sea_orm::{ConnectionTrait, DatabaseConnection, Statement};
use tracing::info;
use uuid::Uuid;

mod alerting;
mod models;
mod otlp;


/// Application state.
#[derive(Clone)]
struct AppState {
    db: DatabaseConnection,
    api_key: String,
}

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value REAL NOT NULL,
    labels TEXT DEFAULT '{}',
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL,
    parent_span_id TEXT,
    name TEXT NOT NULL,
    duration_ms REAL,
    status TEXT,
    attributes TEXT DEFAULT '{}',
    timestamp TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    service TEXT,
    attributes TEXT DEFAULT '{}',
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_traces_trace_id ON traces(trace_id);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
"#;

#[allow(dead_code)]
fn gen_id() -> String {
    Uuid::new_v4().to_string()
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
    let token = if let Some(auth) = auth_header {
        if let Ok(auth_str) = auth.to_str() {
            if let Some(stripped) = auth_str.strip_prefix("Bearer ") {
                Some(stripped.to_string())
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
    Json(serde_json::json!({"status": "ok", "service": "Sneaker", "version": "2.0.0"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Sneaker"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Sneaker",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP sneaker_uptime_seconds Service uptime in seconds.\n\
     # TYPE sneaker_uptime_seconds gauge\n\
     sneaker_uptime_seconds 0.0\n\
     # HELP sneaker_ready Service readiness.\n\
     # TYPE sneaker_ready gauge\n\
     sneaker_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Sneaker",
        "version": "2.0.0",
        "capabilities": [
            "otlp_traces",
            "otlp_metrics",
            "otlp_logs",
            "prometheus_metrics",
            "alerting",
        ],
        "integrations": {
            "opentelemetry": {"enabled": true},
            "sqlite": {"enabled": true},
        },
    }))
}

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Sneaker.");
        std::process::exit(1);
    }

    let db_url =
        std::env::var("DB_URL").unwrap_or_else(|_| "sqlite:///./data/sneaker.db".to_string());
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
        // OTLP endpoints
        .route("/v1/traces", post(otlp::receive_traces))
        .route("/v1/metrics", post(otlp::receive_metrics))
        .route("/v1/logs", post(otlp::receive_logs))
        .route("/api/otlp/stats", get(otlp::get_otlp_stats))
        // Alerting endpoints
        .route("/api/alerts", get(alerting::list_alerts))
        .route("/api/alerts/rules", get(alerting::list_rules))
        .with_state(state.clone())
        .layer(from_fn(move |req, next| {
            auth_middleware(axum::extract::State(state.clone()), req, next)
        }));

    let addr = "0.0.0.0:8086";
    info!("Sneaker listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
