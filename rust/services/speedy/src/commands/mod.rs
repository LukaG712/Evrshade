//! Command modules for the Evershade CLI.

use std::path::PathBuf;
use std::process::Command;

pub mod backup;
pub mod capabilities;
pub mod doctor;
pub mod install;
pub mod logs;
pub mod monitoring;
pub mod restore;
pub mod start;
pub mod status;
pub mod stop;

// ─── Shared Helpers ────────────────────────────────────────────────

pub struct CommandOutput {
    pub status: i32,
    pub stdout: String,
    pub stderr: String,
}

pub fn find_compose_file() -> Option<PathBuf> {
    let mut current = std::env::current_dir().ok()?;
    for _ in 0..10 {
        let compose_file = current.join("docker-compose.yml");
        if compose_file.exists() {
            return Some(compose_file);
        }
        current = current.parent()?.to_path_buf();
    }
    None
}

pub fn run_compose(
    args: &[&str],
    project_dir: Option<&PathBuf>,
) -> Result<CommandOutput, String> {
    let mut cmd = Command::new("docker");
    cmd.arg("compose");
    if let Some(dir) = project_dir {
        cmd.arg("-f")
            .arg(dir.join("docker-compose.yml").to_string_lossy().as_ref());
    }
    cmd.args(args);

    let output = cmd.output().map_err(|e| format!("Failed to run docker: {}", e))?;

    Ok(CommandOutput {
        status: output.status.code().unwrap_or(-1),
        stdout: String::from_utf8_lossy(&output.stdout).to_string(),
        stderr: String::from_utf8_lossy(&output.stderr).to_string(),
    })
}

pub fn check_docker_available() -> bool {
    Command::new("docker")
        .arg("info")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}
