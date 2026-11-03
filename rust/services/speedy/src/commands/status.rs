//! Status command — checks service health status.

use std::path::PathBuf;
use std::time::Duration;

use super::{find_compose_file, run_compose};

pub fn run(dir: Option<PathBuf>) {
    println!("📊 Evershade service status:");
    println!();

    let project_dir: Option<PathBuf> = dir
        .clone()
        .or_else(|| find_compose_file().and_then(|p| p.parent().map(|p| p.to_path_buf())));

    match run_compose(&["ps", "--format", "json"], project_dir.as_ref()) {
        Ok(output) if output.status == 0 => {
            let stdout = output.stdout.trim().to_string();
            if stdout.is_empty() {
                println!("  No running containers found.");
            } else if let Ok(containers) = serde_json::from_str::<Vec<serde_json::Value>>(&stdout) {
                for container in &containers {
                    let name = container
                        .get("Name")
                        .and_then(|v| v.as_str())
                        .unwrap_or("unknown");
                    let state = container
                        .get("State")
                        .and_then(|v| v.as_str())
                        .unwrap_or("unknown");
                    let status = if state == "running" { "✅" } else { "⚠️" };
                    println!("  {} {} ({})", status, name, state);
                }
            } else {
                println!("  {}", stdout);
            }
        }
        Ok(output) => {
            println!("  {}", output.stderr);
        }
        Err(e) => {
            println!("❌ Failed to get status: {}", e);
        }
    }

    println!();

    let services = [
        ("Hider", "http://localhost:8087"),
        ("Greenie", "http://localhost:8080"),
        ("Slinker", "http://localhost:8000"),
        ("Sneaker", "http://localhost:8085"),
        ("Poltergeist", "http://localhost:8086"),
        ("Shrewd", "http://localhost:8083"),
        ("Gobber", "http://localhost:8084"),
    ];

    println!("  API Health:");
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(5))
        .build()
        .unwrap_or_else(|_| reqwest::blocking::Client::new());

    for (name, url) in &services {
        match client.get(format!("{}/health", url)).send() {
            Ok(resp) if resp.status().is_success() => {
                println!("    ✅ {}", name);
            }
            Ok(_) => {
                println!("    ⚠️  {} (non-200 response)", name);
            }
            Err(_) => {
                println!("    ❌ {} (unreachable)", name);
            }
        }
    }
}
