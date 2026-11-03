//! Doctor command — runs diagnostics.

use std::process::Command;

use super::find_compose_file;

pub fn run() {
    println!("🩺 Running Evershade diagnostics...\n");

    println!("  Docker:");
    if check_docker_available() {
        println!("    ✅ Docker is running");
        if let Ok(output) = Command::new("docker").arg("--version").output() {
            let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
            println!("    📦 {}", version);
        }
    } else {
        println!("    ❌ Docker is not running");
    }

    println!("\n  Docker Compose:");
    match Command::new("docker").args(["compose", "version"]).output() {
        Ok(output) if output.status.success() => {
            let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
            println!("    ✅ {}", version);
        }
        _ => println!("    ❌ Docker Compose not available"),
    }

    println!("\n  Configuration:");
    match find_compose_file() {
        Some(path) => println!("    ✅ docker-compose.yml found at {}", path.display()),
        None => println!("    ⚠️  docker-compose.yml not found"),
    }

    println!("\n  Environment:");
    let env_vars = [
        ("API_KEY", "Service authentication key"),
        ("ENCRYPTION_SALT", "Hider encryption salt"),
        ("DB_URL", "Database URL"),
        ("REDIS_URL", "Redis connection URL"),
    ];
    for (var, desc) in &env_vars {
        match std::env::var(var) {
            Ok(val) if !val.is_empty() => {
                let masked = if *var == "API_KEY" || *var == "ENCRYPTION_SALT" {
                    format!("{}***", &val[..2.min(val.len())])
                } else {
                    val
                };
                println!("    ✅ {} = {}", var, masked);
            }
            _ => println!("    ⚠️  {} not set ({})", var, desc),
        }
    }

    println!("\n  Ports:");
    let ports = [
        (8080, "Greenie"),
        (8000, "Slinker"),
        (8087, "Hider"),
        (8085, "Sneaker"),
    ];
    for (port, name) in &ports {
        let listener = std::net::TcpListener::bind(format!("127.0.0.1:{}", port));
        match listener {
            Ok(_) => println!("    ✅ Port {} ({}) is available", port, name),
            Err(_) => println!("    ⚠️  Port {} ({}) is in use", port, name),
        }
    }

    println!("\n✅ Diagnostics complete");
}

fn check_docker_available() -> bool {
    Command::new("docker")
        .arg("info")
        .output()
        .map(|o| o.status.success())
        .unwrap_or(false)
}
