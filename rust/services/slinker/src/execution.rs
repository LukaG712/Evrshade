//! Execution routes for Slinker — task CRUD and adapter operations.

use axum::{Json, extract::Path, extract::State, http::StatusCode};
use sea_orm::{ConnectionTrait, DatabaseConnection, Statement};
use std::collections::HashMap;

use crate::{
    AppState,
    adapters::{
        AdapterTrait, ExecutionRequest, JunieAdapter, SubprocessAdapter,
        escape_sql, gen_id, now_iso,
    },
};

/// Validate workspace path is within allowed directories.
fn validate_workspace_path(workspace_path: &str) -> Result<String, StatusCode> {
    let allowed_bases: Vec<&str> = vec![
        "/tmp/workspace",
        "/workspace",
        "/data/workspace",
        std::env::var("WORKSPACE_BASE")
            .unwrap_or_else(|_| "/tmp/workspace".to_string())
            .as_str(),
    ];

    let path = if workspace_path.is_empty() {
        "/tmp/workspace".to_string()
    } else {
        workspace_path.to_string()
    };

    for base in &allowed_bases {
        if path.starts_with(base) {
            return Ok(path);
        }
    }

    Err(StatusCode::BAD_REQUEST)
}

/// Create a new execution task.
pub async fn create_task(
    State(state): State<AppState>,
    Json(body): Json<serde_json::Value>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let task_id = gen_id();
    let session_id = gen_id();
    let now = now_iso();

    let title = body
        .get("title")
        .and_then(|v| v.as_str())
        .unwrap_or("Untitled task")
        .to_string();
    let description = body
        .get("description")
        .and_then(|v| v.as_str())
        .unwrap_or("")
        .to_string();
    let adapter_name = body
        .get("adapter")
        .and_then(|v| v.as_str())
        .unwrap_or("subprocess")
        .to_string();
    let workspace_path = body
        .get("workspace_path")
        .and_then(|v| v.as_str())
        .unwrap_or("/tmp/workspace")
        .to_string();
    let timeout = body.get("timeout").and_then(|v| v.as_u64()).unwrap_or(300);
    let commands = body
        .get("commands")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(|s| s.to_string()))
                .collect::<Vec<_>>()
        });
    let metadata = body
        .get("metadata")
        .cloned()
        .unwrap_or_else(|| serde_json::Value::Object(serde_json::Map::new()));

    let workspace_path = match validate_workspace_path(&workspace_path) {
        Ok(p) => p,
        Err(_) => return Err(StatusCode::BAD_REQUEST),
    };

    let workspace_id = gen_id();
    let ws_name = std::path::Path::new(&workspace_path)
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "workspace".to_string());

    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT OR IGNORE INTO workspaces (id, name, path, status, created_at, updated_at) \
                 VALUES ('{}', '{}', '{}', 'active', '{}', '{}')",
                workspace_id,
                escape_sql(&ws_name),
                escape_sql(&workspace_path),
                now,
                now
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let metadata_str =
        serde_json::to_string(&metadata).unwrap_or_else(|_| "{}".to_string());
    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT INTO execution_sessions (id, task_id, adapter, workspace_id, status, \
                 metadata, created_at, updated_at) \
                 VALUES ('{}', '{}', '{}', '{}', 'running', '{}', '{}', '{}')",
                session_id,
                task_id,
                escape_sql(&adapter_name),
                workspace_id,
                escape_sql(&metadata_str),
                now,
                now
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    state
        .db
        .execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT OR IGNORE INTO tasks (id, name, description, status, created_at, updated_at) \
                 VALUES ('{}', '{}', '{}', 'running', '{}', '{}')",
                task_id,
                escape_sql(&title),
                escape_sql(&description),
                now,
                now
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let exec_request = ExecutionRequest {
        title,
        description,
        workspace_path,
        files: None,
        commands,
        timeout,
        permissions: serde_json::Value::Object(serde_json::Map::new()),
        metadata,
    };

    let db_clone = state.db.clone();
    let task_id_clone = task_id.clone();
    let session_id_clone = session_id.clone();
    tokio::spawn(async move {
        let adapter: Box<dyn AdapterTrait + Send + Sync> = if adapter_name == "junie" {
            Box::new(JunieAdapter::new())
        } else {
            Box::new(SubprocessAdapter::new())
        };

        let result = adapter.execute(&exec_request).await;
        let now = now_iso();

        let output_truncated = result.output.chars().take(50000).collect::<String>();
        let error_truncated = result
            .error
            .as_ref()
            .map(|e| e.chars().take(5000).collect::<String>());

        let _ = db_clone
            .execute(Statement::from_string(
                db_clone.get_database_backend(),
                format!(
                    "UPDATE execution_sessions SET status = '{}', output = '{}', error = '{}', \
                     exit_code = {}, duration_ms = {}, completed_at = '{}', updated_at = '{}' \
                     WHERE id = '{}'",
                    escape_sql(&result.status),
                    escape_sql(&output_truncated),
                    escape_sql(&error_truncated.unwrap_or_default()),
                    result.exit_code,
                    result.duration_ms,
                    now,
                    now,
                    session_id_clone
                ),
            ))
            .await;

        let _ = db_clone
            .execute(Statement::from_string(
                db_clone.get_database_backend(),
                format!(
                    "UPDATE tasks SET status = '{}', output = '{}', error = '{}', \
                     exit_code = {}, completed_at = '{}', updated_at = '{}' WHERE id = '{}'",
                    escape_sql(&result.status),
                    escape_sql(&output_truncated),
                    escape_sql(&error_truncated.unwrap_or_default()),
                    result.exit_code,
                    now,
                    now,
                    task_id_clone
                ),
            ))
            .await;
    });

    Ok(Json(serde_json::json!({
        "id": task_id,
        "title": exec_request.title,
        "status": "running",
        "adapter": adapter_name,
        "workspace": exec_request.workspace_path,
        "created_at": now,
    })))
}

