//! Start command — starts all services via Docker Compose.

use std::path::PathBuf;

use super::{find_compose_file, run_compose};

pub fn run(dir: Option<PathBuf>, profiles: Vec<String>) {
    println!("🚀 Starting Evershade services...");

    let project_dir = dir
        .as_ref()
        .or_else(|| {
            find_compose_file()
                .and_then(|p| p.parent().map(|p| p.to_path_buf()))
        });

    let mut args = vec!["up", "-d"];
    for profile in &profiles {
        args.push("--profile");
        args.push(profile);
    }

    match run_compose(&args, project_dir.as_ref()) {
        Ok(_) => println!("✅ Services started successfully"),
        Err(e) => {
            println!("❌ Failed to start services: {}", e);
            std::process::exit(1);
        }
    }
}
