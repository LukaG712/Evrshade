//! Task management routes for Greenie.

use axum::{extract::Path, extract::State, http::StatusCode, Json};
use sea_orm::{ConnectionTrait, Statement};

use crate::{models::*, AppState};

/// Create a new task.
pub async fn create_task(
    State(state): State<AppState>,
    Json(body): Json<TaskCreate>,
) -> Result<Json<TaskResponse>, StatusCode> {
    let id = gen_id();
    let now = now_iso();
    let payload_json = serde_json::to_string(&body.payload).unwrap_or_else(|_| "{}".to_string());
    let sql = format!(
        "INSERT INTO tasks (id, mission_id, name, description, type, payload, created_at, updated_at) \
         VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')",
        id,
        escape_sql(&body.mission_id),
        escape_sql(&body.name),
        escape_sql(&body.description),
        escape_sql(&body.task_type),
        escape_sql(&payload_json),
        now,
        now,
    );
    state
        .db
        .execute(Statement::from_string(state.db.get_database_backend(), sql))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, mission_id, name, description, type, status, payload, result, error, \
                 assigned_to, started_at, completed_at, created_at, updated_at \
                 FROM tasks WHERE id = '{}'",
                id
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(TaskResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            mission_id: r.try_get_by_index(1).unwrap_or_default(),
            name: r.try_get_by_index(2).unwrap_or_default(),
            description: r.try_get_by_index(3).unwrap_or_default(),
            task_type: r.try_get_by_index(4).unwrap_or_default(),
            status: r.try_get_by_index(5).unwrap_or_default(),
            payload: serde_json::from_str(
                &r.try_get_by_index::<String>(6)
                    .unwrap_or_else(|_| "{}".to_string()),
            )
            .unwrap_or_default(),
            result: r.try_get_by_index(7).unwrap_or_default(),
            error: r.try_get_by_index(8).unwrap_or_default(),
            assigned_to: r.try_get_by_index(9).unwrap_or_default(),
            started_at: r.try_get_by_index(10).ok(),
            completed_at: r.try_get_by_index(11).ok(),
            created_at: r.try_get_by_index(12).unwrap_or_default(),
            updated_at: r.try_get_by_index(13).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// List all tasks.
pub async fn list_tasks(
    State(state): State<AppState>,
) -> Result<Json<Vec<TaskResponse>>, StatusCode> {
    let rows = state
        .db
        .query(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, mission_id, name, description, type, status, payload, result, error, \
             assigned_to, started_at, completed_at, created_at, updated_at \
             FROM tasks ORDER BY created_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let tasks = rows
        .iter()
        .filter_map(|r| {
            Some(TaskResponse {
                id: r.try_get_by_index(0).ok()?,
                mission_id: r.try_get_by_index(1).ok()?,
                name: r.try_get_by_index(2).ok()?,
                description: r.try_get_by_index(3).ok()?,
                task_type: r.try_get_by_index(4).ok()?,
                status: r.try_get_by_index(5).ok()?,
                payload: serde_json::from_str(
                    &r.try_get_by_index::<String>(6)
                        .unwrap_or_else(|_| "{}".to_string()),
                )
                .unwrap_or_default(),
                result: r.try_get_by_index(7).ok()?,
                error: r.try_get_by_index(8).ok()?,
                assigned_to: r.try_get_by_index(9).ok()?,
                started_at: r.try_get_by_index(10).ok(),
                completed_at: r.try_get_by_index(11).ok(),
                created_at: r.try_get_by_index(12).ok()?,
                updated_at: r.try_get_by_index(13).ok()?,
            })
        })
        .collect();

    Ok(Json(tasks))
}

/// Get a task by ID.
pub async fn get_task(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<TaskResponse>, StatusCode> {
    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, mission_id, name, description, type, status, payload, result, error, \
                 assigned_to, started_at, completed_at, created_at, updated_at \
                 FROM tasks WHERE id = '{}'",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(TaskResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            mission_id: r.try_get_by_index(1).unwrap_or_default(),
            name: r.try_get_by_index(2).unwrap_or_default(),
            description: r.try_get_by_index(3).unwrap_or_default(),
            task_type: r.try_get_by_index(4).unwrap_or_default(),
            status: r.try_get_by_index(5).unwrap_or_default(),
            payload: serde_json::from_str(
                &r.try_get_by_index::<String>(6)
                    .unwrap_or_else(|_| "{}".to_string()),
            )
            .unwrap_or_default(),
            result: r.try_get_by_index(7).unwrap_or_default(),
            error: r.try_get_by_index(8).unwrap_or_default(),
            assigned_to: r.try_get_by_index(9).unwrap_or_default(),
            started_at: r.try_get_by_index(10).ok(),
            completed_at: r.try_get_by_index(11).ok(),
            created_at: r.try_get_by_index(12).unwrap_or_default(),
            updated_at: r.try_get_by_index(13).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// Start a task.
pub async fn start_task(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<TaskResponse>, StatusCode> {
    let now = now_iso();
    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "UPDATE tasks SET status = 'running', started_at = '{}', updated_at = '{}' \
                 WHERE id = '{}'",
                now,
                now,
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, mission_id, name, description, type, status, payload, result, error, \
                 assigned_to, started_at, completed_at, created_at, updated_at \
                 FROM tasks WHERE id = '{}'",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(TaskResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            mission_id: r.try_get_by_index(1).unwrap_or_default(),
            name: r.try_get_by_index(2).unwrap_or_default(),
            description: r.try_get_by_index(3).unwrap_or_default(),
            task_type: r.try_get_by_index(4).unwrap_or_default(),
            status: r.try_get_by_index(5).unwrap_or_default(),
            payload: serde_json::from_str(
                &r.try_get_by_index::<String>(6)
                    .unwrap_or_else(|_| "{}".to_string()),
            )
            .unwrap_or_default(),
            result: r.try_get_by_index(7).unwrap_or_default(),
            error: r.try_get_by_index(8).unwrap_or_default(),
            assigned_to: r.try_get_by_index(9).unwrap_or_default(),
            started_at: r.try_get_by_index(10).ok(),
            completed_at: r.try_get_by_index(11).ok(),
            created_at: r.try_get_by_index(12).unwrap_or_default(),
            updated_at: r.try_get_by_index(13).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// Delete a task.
pub async fn delete_task(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<StatusCode, StatusCode> {
    let result = state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!("DELETE FROM tasks WHERE id = '{}'", escape_sql(&task_id)),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if result.rows_affected() > 0 {
        Ok(StatusCode::NO_CONTENT)
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}
