//! Stop command — stops all services via Docker Compose.

use std::path::PathBuf;

use super::{find_compose_file, run_compose};

pub fn run(dir: Option<PathBuf>) {
    println!("🛑 Stopping Evershade services...");

    let project_dir: Option<PathBuf> = dir
        .clone()
        .or_else(|| find_compose_file().and_then(|p| p.parent().map(|p| p.to_path_buf())));

    match run_compose(&["down"], project_dir.as_ref()) {
        Ok(_) => println!("✅ Services stopped successfully"),
        Err(e) => {
            println!("❌ Failed to stop services: {}", e);
            std::process::exit(1);
        }
    }
}
