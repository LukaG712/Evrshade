//! Database utilities for Evershade services.
//!
//! Provides SQLite connection pool initialization with WAL mode
//! and migration helpers using SeaORM.

use sea_orm::{Database, DatabaseConnection, ConnectionTrait, Statement};
use tracing::info;

/// Initialize a SeaORM database connection with SQLite WAL mode.
pub async fn init_db(db_url: &str) -> Result<DatabaseConnection, sea_orm::DbErr> {
    // Ensure the directory for the database file exists
    if let Some(pos) = db_url.rfind('/') {
        let dir = &db_url[..pos];
        if !dir.is_empty() && dir != "sqlite:" {
            std::fs::create_dir_all(dir).ok();
        }
    }

    let db = Database::connect(db_url).await?;

    // Enable WAL mode and optimal SQLite settings
    db.execute(Statement::from_string(
        db.get_database_backend(),
        "PRAGMA journal_mode=WAL".to_string(),
    ))
    .await
    .ok();

    db.execute(Statement::from_string(
        db.get_database_backend(),
        "PRAGMA synchronous=NORMAL".to_string(),
    ))
    .await
    .ok();

    db.execute(Statement::from_string(
        db.get_database_backend(),
        "PRAGMA cache_size=-64000".to_string(),
    ))
    .await
    .ok();

    db.execute(Statement::from_string(
        db.get_database_backend(),
        "PRAGMA foreign_keys=ON".to_string(),
    ))
    .await
    .ok();

    info!("Database connected: {}", db_url);
    Ok(db)
}

/// Execute a SQL script to create tables.
pub async fn execute_script(db: &DatabaseConnection, sql: &str) -> Result<(), sea_orm::DbErr> {
    db.execute(Statement::from_string(
        db.get_database_backend(),
        sql.to_string(),
    ))
    .await?;
    Ok(())
}

/// Ensure the directory for a database file exists.
pub fn ensure_db_path(db_path: &str) -> String {
    if let Some(pos) = db_path.rfind('/') {
        let dir = &db_path[..pos];
        if !dir.is_empty() {
            std::fs::create_dir_all(dir).ok();
        }
    }
    db_path.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ensure_db_path() {
        let path = ensure_db_path("./data/app.db");
        assert_eq!(path, "./data/app.db");
    }
}
