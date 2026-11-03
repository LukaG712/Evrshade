//! Restore command — restores from backup.

use std::path::PathBuf;

pub fn run(backup: PathBuf) {
    if !backup.exists() {
        eprintln!("❌ Backup not found: {}", backup.display());
        std::process::exit(1);
    }

    println!("🔄 Restoring from backup: {}", backup.display());

    let data_dir = PathBuf::from("./data");
    std::fs::create_dir_all(&data_dir).unwrap_or_else(|e| {
        eprintln!("Failed to create data directory: {}", e);
        std::process::exit(1);
    });

    if backup.is_dir() {
        for entry in std::fs::read_dir(&backup).unwrap_or_else(|e| {
            eprintln!("Failed to read backup directory: {}", e);
            std::process::exit(1);
        }) {
            let entry = entry.unwrap();
            let path = entry.path();
            if path.extension().map_or(false, |ext| ext == "db") {
                let filename = path.file_name().unwrap();
                let dest = data_dir.join(filename);
                std::fs::copy(&path, &dest).unwrap_or_else(|e| {
                    eprintln!("Failed to restore {}: {}", path.display(), e);
                });
                println!("  ✅ Restored {}", filename.to_string_lossy());
            }
        }
    } else {
        let filename = backup.file_name().unwrap();
        let dest = data_dir.join(filename);
        std::fs::copy(&backup, &dest).unwrap_or_else(|e| {
            eprintln!("Failed to restore backup: {}", e);
            std::process::exit(1);
        });
        println!("  ✅ Restored {}", filename.to_string_lossy());
    }

    println!("\n✅ Restore complete. Restart services with 'evershade start'.");
}
