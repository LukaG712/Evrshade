//! Greenie — Mission orchestration service.
//!
//! Provides agent lifecycle management, mission planning, task delegation,
//! plugin management, MCP server configuration, and workstation management
//! with Docker integration.

mod agents;
mod mcp;
mod missions;
mod models;
mod plugins;
mod tasks;
mod workstations;

use axum::{
    Router,
    body::Body,
    extract::State,
    http::StatusCode,
    middleware::Next,
    routing::{delete, get, patch, post},
    Json,
};
use sea_orm::{ConnectionTrait, DatabaseConnection, Statement};
use tracing::info;

// ─── Database Schema ───────────────────────────────────────────────

const SCHEMA_SQL: &str = r#"
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    model TEXT DEFAULT '',
    system_prompt TEXT DEFAULT '',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'paused')),
    metadata TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    agent_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    progress REAL DEFAULT 0.0,
    result TEXT DEFAULT '',
    error TEXT DEFAULT '',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    type TEXT DEFAULT 'execution',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    payload TEXT DEFAULT '{}',
    result TEXT DEFAULT '',
    error TEXT DEFAULT '',
    assigned_to TEXT DEFAULT '',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (mission_id) REFERENCES missions(id)
);

CREATE TABLE IF NOT EXISTS plugins (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    type TEXT DEFAULT 'tool',
    source TEXT DEFAULT '',
    config TEXT DEFAULT '{}',
    enabled INTEGER DEFAULT 1,
    installed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS mcp_servers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    transport TEXT DEFAULT 'stdio',
    config TEXT DEFAULT '{}',
    tools TEXT DEFAULT '[]',
    connected INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS workstations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    agent_name TEXT DEFAULT '',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'creating', 'running', 'stopped', 'error', 'destroyed')),
    container_id TEXT DEFAULT '',
    container_name TEXT DEFAULT '',
    started_at TEXT,
    image TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    error TEXT DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_missions_agent_id ON missions(agent_id);
CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(status);
CREATE INDEX IF NOT EXISTS idx_tasks_mission_id ON tasks(mission_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_plugins_enabled ON plugins(enabled);
CREATE INDEX IF NOT EXISTS idx_workstations_status ON workstations(status);
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
    req: Request<Body>,
    next: Next,
) -> axum::response::Response {
    use axum::http::Request as HttpRequest;

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
    Json(serde_json::json!({"status": "ok", "service": "Greenie", "version": "2.0.0"}))
}

async fn ready_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({"status": "ready", "service": "Greenie"}))
}

async fn status_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Greenie",
        "version": "2.0.0",
        "status": "running",
    }))
}

async fn metrics_handler() -> String {
    "# HELP greenie_uptime_seconds Service uptime in seconds.\n\
     # TYPE greenie_uptime_seconds gauge\n\
     greenie_uptime_seconds 0.0\n\
     # HELP greenie_ready Service readiness.\n\
     # TYPE greenie_ready gauge\n\
     greenie_ready 1\n"
        .to_string()
}

async fn capabilities_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "service": "Greenie",
        "version": "2.0.0",
        "capabilities": [
            "agent_management",
            "mission_planning",
            "task_orchestration",
            "chat_sessions",
            "service_registry",
            "sse_streaming",
            "workflow_engine",
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
        eprintln!("API_KEY environment variable is not set. Refusing to start Greenie.");
        std::process::exit(1);
    }

    let db_url = std::env::var("DB_URL")
        .unwrap_or_else(|_| "sqlite:///./data/greenie.db".to_string());
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
        // Agent routes
        .route("/api/agents/", post(agents::create_agent))
        .route("/api/agents/", get(agents::list_agents))
        .route("/api/agents/{agent_id}", get(agents::get_agent))
        .route(
            "/api/agents/{agent_id}",
            delete(agents::delete_agent),
        )
        // Mission routes
        .route("/api/missions/", post(missions::create_mission))
        .route("/api/missions/", get(missions::list_missions))
        .route("/api/missions/{mission_id}", get(missions::get_mission))
        .route(
            "/api/missions/{mission_id}/start",
            post(missions::start_mission),
        )
        .route(
            "/api/missions/{mission_id}",
            delete(missions::delete_mission),
        )
        // Task routes
        .route("/api/tasks/", post(tasks::create_task))
        .route("/api/tasks/", get(tasks::list_tasks))
        .route("/api/tasks/{task_id}", get(tasks::get_task))
        .route("/api/tasks/{task_id}/start", post(tasks::start_task))
        .route("/api/tasks/{task_id}", delete(tasks::delete_task))
        // Plugin routes
        .route("/api/plugins/", get(plugins::list_plugins))
        .route("/api/plugins/", post(plugins::install_plugin))
        .route("/api/plugins/{plugin_id}", patch(plugins::update_plugin))
        .route(
            "/api/plugins/{plugin_id}",
            delete(plugins::uninstall_plugin),
        )
        // MCP routes
        .route("/api/mcp/servers", get(mcp::list_mcp_servers))
        .route("/api/mcp/servers", post(mcp::add_mcp_server))
        .route(
            "/api/mcp/servers/{server_name}",
            delete(mcp::remove_mcp_server),
        )
        // Workstation routes
        .route(
            "/api/workstations/",
            get(workstations::list_workstations),
        )
        .route(
            "/api/workstations/stats",
            get(workstations::get_workstation_stats),
        )
        .route(
            "/api/workstations/",
            post(workstations::create_workstation),
        )
        .route(
            "/api/workstations/{ws_id}/start",
            post(workstations::start_workstation),
        )
        .route(
            "/api/workstations/{ws_id}/stop",
            post(workstations::stop_workstation),
        )
        .route(
            "/api/workstations/{ws_id}/destroy",
            post(workstations::destroy_workstation),
        )
        .route(
            "/api/workstations/{ws_id}/logs",
            get(workstations::get_workstation_logs),
        )
        .with_state(state.clone())
        .layer(axum::middleware::from_fn(move |req, next| {
            auth_middleware(State(state.clone()), req, next)
        }));

    let addr = "0.0.0.0:8080";
    info!("Greenie listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
