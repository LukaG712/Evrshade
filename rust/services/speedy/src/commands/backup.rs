//! Backup command — backs up Evershade databases.

use std::path::PathBuf;

pub fn run(output: PathBuf) {
    println!("💾 Backing up Evershade databases...");

    std::fs::create_dir_all(&output).unwrap_or_else(|e| {
        eprintln!("Failed to create backup directory: {}", e);
        std::process::exit(1);
    });

    let timestamp = chrono::Utc::now().format("%Y%m%d_%H%M%S");
    let backup_dir = output.join(&format!("evershade_backup_{}", timestamp));
    std::fs::create_dir_all(&backup_dir).unwrap_or_else(|e| {
        eprintln!("Failed to create backup directory: {}", e);
        std::process::exit(1);
    });

    let data_dir = PathBuf::from("./data");
    if data_dir.exists() {
        for entry in std::fs::read_dir(&data_dir).unwrap_or_else(|e| {
            eprintln!("Failed to read data directory: {}", e);
            std::process::exit(1);
        }) {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.extension().map_or(false, |ext| ext == "db") {
                let filename = path.file_name().unwrap();
                let dest = backup_dir.join(filename);
                std::fs::copy(&path, &dest).unwrap_or_else(|e| {
                    eprintln!("Failed to copy {}: {}", path.display(), e);
                });
                println!("  ✅ Backed up {}", filename.to_string_lossy());
            }
        }
    } else {
        println!("  ⚠️  Data directory not found at {}", data_dir.display());
    }

    println!("\n✅ Backup complete: {}", backup_dir.display());
}
