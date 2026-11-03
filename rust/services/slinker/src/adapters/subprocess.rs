//! Subprocess adapter for Slinker — executes shell commands in isolated workspaces.

use async_trait::async_trait;
use std::time::Instant;

use crate::adapters::*;

lazy_static::lazy_static! {
    static ref ALLOWED_COMMANDS: std::collections::HashSet<&'static str> = [
        "python", "python3", "pip", "pip3", "node", "npm", "npx", "git",
        "make", "cmake", "pytest", "ruff", "black", "mypy", "cargo", "go",
        "rustc", "java", "javac", "mvn", "gradle", "docker", "docker-compose",
        "ls", "cat", "head", "tail", "grep", "find", "echo", "date", "pwd",
        "whoami", "curl", "wget", "tar", "zip", "unzip", "chmod", "chown",
        "rm", "cp", "mv", "mkdir",
    ]
    .iter()
    .cloned()
    .collect();
}

/// Validate a shell command for safety.
pub fn validate_command(command: &str) -> Result<(), String> {
    if command.trim().is_empty() {
        return Err("Empty command is not allowed".to_string());
    }

    let dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '!', '\\', '\n', '\r'];
    for ch in command.chars() {
        if dangerous_chars.contains(&ch) {
            return Err(format!("Command contains dangerous character: {}", ch));
        }
    }

    let base_cmd = command.split_whitespace().next().unwrap_or("").to_string();
    let base_name = std::path::Path::new(&base_cmd)
        .file_stem()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_default();

    if !ALLOWED_COMMANDS.contains(base_name.as_str())
        && !ALLOWED_COMMANDS.contains(base_cmd.as_str())
    {
        return Err(format!("Command '{}' is not in the allowlist", base_name));
    }

    Ok(())
}

struct CommandResult {
    stdout: String,
    stderr: String,
    returncode: i32,
}

async fn run_command(
    command: &str,
    workspace: &str,
    timeout_secs: u64,
) -> Result<CommandResult, String> {
    let args: Vec<String> = shell_words::split(command)
        .map_err(|e| format!("Failed to parse command: {}", e))?;

    if args.is_empty() {
        return Err("Empty command".to_string());
    }

    let mut cmd = tokio::process::Command::new(&args[0]);
    cmd.args(&args[1..]).current_dir(workspace);

    let output = tokio::time::timeout(
        std::time::Duration::from_secs(timeout_secs),
        cmd.output(),
    )
    .await
    .map_err(|_| format!("Command timed out after {}s", timeout_secs))?
    .map_err(|e| format!("Failed to execute: {}", e))?;

    Ok(CommandResult {
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
        returncode: output.status.code().unwrap_or(-1),
    })
}

pub struct SubprocessAdapter;

impl SubprocessAdapter {
    pub fn new() -> Self {
        Self
    }
}

#[async_trait]
impl AdapterTrait for SubprocessAdapter {
    fn name(&self) -> &str {
        "subprocess"
    }

    async fn execute(&self, request: &ExecutionRequest) -> ExecutionResult {
        let start = Instant::now();
        let task_id = gen_id();

        let commands = request.commands.clone().unwrap_or_else(|| {
            if !request.description.is_empty() {
                vec![request.description.clone()]
            } else {
                vec![]
            }
        });

        let mut output_parts = Vec::new();
        let mut all_stderr = Vec::new();
        let mut last_returncode = 0i32;

        for cmd in &commands {
            if let Err(e) = validate_command(cmd) {
                output_parts.push(format!("$ {}", cmd));
                all_stderr.push(format!("Command rejected: {}", e));
                last_returncode = -1;
                continue;
            }

            match run_command(cmd, &request.workspace_path, request.timeout).await {
                Ok(result) => {
                    output_parts.push(format!("$ {}", cmd));
                    output_parts.push(result.stdout);
                    if !result.stderr.is_empty() {
                        all_stderr.push(result.stderr);
                    }
                    last_returncode = result.returncode;
                }
                Err(e) => {
                    output_parts.push(format!("$ {}", cmd));
                    all_stderr.push(e);
                    last_returncode = -1;
                }
            }
        }

        let duration = start.elapsed().as_millis() as i64;
        let status = if last_returncode == 0 {
            "completed"
        } else {
            "failed"
        };

        ExecutionResult {
            task_id,
            status: status.to_string(),
            output: output_parts.join("\n"),
            error: if last_returncode != 0 {
                Some(all_stderr.join("\n"))
            } else {
                None
            },
            exit_code: last_returncode,
            file_changes: Vec::new(),
            duration_ms: duration,
        }
    }

    async fn run_tests(
        &self,
        workspace: &str,
        test_command: Option<&str>,
    ) -> serde_json::Value {
        let cmd = match test_command {
            Some(c) => c.to_string(),
            None => "python -m pytest -x --tb=short".to_string(),
        };
        match run_command(&cmd, workspace, 120).await {
            Ok(r) => serde_json::json!({
                "passed": r.returncode == 0,
                "output": r.stdout,
                "error": r.stderr,
                "returncode": r.returncode,
            }),
            Err(e) => serde_json::json!({
                "passed": false,
                "error": e,
                "returncode": -1,
            }),
        }
    }

    async fn run_lint(
        &self,
        workspace: &str,
        lint_command: Option<&str>,
    ) -> serde_json::Value {
        let cmd = match lint_command {
            Some(c) => c.to_string(),
            None => "python -m ruff check .".to_string(),
        };
        match run_command(&cmd, workspace, 60).await {
            Ok(r) => serde_json::json!({
                "passed": r.returncode <= 1,
                "output": r.stdout,
                "error": r.stderr,
                "returncode": r.returncode,
            }),
            Err(e) => serde_json::json!({
                "passed": false,
                "error": e,
                "returncode": -1,
            }),
        }
    }

    async fn run_build(
        &self,
        workspace: &str,
        build_command: Option<&str>,
    ) -> serde_json::Value {
        let cmd = match build_command {
            Some(c) => c.to_string(),
            None => "make".to_string(),
        };
        match run_command(&cmd, workspace, 120).await {
            Ok(r) => serde_json::json!({
                "passed": r.returncode == 0,
                "output": r.stdout,
                "error": r.stderr,
                "returncode": r.returncode,
            }),
            Err(e) => serde_json::json!({
                "passed": false,
                "error": e,
                "returncode": -1,
            }),
        }
    }
}
