//! Install command — validates environment and prepares for installation.

use std::path::PathBuf;

use super::{check_docker_available, find_compose_file, run_compose};

pub fn run(dir: Option<PathBuf>) {
    println!("🔧 Validating Evershade environment...");

    if !check_docker_available() {
        println!("❌ Docker is not available. Please install Docker first.");
        std::process::exit(1);
    }
    println!("✅ Docker is available");

    let compose_file = match &dir {
        Some(d) => d.join("docker-compose.yml"),
        None => find_compose_file().unwrap_or_else(|| {
            println!(
                "❌ docker-compose.yml not found. Run from the project root or specify --dir."
            );
            std::process::exit(1);
        }),
    };

    if !compose_file.exists() {
        println!(
            "❌ docker-compose.yml not found at {}",
            compose_file.display()
        );
        std::process::exit(1);
    }
    println!("✅ Found docker-compose.yml");

    let project_dir: Option<PathBuf> = dir
        .clone()
        .or_else(|| compose_file.parent().map(|p| p.to_path_buf()));
    match run_compose(&["config", "--quiet"], project_dir.as_ref()) {
        Ok(_) => println!("✅ Docker Compose configuration is valid"),
        Err(e) => {
            println!("❌ Invalid Docker Compose configuration: {}", e);
            std::process::exit(1);
        }
    }

    let required_vars = ["API_KEY", "ENCRYPTION_SALT"];
    for var in &required_vars {
        if std::env::var(var).is_err() {
            println!("⚠️  Missing environment variable: {}", var);
        }
    }

    println!("✅ Environment validation complete");
}
