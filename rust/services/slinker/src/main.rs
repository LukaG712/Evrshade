//! Slinker — Code execution sandbox service.
//!
//! Provides task execution in isolated workspaces with subprocess and Junie CLI
//! adapters, OpenAI-compatible endpoints, and command injection prevention.

mod adapters;
mod execution;
mod openai;

use axum::{
    body::Body,
    extract::State,
    http::StatusCode,
    middleware::Next,
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use sea_orm::{ConnectionTrait, DatabaseConnection, Statement};
use tracing::info;

// ─── Database Schema ───────────────────────────────────────────────

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    project_id TEXT DEFAULT '',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    worktree_path TEXT DEFAULT '',
    command TEXT DEFAULT '',
    output TEXT DEFAULT '',
    error TEXT DEFAULT '',
    exit_code INTEGER,
    worker_id TEXT DEFAULT '',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'idle' CHECK(status IN ('idle', 'busy', 'stopped')),
    current_task_id TEXT DEFAULT '',
    last_heartbeat TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repo_url TEXT DEFAULT '',
    branch TEXT DEFAULT 'main',
    worktree_base TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'failed')),
    task_count INTEGER DEFAULT 0,
    started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS session_logs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    task_id TEXT DEFAULT '',
    level TEXT DEFAULT 'info' CHECK(level IN ('debug', 'info', 'warn', 'error')),
    message TEXT NOT NULL DEFAULT '',
    data TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    project_id TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'locked', 'deleted')),
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS execution_sessions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    adapter TEXT NOT NULL,
    workspace_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled', 'timeout')),
    output TEXT,
    error TEXT,
    exit_code INTEGER DEFAULT 0,
    duration_ms INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at TEXT,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

CREATE TABLE IF NOT EXISTS file_changes (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    path TEXT NOT NULL,
    action TEXT NOT NULL CHECK(action IN ('created', 'modified', 'deleted')),
    diff TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (session_id) REFERENCES execution_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_workers_status ON workers(status);
CREATE INDEX IF NOT EXISTS idx_session_logs_session_id ON session_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_project_id ON workspaces(project_id);
CREATE INDEX IF NOT EXISTS idx_execution_sessions_task_id ON execution_sessions(task_id);
CREATE INDEX IF NOT EXISTS idx_execution_sessions_status ON execution_sessions(status);
CREATE INDEX IF NOT EXISTS idx_file_changes_session_id ON file_changes(session_id);
"#;

// ─── Application State ─────────────────────────────────────────────

#[derive(Clone)]
struct AppState {
    db: DatabaseConnection,
    api_key: String,
}

// ─── Auth Middleware ───────────────────────────────────────────────

async fn auth_middleware(
    state: State<AppState>,
    req: axum::http::Request<Body>,
    next: Next,
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
        .and_then(|auth_str| auth_str.strip_prefix("Bearer ").map(|s| s.to_string()));

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

    if !constant_time_eq(&token, &state.api_key) {
        return (
            StatusCode::UNAUTHORIZED,
            Json(serde_json::json!({"detail": "Invalid API key"})),
        )
            .into_response();
    }

    next.run(req).await
}

fn constant_time_eq(a: &str, b: &str) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut result = 0u8;
    for (x, y) in a.bytes().zip(b.bytes()) {
        result |= x ^ y;
    }
    result == 0
}

// ─── Health & Status ───────────────────────────────────────────────

async fn health_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ok", "service": "Slinker", "version": "2.0.0"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Slinker"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Slinker",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP slinker_uptime_seconds Service uptime in seconds.\n\
     # TYPE slinker_uptime_seconds gauge\n\
     slinker_uptime_seconds 0.0\n\
     # HELP slinker_ready Service readiness.\n\
     # TYPE slinker_ready gauge\n\
     slinker_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Slinker",
        "version": "2.0.0",
        "capabilities": [
            "task_execution",
            "worker_registry",
            "project_management",
            "session_logging",
            "openai_compatible",
            "git_worktrees",
        ],
        "integrations": {
            "opentelemetry": {"enabled": false},
            "sqlite": {"enabled": true},
        },
    }))
}

// ─── Main ──────────────────────────────────────────────────────────

#[tokio::main]
async fn main() {
    tracing_subscriber::fmt::init();

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    if api_key.is_empty() {
        eprintln!("API_KEY environment variable is not set. Refusing to start Slinker.");
        std::process::exit(1);
    }

    let db_url =
        std::env::var("DB_URL").unwrap_or_else(|_| "sqlite:///./data/slinker.db".to_string());
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
        // Health endpoints (public)
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        // Capabilities
        .route("/api/capabilities", get(capabilities_handler))
        // Execution routes
        .route("/api/v1/tasks", post(execution::create_task))
        .route("/api/v1/tasks", get(execution::list_tasks))
        .route("/api/v1/tasks/{task_id}", get(execution::get_task))
        .route(
            "/api/v1/tasks/{task_id}/cancel",
            post(execution::cancel_task),
        )
        .route(
            "/api/v1/tasks/adapters",
            get(execution::list_adapters_handler),
        )
        .route(
            "/api/v1/tasks/{task_id}/run-tests",
            post(execution::run_tests_handler),
        )
        .route(
            "/api/v1/tasks/{task_id}/run-lint",
            post(execution::run_lint_handler),
        )
        .route(
            "/api/v1/tasks/{task_id}/run-build",
            post(execution::run_build_handler),
        )
        // OpenAI-compatible routes
        .route("/v1/models", get(openai::list_models_handler))
        .route("/v1/chat/completions", post(openai::chat_completions))
        .with_state(state.clone())
        .layer(axum::middleware::from_fn(move |req, next| {
            auth_middleware(State(state.clone()), req, next)
        }));

    let addr = "0.0.0.0:8000";
    info!("Slinker listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
