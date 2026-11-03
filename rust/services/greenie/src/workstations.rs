//! Workstation management routes for Greenie.
//!
//! Handles workstation CRUD and Docker container lifecycle (start/stop/destroy).

use axum::{Json, extract::Path, extract::Query, extract::State, http::StatusCode};
use sea_orm::{ConnectionTrait, Statement};
use serde::Deserialize;

use crate::{AppState, models::*};

/// Validate container name matches the expected pattern.
fn validate_container_name(name: &str) -> Result<(), String> {
    if name.is_empty() {
        return Err("Container name is empty".to_string());
    }
    let re = regex::Regex::new(r"^evershade-ws-[a-f0-9]{8}$").unwrap();
    if !re.is_match(name) {
        return Err(format!(
            "Container name '{}' does not match expected pattern 'evershade-ws-*'",
            name
        ));
    }
    Ok(())
}

/// Run a Docker command asynchronously.
async fn run_docker(args: &[&str], timeout_secs: u64) -> Result<(i32, String, String), String> {
    let mut cmd = tokio::process::Command::new("docker");
    cmd.args(args);
    let output = tokio::time::timeout(
        std::time::Duration::from_secs(timeout_secs),
        cmd.output(),
    )
    .await
    .map_err(|_| "Timeout".to_string())?
    .map_err(|e| format!("Docker not found: {}", e))?;

    Ok((
        output.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&output.stdout).to_string(),
        String::from_utf8_lossy(&output.stderr).to_string(),
    ))
}

async fn count_query(
    db: &sea_orm::DatabaseConnection,
    sql: String,
) -> Result<i64, sea_orm::DbErr> {
    let row = db
        .query_one(Statement::from_string(db.get_database_backend(), sql))
        .await?;
    match row {
        Some(r) => Ok(r.try_get_by_index::<i64>(0).unwrap_or(0)),
        None => Ok(0),
    }
}

/// List all workstations.
pub async fn list_workstations(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let rows = state
        .db
        .query(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, name, description, agent_name, status, container_id, container_name, \
             started_at, image, tags, error, created_at, updated_at \
             FROM workstations ORDER BY created_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let workstations: Vec<serde_json::Value> = rows
        .iter()
        .filter_map(|r| {
            Some(serde_json::json!({
                "id": r.try_get_by_index::<String>(0).ok()?,
                "name": r.try_get_by_index::<String>(1).ok()?,
                "description": r.try_get_by_index::<String>(2).ok()?,
                "agent_name": r.try_get_by_index::<String>(3).ok()?,
                "status": r.try_get_by_index::<String>(4).ok()?,
                "container_id": r.try_get_by_index::<String>(5).ok()?,
                "container_name": r.try_get_by_index::<String>(6).ok()?,
                "started_at": r.try_get_by_index::<String>(7).ok(),
                "image": r.try_get_by_index::<String>(8).ok()?,
                "tags": serde_json::from_str(&r.try_get_by_index::<String>(9).unwrap_or_else(|_| "[]".to_string()))
                    .unwrap_or_else(|_| serde_json::Value::Array(Vec::new())),
                "error": r.try_get_by_index::<String>(10).ok()?,
                "created_at": r.try_get_by_index::<String>(11).ok()?,
                "updated_at": r.try_get_by_index::<String>(12).ok()?,
            }))
        })
        .collect();

    Ok(Json(serde_json::json!({"workstations": workstations})))
}

/// Get workstation statistics.
pub async fn get_workstation_stats(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let total = count_query(&state.db, "SELECT COUNT(*) FROM workstations".to_string())
        .await
        .unwrap_or(0);
    let running = count_query(
        &state.db,
        "SELECT COUNT(*) FROM workstations WHERE status = 'running'".to_string(),
    )
    .await
    .unwrap_or(0);
    let stopped = count_query(
        &state.db,
        "SELECT COUNT(*) FROM workstations WHERE status = 'stopped'".to_string(),
    )
    .await
    .unwrap_or(0);
    let error = count_query(
        &state.db,
        "SELECT COUNT(*) FROM workstations WHERE status = 'error'".to_string(),
    )
    .await
    .unwrap_or(0);

    let docker_available = matches!(run_docker(&["info"], 5).await, Ok((0, _, _)));

    Ok(Json(serde_json::json!({
        "total": total,
        "running": running,
        "stopped": stopped,
        "error": error,
        "docker_available": docker_available,
    })))
}

/// Create a new workstation.
pub async fn create_workstation(
    State(state): State<AppState>,
    Json(body): Json<WorkstationCreate>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let name = body.name.trim().to_string();
    if name.is_empty() {
        return Err(StatusCode::BAD_REQUEST);
    }

    let id = gen_id();
    let tags_json =
        serde_json::to_string(&body.tags).unwrap_or_else(|_| "[]".to_string());
    let sql = format!(
        "INSERT INTO workstations (id, name, description, agent_name, tags) \
         VALUES ('{}', '{}', '{}', '{}', '{}')",
        id,
        escape_sql(&name),
        escape_sql(&body.description),
        escape_sql(&body.agent_name),
        escape_sql(&tags_json)
    );
    state
        .db
        .execute(Statement::from_string(state.db.get_database_backend(), sql))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": id,
        "name": name,
        "status": "pending",
    })))
}