/// Get a task by ID.
pub async fn get_task(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let session = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT * FROM execution_sessions WHERE task_id = '{}' ORDER BY created_at DESC",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if let Some(r) = session {
        let mut result: HashMap<String, serde_json::Value> = HashMap::new();
        result.insert(
            "id".to_string(),
            serde_json::Value::String(r.try_get_by_index(0).unwrap_or_default()),
        );
        result.insert(
            "task_id".to_string(),
            serde_json::Value::String(r.try_get_by_index(1).unwrap_or_default()),
        );
        result.insert(
            "adapter".to_string(),
            serde_json::Value::String(r.try_get_by_index(2).unwrap_or_default()),
        );
        result.insert(
            "workspace_id".to_string(),
            serde_json::Value::String(r.try_get_by_index(3).unwrap_or_default()),
        );
        result.insert(
            "status".to_string(),
            serde_json::Value::String(r.try_get_by_index(4).unwrap_or_default()),
        );
        result.insert(
            "output".to_string(),
            serde_json::Value::String(r.try_get_by_index::<String>(5).unwrap_or_default()),
        );
        result.insert(
            "error".to_string(),
            serde_json::Value::String(r.try_get_by_index::<String>(6).unwrap_or_default()),
        );
        result.insert(
            "exit_code".to_string(),
            serde_json::Value::Number(r.try_get_by_index::<i64>(7).unwrap_or(0).into()),
        );
        result.insert(
            "duration_ms".to_string(),
            serde_json::Value::Number(r.try_get_by_index::<i64>(8).unwrap_or(0).into()),
        );
        result.insert(
            "metadata".to_string(),
            serde_json::from_str(&r.try_get_by_index::<String>(9).unwrap_or_else(|_| "{}".to_string()))
                .unwrap_or_default(),
        );
        result.insert(
            "created_at".to_string(),
            serde_json::Value::String(r.try_get_by_index(10).unwrap_or_default()),
        );
        result.insert(
            "updated_at".to_string(),
            serde_json::Value::String(r.try_get_by_index(11).unwrap_or_default()),
        );
        result.insert(
            "completed_at".to_string(),
            serde_json::Value::String(r.try_get_by_index::<String>(12).unwrap_or_default()),
        );

        let session_id: String = r.try_get_by_index(0).unwrap_or_default();
        let changes = state
            .db
            .query(Statement::from_string(
                state.db.get_database_backend(),
                format!(
                    "SELECT * FROM file_changes WHERE session_id = '{}' ORDER BY created_at",
                    escape_sql(&session_id)
                ),
            ))
            .await
            .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

        let file_changes: Vec<serde_json::Value> = changes
            .iter()
            .filter_map(|c| {
                Some(serde_json::json!({
                    "id": c.try_get_by_index::<String>(0).ok()?,
                    "path": c.try_get_by_index::<String>(1).ok()?,
                    "action": c.try_get_by_index::<String>(2).ok()?,
                    "diff": c.try_get_by_index::<String>(3).ok(),
                    "created_at": c.try_get_by_index::<String>(4).ok()?,
                }))
            })
            .collect();
        result.insert(
            "file_changes".to_string(),
            serde_json::Value::Array(file_changes),
        );

        return Ok(Json(serde_json::Value::Object(
            result.into_iter().collect(),
        )));
    }

    let task = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!("SELECT * FROM tasks WHERE id = '{}'", escape_sql(&task_id)),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match task {
        Some(r) => {
            let mut result: HashMap<String, serde_json::Value> = HashMap::new();
            result.insert(
                "id".to_string(),
                serde_json::Value::String(r.try_get_by_index(0).unwrap_or_default()),
            );
            result.insert(
                "name".to_string(),
                serde_json::Value::String(r.try_get_by_index(1).unwrap_or_default()),
            );
            result.insert(
                "description".to_string(),
                serde_json::Value::String(r.try_get_by_index(2).unwrap_or_default()),
            );
            result.insert(
                "status".to_string(),
                serde_json::Value::String(r.try_get_by_index(5).unwrap_or_default()),
            );
            result.insert(
                "output".to_string(),
                serde_json::Value::String(r.try_get_by_index(7).unwrap_or_default()),
            );
            result.insert(
                "error".to_string(),
                serde_json::Value::String(r.try_get_by_index(8).unwrap_or_default()),
            );
            result.insert(
                "created_at".to_string(),
                serde_json::Value::String(r.try_get_by_index(13).unwrap_or_default()),
            );
            Ok(Json(serde_json::Value::Object(
                result.into_iter().collect(),
            )))
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// List recent tasks.
pub async fn list_tasks(
    State(state): State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, StatusCode> {
    let rows = state
        .db
        .query(Statement::from_string(
            state.db.get_database_backend(),
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 50".to_string(),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let tasks: Vec<serde_json::Value> = rows
        .iter()
        .filter_map(|r| {
            Some(serde_json::json!({
                "id": r.try_get_by_index::<String>(0).ok()?,
                "name": r.try_get_by_index::<String>(1).ok()?,
                "status": r.try_get_by_index::<String>(5).ok()?,
                "created_at": r.try_get_by_index::<String>(13).ok()?,
            }))
        })
        .collect();

    Ok(Json(tasks))
}

/// Cancel a running task.
pub async fn cancel_task(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let task = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT status FROM tasks WHERE id = '{}'",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match task {
        Some(r) => {
            let status: String = r.try_get_by_index(0).unwrap_or_default();
            if status != "running" && status != "pending" {
                return Err(StatusCode::BAD_REQUEST);
            }
            let now = now_iso();
            state
                .db
                .execute(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "UPDATE tasks SET status = 'cancelled', completed_at = '{}', \
                     updated_at = '{}' WHERE id = '{}'",
                        now,
                        now,
                        escape_sql(&task_id)
                    ),
                ))
                .await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
        }
        None => return Err(StatusCode::NOT_FOUND),
    }

    Ok(Json(serde_json::json!({
        "task_id": task_id,
        "cancelled": true,
    })))
}

/// List available adapters.
pub async fn list_adapters_handler() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "adapters": {
            "subprocess": {"name": "subprocess", "class": "SubprocessAdapter", "available": true},
            "junie": {"name": "junie", "class": "JunieAdapter", "available": true},
        }
    }))
}

