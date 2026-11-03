//! Versioned configuration routes.

use axum::{Json, extract::Path, extract::State, http::StatusCode};
use sea_orm::{Statement, ConnectionTrait};
use serde_json::json;
use serde::{Deserialize, Serialize};

use crate::{AppState, gen_id};

#[derive(Deserialize)]
pub struct ConfigCreate {
    key: String,
    value: String,
    #[serde(default)]
    is_encrypted: bool,
    #[serde(default)]
    description: String,
}

#[derive(Deserialize)]
pub struct ConfigUpdate {
    value: String,
    #[serde(default)]
    is_encrypted: bool,
    #[serde(default)]
    description: String,
}

/// Create a new config entry.
pub async fn create_config(
    state: State<AppState>,
    Json(body): Json<ConfigCreate>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let cid = gen_id();
    let now = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string();
    let is_encrypted = if body.is_encrypted { 1 } else { 0 };

    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "INSERT INTO config_entries (id, key, value, is_encrypted, description, version, created_at, updated_at) VALUES ('{}', '{}', '{}', {}, '{}', 1, '{}', '{}')",
            cid, body.key, body.value, is_encrypted, body.description, now, now
        ),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    Ok(Json(json!({
        "id": cid,
        "key": body.key,
        "value": body.value,
        "is_encrypted": body.is_encrypted,
        "description": body.description,
        "version": 1,
        "created_at": now,
        "updated_at": now,
    })))
}

/// List all config entries.
pub async fn list_config(
    state: State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, (StatusCode, Json<serde_json::Value>)> {
    let rows = state.db.query_all(Statement::from_string(
        state.db.get_database_backend(),
        "SELECT id, key, value, is_encrypted, description, version, created_at, updated_at FROM config_entries ORDER BY key".to_string(),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let configs: Vec<serde_json::Value> = rows.iter().map(|row| {
        json!({
            "id": row.try_get::<String>("", "id").unwrap_or_default(),
            "key": row.try_get::<String>("", "key").unwrap_or_default(),
            "value": row.try_get::<String>("", "value").unwrap_or_default(),
            "is_encrypted": row.try_get::<i32>("", "is_encrypted").unwrap_or(0) == 1,
            "description": row.try_get::<String>("", "description").unwrap_or_default(),
            "version": row.try_get::<i32>("", "version").unwrap_or(0),
            "created_at": row.try_get::<String>("", "created_at").unwrap_or_default(),
            "updated_at": row.try_get::<String>("", "updated_at").unwrap_or_default(),
        })
    }).collect();

    Ok(Json(configs))
}

/// Get a config entry by key.
pub async fn get_config(
    state: State<AppState>,
    Path(config_key): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM config_entries WHERE key = '{}'", config_key),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let row = row.ok_or_else(|| (StatusCode::NOT_FOUND, Json(json!({"detail": "Config not found"}))))?;

    Ok(Json(json!({
        "id": row.try_get::<String>("", "id").unwrap_or_default(),
        "key": config_key,
        "value": row.try_get::<String>("", "value").unwrap_or_default(),
        "is_encrypted": row.try_get::<i32>("", "is_encrypted").unwrap_or(0) == 1,
        "description": row.try_get::<String>("", "description").unwrap_or_default(),
        "version": row.try_get::<i32>("", "version").unwrap_or(0),
        "created_at": row.try_get::<String>("", "created_at").unwrap_or_default(),
        "updated_at": row.try_get::<String>("", "updated_at").unwrap_or_default(),
    })))
}

/// Update a config entry.
pub async fn update_config(
    state: State<AppState>,
    Path(config_key): Path<String>,
    Json(body): Json<ConfigUpdate>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM config_entries WHERE key = '{}'", config_key),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let row = row.ok_or_else(|| (StatusCode::NOT_FOUND, Json(json!({"detail": "Config not found"}))))?;

    let new_version = row.try_get::<i32>("", "version").unwrap_or(0) + 1;
    let now = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string();
    let is_encrypted = if body.is_encrypted { 1 } else { 0 };

    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "UPDATE config_entries SET value = '{}', is_encrypted = {}, description = '{}', version = {}, updated_at = '{}' WHERE key = '{}'",
            body.value, is_encrypted, body.description, new_version, now, config_key
        ),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let cid = row.try_get::<String>("", "id").unwrap_or_default();
    Ok(Json(json!({
        "id": cid,
        "key": config_key,
        "value": body.value,
        "is_encrypted": body.is_encrypted,
        "description": body.description,
        "version": new_version,
        "updated_at": now,
    })))
}

/// Delete a config entry.
pub async fn delete_config(
    state: State<AppState>,
    Path(config_key): Path<String>,
) -> Result<StatusCode, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM config_entries WHERE key = '{}'", config_key),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    if row.is_none() {
        return Err((StatusCode::NOT_FOUND, Json(json!({"detail": "Config not found"}))));
    }

    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!("DELETE FROM config_entries WHERE key = '{}'", config_key),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    Ok(StatusCode::NO_CONTENT)
}
