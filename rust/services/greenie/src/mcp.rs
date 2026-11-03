//! MCP server management routes for Greenie.

use axum::{extract::Path, extract::State, http::StatusCode, Json};
use sea_orm::{ConnectionTrait, Statement};

use crate::{models::*, AppState};

/// List all MCP servers.
pub async fn list_mcp_servers(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let rows = state
        .db
        .query_all(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, name, url, transport, config, tools, connected, created_at \
             FROM mcp_servers ORDER BY created_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let servers: Vec<serde_json::Value> = rows
        .iter()
        .filter_map(|r| {
            Some(serde_json::json!({
                "id": r.try_get_by_index::<String>(0).ok()?,
                "name": r.try_get_by_index::<String>(1).ok()?,
                "url": r.try_get_by_index::<String>(2).ok()?,
                "transport": r.try_get_by_index::<String>(3).ok()?,
                "config": serde_json::from_str::<serde_json::Value>(&r.try_get_by_index::<String>(4).unwrap_or_else(|_| "{}".to_string()))
                    .unwrap_or_default(),
                "tools": serde_json::from_str(&r.try_get_by_index::<String>(5).unwrap_or_else(|_| "[]".to_string()))
                    .unwrap_or_else(|_| serde_json::Value::Array(Vec::new())),
                "connected": r.try_get_by_index::<i32>(6).unwrap_or(0) == 1,
                "created_at": r.try_get_by_index::<String>(7).ok()?,
            }))
        })
        .collect();

    Ok(Json(serde_json::json!({"servers": servers})))
}

/// Add a new MCP server.
pub async fn add_mcp_server(
    State(state): State<AppState>,
    Json(body): Json<McpServerAdd>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let name = body.name.trim().to_string();
    let url = body.url.trim().to_string();
    if name.is_empty() || url.is_empty() {
        return Err(StatusCode::BAD_REQUEST);
    }

    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id FROM mcp_servers WHERE name = '{}'",
                escape_sql(&name)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if existing.is_some() {
        return Err(StatusCode::CONFLICT);
    }

    let id = gen_id();
    let transport = if url.starts_with("http://") || url.starts_with("https://") {
        "http"
    } else if url.starts_with("sse://") {
        "sse"
    } else {
        "stdio"
    };

    let sql = format!(
        "INSERT INTO mcp_servers (id, name, url, transport) \
         VALUES ('{}', '{}', '{}', '{}')",
        id,
        escape_sql(&name),
        escape_sql(&url),
        transport
    );
    state
        .db
        .execute(Statement::from_string(state.db.get_database_backend(), sql))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": id,
        "name": name,
        "url": url,
        "transport": transport,
    })))
}

/// Remove an MCP server.
pub async fn remove_mcp_server(
    State(state): State<AppState>,
    Path(server_name): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id FROM mcp_servers WHERE name = '{}'",
                escape_sql(&server_name)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if existing.is_none() {
        return Err(StatusCode::NOT_FOUND);
    }

    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "DELETE FROM mcp_servers WHERE name = '{}'",
                escape_sql(&server_name)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "name": server_name,
        "deleted": true,
    })))
}