/// Run tests for a task's workspace.
pub async fn run_tests_handler(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let session = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT workspace_id, adapter FROM execution_sessions WHERE task_id = '{}' \
                 ORDER BY created_at DESC",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match session {
        Some(r) => {
            let workspace_id: String = r.try_get_by_index(0).unwrap_or_default();
            let adapter_name: String = r.try_get_by_index(1).unwrap_or_default();

            let workspace = state
                .db
                .query_one(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "SELECT path FROM workspaces WHERE id = '{}'",
                        escape_sql(&workspace_id)
                    ),
                ))
                .await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

            match workspace {
                Some(ws) => {
                    let path: String = ws.try_get_by_index(0).unwrap_or_default();
                    let adapter: Box<dyn AdapterTrait + Send + Sync> =
                        if adapter_name == "junie" {
                            Box::new(JunieAdapter::new())
                        } else {
                            Box::new(SubprocessAdapter::new())
                        };
                    let result = adapter.run_tests(&path, None).await;
                    Ok(Json(serde_json::json!({
                        "task_id": task_id,
                        "tests": result,
                    })))
                }
                None => Err(StatusCode::BAD_REQUEST),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// Run lint for a task's workspace.
pub async fn run_lint_handler(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let session = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT workspace_id, adapter FROM execution_sessions WHERE task_id = '{}' \
                 ORDER BY created_at DESC",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match session {
        Some(r) => {
            let workspace_id: String = r.try_get_by_index(0).unwrap_or_default();
            let adapter_name: String = r.try_get_by_index(1).unwrap_or_default();

            let workspace = state
                .db
                .query_one(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "SELECT path FROM workspaces WHERE id = '{}'",
                        escape_sql(&workspace_id)
                    ),
                ))
                .await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

            match workspace {
                Some(ws) => {
                    let path: String = ws.try_get_by_index(0).unwrap_or_default();
                    let adapter: Box<dyn AdapterTrait + Send + Sync> =
                        if adapter_name == "junie" {
                            Box::new(JunieAdapter::new())
                        } else {
                            Box::new(SubprocessAdapter::new())
                        };
                    let result = adapter.run_lint(&path, None).await;
                    Ok(Json(serde_json::json!({
                        "task_id": task_id,
                        "lint": result,
                    })))
                }
                None => Err(StatusCode::BAD_REQUEST),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// Run build for a task's workspace.
pub async fn run_build_handler(
    State(state): State<AppState>,
    Path(task_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let session = state
        .db
        .query_one(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "SELECT workspace_id, adapter FROM execution_sessions WHERE task_id = '{}' \
                 ORDER BY created_at DESC",
                escape_sql(&task_id)
            ),
        ))
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    match session {
        Some(r) => {
            let workspace_id: String = r.try_get_by_index(0).unwrap_or_default();
            let adapter_name: String = r.try_get_by_index(1).unwrap_or_default();

            let workspace = state
                .db
                .query_one(Statement::from_string(
                    state.db.get_database_backend(),
                    format!(
                        "SELECT path FROM workspaces WHERE id = '{}'",
                        escape_sql(&workspace_id)
                    ),
                ))
                .await
                .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

            match workspace {
                Some(ws) => {
                    let path: String = ws.try_get_by_index(0).unwrap_or_default();
                    let adapter: Box<dyn AdapterTrait + Send + Sync> =
                        if adapter_name == "junie" {
                            Box::new(JunieAdapter::new())
                        } else {
                            Box::new(SubprocessAdapter::new())
                        };
                    let result = adapter.run_build(&path, None).await;
                    Ok(Json(serde_json::json!({
                        "task_id": task_id,
                        "build": result,
                    })))
                }
                None => Err(StatusCode::BAD_REQUEST),
            }
        }
        None => Err(StatusCode::NOT_FOUND),
    }
}