/// Start a workstation (creates and starts a Docker container).
pub async fn start_workstation(
    State(state): State<AppState>,
    Path(ws_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!("SELECT id FROM workstations WHERE id = '{}'", escape_sql(&ws_id)),
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
                "UPDATE workstations SET status = 'creating' WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let container_name = format!("evershade-ws-{}", &ws_id[..8.min(ws_id.len())]);

    match run_docker(
        &[
            "create",
            "--name",
            &container_name,
            "python:3.12-slim",
            "tail",
            "-f",
            "/dev/null",
        ],
        30,
    )
    .await
    {
        Ok((0, stdout, _)) => {
            let container_id = stdout.trim().chars().take(12).collect::<String>();
            let _ = run_docker(&["start", &container_name], 15).await;
            let now = now_iso();
            state
                .db
                .execute(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "UPDATE workstations SET status = 'running', container_id = '{}', \
                     container_name = '{}', started_at = '{}' WHERE id = '{}'",
                        escape_sql(&container_id),
                        escape_sql(&container_name),
                        now,
                        escape_sql(&ws_id)
                    ),
                ))
                .await
                .ok();

            Ok(Json(serde_json::json!({
                "id": ws_id,
                "status": "running",
                "container_id": container_id,
            })))
        }
        Ok((_code, _stdout, stderr)) => {
            tracing::error!(
                "Failed to start workstation {}: {}",
                ws_id,
                stderr
            );
            state
                .db
                .execute(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "UPDATE workstations SET status = 'error', error = '{}' WHERE id = '{}'",
                        "Failed to start container",
                        escape_sql(&ws_id)
                    ),
                ))
                .await
                .ok();
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
        Err(e) => {
            tracing::error!(
                "Failed to start workstation {}: {}",
                ws_id,
                e
            );
            state
                .db
                .execute(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "UPDATE workstations SET status = 'error', error = '{}' WHERE id = '{}'",
                        "Failed to start container",
                        escape_sql(&ws_id)
                    ),
                ))
                .await
                .ok();
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// Stop a workstation.
pub async fn stop_workstation(
    State(state): State<AppState>,
    Path(ws_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT container_name FROM workstations WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match existing {
        Some(r) => {
            let container_name: String = r.try_get_by_index(0).unwrap_or_default();
            if !container_name.is_empty() {
                if validate_container_name(&container_name).is_ok() {
                    let _ = run_docker(&["stop", &container_name], 30).await;
                }
            }
        }
        None => return Err(StatusCode::NOT_FOUND),
    }

    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "UPDATE workstations SET status = 'stopped' WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": ws_id,
        "status": "stopped",
    })))
}

/// Destroy a workstation.
pub async fn destroy_workstation(
    State(state): State<AppState>,
    Path(ws_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT container_name FROM workstations WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match existing {
        Some(r) => {
            let container_name: String = r.try_get_by_index(0).unwrap_or_default();
            if !container_name.is_empty() {
                if validate_container_name(&container_name).is_ok() {
                    let _ = run_docker(&["rm", "-f", &container_name], 30).await;
                }
            }
        }
        None => return Err(StatusCode::NOT_FOUND),
    }

    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "UPDATE workstations SET status = 'destroyed' WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "id": ws_id,
        "status": "destroyed",
    })))
}

#[derive(Deserialize)]
struct WorkstationLogsQuery {
    #[serde(default = "default_tail")]
    tail: i64,
}
fn default_tail() -> i64 {
    100
}

/// Get workstation logs.
pub async fn get_workstation_logs(
    State(state): State<AppState>,
    Path(ws_id): Path<String>,
    Query(params): Query<WorkstationLogsQuery>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let existing = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT container_name FROM workstations WHERE id = '{}'",
                escape_sql(&ws_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match existing {
        Some(r) => {
            let container_name: String = r.try_get_by_index(0).unwrap_or_default();
            if container_name.is_empty() {
                return Ok(Json(serde_json::json!({"logs": "No container attached"})));
            }
            if validate_container_name(&container_name).is_err() {
                return Err(StatusCode::BAD_REQUEST);
            }
            match run_docker(
                &[
                    "logs",
                    "--tail",
                    &params.tail.to_string(),
                    &container_name,
                ],
                10,
            )
            .await
            {
                Ok((_code, stdout, stderr)) => {
                    Ok(Json(serde_json::json!({"logs": format!("{}{}", stdout, stderr)})))
                }
                Err(_) => Ok(Json(serde_json::json!({"logs": "Docker not available"}))),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}
