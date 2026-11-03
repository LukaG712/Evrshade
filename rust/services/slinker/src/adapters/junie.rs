//! Junie CLI adapter for Slinker — delegates tasks to the Junie CLI tool.

use async_trait::async_trait;

use crate::adapters::*;

pub struct JunieAdapter {
    junie_path: String,
}

impl JunieAdapter {
    pub fn new() -> Self {
        Self {
            junie_path: std::env::var("JUNIE_PATH").unwrap_or_else(|_| "junie".to_string()),
        }
    }
}

#[async_trait]
impl AdapterTrait for JunieAdapter {
    fn name(&self) -> &str {
        "junie"
    }

    async fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        let start = std::time::Instant::now();
        let task_id = gen_id();

        let prompt = format!("{}\n{}", request.title, request.description);

        let mut cmd = tokio::process::Command::new(&self.junie_path);
        cmd.args([
            "--non-interactive",
            &format!("--workspace={}", request.workspace_path),
            "--prompt",
            &prompt,
        ]);

        match tokio::time::timeout(
            std::time::Duration::from_secs(request.timeout),
            cmd.output(),
        )
        .await
        {
            Ok(Ok(output)) => {
                let stdout = String::from_utf8_lossy(&output.stdout).to_string();
                let stderr = String::from_utf8_lossy(&output.stderr).to_string();
                let duration = start.elapsed().as_millis() as i64;
                let success = output.status.success();

                ExecutionResult {
                    task_id,
                    status: if success { "completed" } else { "failed" }.to_string(),
                    output: stdout,
                    error: if !success && !stderr.is_empty() {
                        Some(stderr)
                    } else {
                        None
                    },
                    exit_code: output.status.code().unwrap_or(-1),
                    file_changes: Vec::new(),
                    duration_ms: duration,
                }
            }
            Ok(Err(e)) => {
                let duration = start.elapsed().as_millis() as i64;
                ExecutionResult {
                    task_id,
                    status: "failed".to_string(),
                    output: String::new(),
                    error: Some(format!("Junie not found: {}", e)),
                    exit_code: -1,
                    file_changes: Vec::new(),
                    duration_ms: duration,
                }
            }
            Err(_) => {
                let duration = start.elapsed().as_millis() as i64;
                ExecutionResult {
                    task_id,
                    status: "timeout".to_string(),
                    output: String::new(),
                    error: Some(format!(
                        "Junie execution timed out after {}s",
                        request.timeout
                    )),
                    exit_code: -1,
                    file_changes: Vec::new(),
                    duration_ms: duration,
                }
            }
        }
    }

    async fn run_tests(&self, _workspace: &str, _test_command: Option<&str>) -> serde_json::Value {
        serde_json::json!({"error": "Junie adapter does not support run_tests directly"})
    }

    async fn run_lint(&self, _workspace: &str, _lint_command: Option<&str>) -> serde_json::Value {
        serde_json::json!({"error": "Junie adapter does not support run_lint directly"})
    }

    async fn run_build(&self, _workspace: &str, _build_command: Option<&str>) -> serde_json::Value {
        serde_json::json!({"error": "Junie adapter does not support run_build directly"})
    }
}
