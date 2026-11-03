//! Agent management routes for Greenie.

use axum::{Json, extract::Path, extract::State, http::StatusCode};
use sea_orm::{ConnectionTrait, Statement};

use crate::{AppState, models::*};

/// Create a new agent.
pub async fn create_agent(
    State(state): State<AppState>,
    Json(body): Json<AgentCreate>,
) -> Result<Json<AgentResponse>, StatusCode> {
    let id = gen_id();
    let now = now_iso();
    let sql = format!(
        "INSERT INTO agents (id, name, description, model, system_prompt, created_at, updated_at) \
         VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')",
        id,
        escape_sql(&body.name),
        escape_sql(&body.description),
        escape_sql(&body.model),
        escape_sql(&body.system_prompt),
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
                "SELECT id, name, description, model, system_prompt, status, metadata, created_at, updated_at \
                 FROM agents WHERE id = '{}'",
                id
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| Json(AgentResponse {
        id: r.try_get_by_index(0).unwrap_or_default(),
        name: r.try_get_by_index(1).unwrap_or_default(),
        description: r.try_get_by_index(2).unwrap_or_default(),
        model: r.try_get_by_index(3).unwrap_or_default(),
        system_prompt: r.try_get_by_index(4).unwrap_or_default(),
        status: r.try_get_by_index(5).unwrap_or_default(),
        metadata: serde_json::from_str(&r.try_get_by_index::<String>(6).unwrap_or_else(|_| "{}".to_string()))
            .unwrap_or_default(),
        created_at: r.try_get_by_index(7).unwrap_or_default(),
        updated_at: r.try_get_by_index(8).unwrap_or_default(),
    }))
    .ok_or(StatusCode::NOT_FOUND)
}

/// List all agents.
pub async fn list_agents(
    State(state): State<AppState>,
) -> Result<Json<Vec<AgentResponse>>, StatusCode> {
    let rows = state
        .db
        .query(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT id, name, description, model, system_prompt, status, metadata, created_at, updated_at \
             FROM agents ORDER BY created_at DESC"
                .to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let agents = rows
        .iter()
        .filter_map(|r| {
            Some(AgentResponse {
                id: r.try_get_by_index(0).ok()?,
                name: r.try_get_by_index(1).ok()?,
                description: r.try_get_by_index(2).ok()?,
                model: r.try_get_by_index(3).ok()?,
                system_prompt: r.try_get_by_index(4).ok()?,
                status: r.try_get_by_index(5).ok()?,
                metadata: serde_json::from_str(&r.try_get_by_index::<String>(6).unwrap_or_else(|_| "{}".to_string()))
                    .unwrap_or_default(),
                created_at: r.try_get_by_index(7).ok()?,
                updated_at: r.try_get_by_index(8).ok()?,
            })
        })
        .collect();

    Ok(Json(agents))
}

/// Get an agent by ID.
pub async fn get_agent(
    State(state): State<AppState>,
    Path(agent_id): Path<String>,
) -> Result<Json<AgentResponse>, StatusCode> {
    let row = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT id, name, description, model, system_prompt, status, metadata, created_at, updated_at \
                 FROM agents WHERE id = '{}'",
                escape_sql(&agent_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    row.map(|r| Json(AgentResponse {
        id: r.try_get_by_index(0).unwrap_or_default(),
        name: r.try_get_by_index(1).unwrap_or_default(),
        description: r.try_get_by_index(2).unwrap_or_default(),
        model: r.try_get_by_index(3).unwrap_or_default(),
        system_prompt: r.try_get_by_index(4).unwrap_or_default(),
        status: r.try_get_by_index(5).unwrap_or_default(),
        metadata: serde_json::from_str(&r.try_get_by_index::<String>(6).unwrap_or_else(|_| "{}".to_string()))
            .unwrap_or_default(),
        created_at: r.try_get_by_index(7).unwrap_or_default(),
        updated_at: r.try_get_by_index(8).unwrap_or_default(),
    }))
    .ok_or(StatusCode::NOT_FOUND)
}

/// Delete an agent.
pub async fn delete_agent(
    State(state): State<AppState>,
    Path(agent_id): Path<String>,
) -> Result<StatusCode, StatusCode> {
    let result = state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!("DELETE FROM agents WHERE id = '{}'", escape_sql(&agent_id)),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if result.rows_affected() > 0 {
        Ok(StatusCode::NO_CONTENT)
    } else {
        Err(StatusCode::NOT_FOUND)
    }
}
