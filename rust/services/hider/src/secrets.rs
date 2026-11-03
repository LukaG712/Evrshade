//! Secrets CRUD routes.

use axum::{Json, extract::Path, extract::State, http::StatusCode};
use sea_orm::{Statement, ConnectionTrait};
use serde_json::json;
use regex::Regex;

use crate::{AppState, SecretCreate, SecretUpdate, gen_id, log_audit};

/// Validate secret name to prevent path traversal and injection.
fn validate_secret_name(name: &str) -> Result<(), (StatusCode, String)> {
    if name.is_empty() {
        return Err((StatusCode::BAD_REQUEST, "Secret name cannot be empty".to_string()));
    }
    if name.len() > 255 {
        return Err((StatusCode::BAD_REQUEST, "Secret name is too long (max 255 characters)".to_string()));
    }
    if name.contains("..") || name.contains('\x00') {
        return Err((StatusCode::BAD_REQUEST, "Secret name contains invalid characters".to_string()));
    }
    let re = Regex::new(r"^[a-zA-Z0-9._/\-]+$").unwrap();
    if !re.is_match(name) {
        return Err((StatusCode::BAD_REQUEST, "Secret name can only contain alphanumeric characters, hyphens, underscores, dots, and slashes".to_string()));
    }
    Ok(())
}

/// Create a new encrypted secret.
pub async fn create_secret(
    state: State<AppState>,
    Json(body): Json<SecretCreate>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    validate_secret_name(&body.name)
        .map_err(|(s, msg)| (s, Json(json!({"detail": msg}))))?;

    let sid = gen_id();
    let (encrypted, iv) = state.encryption.encrypt(&body.value)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e}))))?;

    let now = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string();
    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "INSERT INTO secrets (id, name, encrypted_value, iv, tag, description, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '', '{}', '{}', '{}')",
            sid, body.name, encrypted, iv, body.description, now, now
        ),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    // Log history
    let hid = gen_id();
    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "INSERT INTO secret_history (id, secret_id, encrypted_value, iv, tag, version, action) VALUES ('{}', '{}', '{}', '{}', '', 1, 'created')",
            hid, sid, encrypted, iv
        ),
    )).await.ok();

    log_audit(&state.db, "create", "secret", &sid).await;

    Ok(Json(json!({
        "id": sid,
        "name": body.name,
        "description": body.description,
        "version": 1,
        "created_at": now,
        "updated_at": now,
    })))
}

/// List all secrets (without values).
pub async fn list_secrets(
    state: State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, (StatusCode, Json<serde_json::Value>)> {
    let rows = state.db.query_all(Statement::from_string(
        state.db.get_database_backend(),
        "SELECT id, name, description, version, created_at, updated_at FROM secrets ORDER BY name".to_string(),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let secrets: Vec<serde_json::Value> = rows.iter().map(|row| {
        json!({
            "id": row.try_get::<String>("", "id").unwrap_or_default(),
            "name": row.try_get::<String>("", "name").unwrap_or_default(),
            "description": row.try_get::<String>("", "description").unwrap_or_default(),
            "version": row.try_get::<i32>("", "version").unwrap_or(0),
            "created_at": row.try_get::<String>("", "created_at").unwrap_or_default(),
            "updated_at": row.try_get::<String>("", "updated_at").unwrap_or_default(),
        })
    }).collect();

    Ok(Json(secrets))
}

/// Get a secret by ID, returning the decrypted value.
pub async fn get_secret(
    state: State<AppState>,
    Path(secret_id): Path<String>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM secrets WHERE id = '{}'", secret_id),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let row = row.ok_or_else(|| (StatusCode::NOT_FOUND, Json(json!({"detail": "Secret not found"}))))?;

    let encrypted = row.try_get::<String>("", "encrypted_value").unwrap_or_default();
    let iv = row.try_get::<String>("", "iv").unwrap_or_default();
    let value = state.encryption.decrypt(&encrypted, &iv)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e}))))?;

    log_audit(&state.db, "read", "secret", &secret_id).await;

    Ok(Json(json!({
        "id": secret_id,
        "name": row.try_get::<String>("", "name").unwrap_or_default(),
        "value": value,
        "description": row.try_get::<String>("", "description").unwrap_or_default(),
        "version": row.try_get::<i32>("", "version").unwrap_or(0),
        "created_at": row.try_get::<String>("", "created_at").unwrap_or_default(),
        "updated_at": row.try_get::<String>("", "updated_at").unwrap_or_default(),
    })))
}

/// Update a secret's value.
pub async fn update_secret(
    state: State<AppState>,
    Path(secret_id): Path<String>,
    Json(body): Json<SecretUpdate>,
) -> Result<Json<serde_json::Value>, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM secrets WHERE id = '{}'", secret_id),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    let row = row.ok_or_else(|| (StatusCode::NOT_FOUND, Json(json!({"detail": "Secret not found"}))))?;

    let new_version = row.try_get::<i32>("", "version").unwrap_or(0) + 1;
    let (encrypted, iv) = state.encryption.encrypt(&body.value)
        .map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e}))))?;

    let now = chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string();
    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "UPDATE secrets SET encrypted_value = '{}', iv = '{}', tag = '', version = {}, updated_at = '{}' WHERE id = '{}'",
            encrypted, iv, new_version, now, secret_id
        ),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    // Log history
    let hid = gen_id();
    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!(
            "INSERT INTO secret_history (id, secret_id, encrypted_value, iv, tag, version, action) VALUES ('{}', '{}', '{}', '{}', '', {}, 'updated')",
            hid, secret_id, encrypted, iv, new_version
        ),
    )).await.ok();

    log_audit(&state.db, "update", "secret", &secret_id).await;

    let name = row.try_get::<String>("", "name").unwrap_or_default();
    Ok(Json(json!({
        "id": secret_id,
        "name": name,
        "value": body.value,
        "version": new_version,
    })))
}

/// Delete a secret.
pub async fn delete_secret(
    state: State<AppState>,
    Path(secret_id): Path<String>,
) -> Result<StatusCode, (StatusCode, Json<serde_json::Value>)> {
    let row = state.db.query_one(Statement::from_string(
        state.db.get_database_backend(),
        format!("SELECT * FROM secrets WHERE id = '{}'", secret_id),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    if row.is_none() {
        return Err((StatusCode::NOT_FOUND, Json(json!({"detail": "Secret not found"}))));
    }

    state.db.execute(Statement::from_string(
        state.db.get_database_backend(),
        format!("DELETE FROM secrets WHERE id = '{}'", secret_id),
    )).await.map_err(|e| (StatusCode::INTERNAL_SERVER_ERROR, Json(json!({"detail": e.to_string()}))))?;

    log_audit(&state.db, "delete", "secret", &secret_id).await;

    Ok(StatusCode::NO_CONTENT)
}
