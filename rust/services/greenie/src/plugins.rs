//! Plugin management routes for Greenie.

use axum::{extract::Path, extract::State, http::StatusCode, Json};
use sea_orm::{ConnectionTrait, Statement};

use crate::{models::*, AppState};

/// List all plugins.
pub async fn list_plugins(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let rows = state
        .db
        .query_all(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, name, description, type, source, config, enabled, installed_at \
             FROM plugins ORDER BY installed_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let plugins: Vec<serde_json::Value> = rows
        .iter()
        .filter_map(|r| {
            Some(serde_json::json!({
                "id": r.try_get_by_index::<String>(0).ok()?,
                "name": r.try_get_by_index::<String>(1).ok()?,
                "description": r.try_get_by_index::<String>(2).ok()?,
                "type": r.try_get_by_index::<String>(3).ok()?,
                "source": r.try_get_by_index::<String>(4).ok()?,
                "config": serde_json::from_str(&r.try_get_by_index::<String>(5).unwrap_or_else(|_| "{}".to_string()))
                    .unwrap_or_default(),
                "enabled": r.try_get_by_index::<i32>(6).unwrap_or(1) == 1,
                "installed_at": r.try_get_by_index::<String>(7).ok()?,
            }))
        })
        .collect();

    Ok(Json(serde_json::json!({"plugins": plugins})))
}

/// Install a new plugin.
pub async fn install_plugin(
    State(state): State<AppState>,
    Json(body): Json<PluginInstall>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let name = body.name.trim().to_string();
    let source = body.source.trim().to_string();
    if name.is_empty() {
        return Err(StatusCode::BAD_REQUEST);
    }
    if source.is_empty() {
        return Err(StatusCode::BAD_REQUEST);
    }

    let id = gen_id();
    let sql = format!(
        "INSERT INTO plugins (id, name, description, type, source) \
         VALUES ('{}', '{}', '{}', '{}', '{}')",
        id,
        escape_sql(&name),
        escape_sql(&body.description),
        escape_sql(&body.plugin_type),
        escape_sql(&source)
    );
    state
        .db
        .execute(Statement::from_string(state.db.get_database_backend(), sql))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": id,
        "name": name,
        "source": source,
        "type": body.plugin_type,
    })))
}

/// Update a plugin.
pub async fn update_plugin(
    State(state): State<AppState>,
    Path(plugin_id): Path<String>,
    Json(body): Json<PluginUpdate>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id FROM plugins WHERE id = '{}'",
                escape_sql(&plugin_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if existing.is_none() {
        return Err(StatusCode::NOT_FOUND);
    }

    if let Some(enabled) = body.enabled {
        state
            .db
            .execute(Statement::from_string(
                state.db.get_database_backend(),
                format!(
                    "UPDATE plugins SET enabled = {} WHERE id = '{}'",
                    if enabled { 1 } else { 0 },
                    escape_sql(&plugin_id)
                ),
            ))
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    }
    if let Some(config) = body.config {
        let config_str = serde_json::to_string(&config).unwrap_or_else(|_| "{}".to_string());
        state
            .db
            .execute(Statement::from_string(
                state.db.get_database_backend(),
                format!(
                    "UPDATE plugins SET config = '{}' WHERE id = '{}'",
                    escape_sql(&config_str),
                    escape_sql(&plugin_id)
                ),
            ))
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    }

    Ok(Json(serde_json::json!({
        "id": plugin_id,
        "updated": true,
    })))
}

/// Uninstall a plugin.
pub async fn uninstall_plugin(
    State(state): State<AppState>,
    Path(plugin_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id FROM plugins WHERE id = '{}'",
                escape_sql(&plugin_id)
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
                "DELETE FROM plugins WHERE id = '{}'",
                escape_sql(&plugin_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": plugin_id,
        "deleted": true,
    })))
}
