//! Adapter trait and shared types for Slinker execution backends.

use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub mod junie;
pub mod subprocess;

pub use junie::JunieAdapter;
pub use subprocess::SubprocessAdapter;

/// Generate a new UUID string.
pub fn gen_id() -> String {
    Uuid::new_v4().to_string()
}

/// Return the current UTC time in ISO 8601 format.
pub fn now_iso() -> String {
    chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string()
}

/// Escape single quotes in SQL strings.
pub fn escape_sql(s: &str) -> String {
    s.replace('\'', "''")
}

// ─── Data Models ───────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileChange {
    pub path: String,
    pub action: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub diff: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionResult {
    pub task_id: String,
    pub status: String,
    pub output: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    pub exit_code: i32,
    pub file_changes: Vec<FileChange>,
    pub duration_ms: i64,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ExecutionRequest {
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub description: String,
    #[serde(default = "default_workspace")]
    pub workspace_path: String,
    #[serde(default)]
    #[allow(dead_code)]
    pub files: Option<Vec<String>>,
    #[serde(default)]
    pub commands: Option<Vec<String>>,
    #[serde(default = "default_timeout")]
    pub timeout: u64,
    #[serde(default)]
    #[allow(dead_code)]
    pub permissions: serde_json::Value,
    #[serde(default)]
    #[allow(dead_code)]
    pub metadata: serde_json::Value,
}

fn default_workspace() -> String {
    "/tmp/workspace".to_string()
}

fn default_timeout() -> u64 {
    300
}

// ─── Adapter Trait ─────────────────────────────────────────────────

#[async_trait]
pub trait AdapterTrait: Send + Sync {
    #[allow(dead_code)]
    fn name(&self) -> &str;
    async fn execute(&self, request: &ExecutionRequest) -> ExecutionResult;
    async fn run_tests(&self, workspace: &str, test_command: Option<&str>) -> serde_json::Value;
    async fn run_lint(&self, workspace: &str, lint_command: Option<&str>) -> serde_json::Value;
    async fn run_build(&self, workspace: &str, build_command: Option<&str>) -> serde_json::Value;
}
