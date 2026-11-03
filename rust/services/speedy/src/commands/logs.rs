//! Logs command — views service logs.

use std::path::PathBuf;

use super::{find_compose_file, run_compose};

pub fn run(service: Option<String>, tail: i64, dir: Option<PathBuf>) {
    let project_dir: Option<PathBuf> = dir
        .clone()
        .or_else(|| find_compose_file().and_then(|p| p.parent().map(|p| p.to_path_buf())));

    let service_name = service.as_deref().unwrap_or("");
    let tail_str = tail.to_string();
    let mut args = vec!["logs", "--tail", &tail_str];
    if !service_name.is_empty() {
        args.push(service_name);
    }

    match run_compose(&args, project_dir.as_ref()) {
        Ok(output) if output.status == 0 => {
            println!("{}", output.stdout);
        }
        Ok(output) => {
            eprintln!("Error: {}", output.stderr);
            std::process::exit(1);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}
