//! Mission management routes for Greenie.

use axum::{extract::Path, extract::State, http::StatusCode, Json};
use sea_orm::{ConnectionTrait, Statement};

use crate::{models::*, AppState};

/// Create a new mission.
pub async fn create_mission(
    State(state): State<AppState>,
    Json(body): Json<MissionCreate>,
) -> Result<Json<MissionResponse>, StatusCode> {
    let id = gen_id();
    let now = now_iso();
    let sql = format!(
        "INSERT INTO missions (id, name, description, agent_id, created_at, updated_at) \
         VALUES ('{}', '{}', '{}', '{}', '{}', '{}')",
        id,
        escape_sql(&body.name),
        escape_sql(&body.description),
        escape_sql(&body.agent_id),
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
                "SELECT id, name, description, agent_id, status, progress, result, error, \
                 started_at, completed_at, created_at, updated_at \
                 FROM missions WHERE id = '{}'",
                id
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(MissionResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            name: r.try_get_by_index(1).unwrap_or_default(),
            description: r.try_get_by_index(2).unwrap_or_default(),
            agent_id: r.try_get_by_index(3).unwrap_or_default(),
            status: r.try_get_by_index(4).unwrap_or_default(),
            progress: r.try_get_by_index(5).unwrap_or_default(),
            result: r.try_get_by_index(6).unwrap_or_default(),
            error: r.try_get_by_index(7).unwrap_or_default(),
            started_at: r.try_get_by_index(8).ok(),
            completed_at: r.try_get_by_index(9).ok(),
            created_at: r.try_get_by_index(10).unwrap_or_default(),
            updated_at: r.try_get_by_index(11).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// List all missions.
pub async fn list_missions(
    State(state): State<AppState>,
) -> Result<Json<Vec<MissionResponse>>, StatusCode> {
    let rows = state
        .db
        .query(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, name, description, agent_id, status, progress, result, error, \
             started_at, completed_at, created_at, updated_at \
             FROM missions ORDER BY created_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let missions = rows
        .iter()
        .filter_map(|r| {
            Some(MissionResponse {
                id: r.try_get_by_index(0).ok()?,
                name: r.try_get_by_index(1).ok()?,
                description: r.try_get_by_index(2).ok()?,
                agent_id: r.try_get_by_index(3).ok()?,
                status: r.try_get_by_index(4).ok()?,
                progress: r.try_get_by_index(5).ok()?,
                result: r.try_get_by_index(6).ok()?,
                error: r.try_get_by_index(7).ok()?,
                started_at: r.try_get_by_index(8).ok(),
                completed_at: r.try_get_by_index(9).ok(),
                created_at: r.try_get_by_index(10).ok()?,
                updated_at: r.try_get_by_index(11).ok()?,
            })
        })
        .collect();

    Ok(Json(missions))
}

/// Get a mission by ID.
pub async fn get_mission(
    State(state): State<AppState>,
    Path(mission_id): Path<String>,
) -> Result<Json<MissionResponse>, StatusCode> {
    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, name, description, agent_id, status, progress, result, error, \
                 started_at, completed_at, created_at, updated_at \
                 FROM missions WHERE id = '{}'",
                escape_sql(&mission_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(MissionResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            name: r.try_get_by_index(1).unwrap_or_default(),
            description: r.try_get_by_index(2).unwrap_or_default(),
            agent_id: r.try_get_by_index(3).unwrap_or_default(),
            status: r.try_get_by_index(4).unwrap_or_default(),
            progress: r.try_get_by_index(5).unwrap_or_default(),
            result: r.try_get_by_index(6).unwrap_or_default(),
            error: r.try_get_by_index(7).unwrap_or_default(),
            started_at: r.try_get_by_index(8).ok(),
            completed_at: r.try_get_by_index(9).ok(),
            created_at: r.try_get_by_index(10).unwrap_or_default(),
            updated_at: r.try_get_by_index(11).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// Start a mission.
pub async fn start_mission(
    State(state): State<AppState>,
    Path(mission_id): Path<String>,
) -> Result<Json<MissionResponse>, StatusCode> {
    let now = now_iso();
    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "UPDATE missions SET status = 'running', started_at = '{}', updated_at = '{}' \
                 WHERE id = '{}'",
                now,
                now,
                escape_sql(&mission_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, name, description, agent_id, status, progress, result, error, \
                 started_at, completed_at, created_at, updated_at \
                 FROM missions WHERE id = '{}'",
                escape_sql(&mission_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| {
        Json(MissionResponse {
            id: r.try_get_by_index(0).unwrap_or_default(),
            name: r.try_get_by_index(1).unwrap_or_default(),
            description: r.try_get_by_index(2).unwrap_or_default(),
            agent_id: r.try_get_by_index(3).unwrap_or_default(),
            status: r.try_get_by_index(4).unwrap_or_default(),
            progress: r.try_get_by_index(5).unwrap_or_default(),
            result: r.try_get_by_index(6).unwrap_or_default(),
            error: r.try_get_by_index(7).unwrap_or_default(),
            started_at: r.try_get_by_index(8).ok(),
            completed_at: r.try_get_by_index(9).ok(),
            created_at: r.try_get_by_index(10).unwrap_or_default(),
            updated_at: r.try_get_by_index(11).unwrap_or_default(),
        })
    })
    .ok_or(StatusCode::NOT_FOUND)
}

/// Delete a mission.
pub async fn delete_mission(
    State(state): State<AppState>,
    Path(mission_id): Path<String>,
) -> Result<StatusCode, StatusCode> {
    let result = state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "DELETE FROM missions WHERE id = '{}'",
                escape_sql(&mission_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if result.rows_affected() > 0 {
        Ok(StatusCode::NO_CONTENT)
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}
