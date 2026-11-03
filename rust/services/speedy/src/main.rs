//! Speedy — CLI for the Evershade ecosystem.
//!
//! Provides commands to install, manage, and diagnose the Evershade platform.
//!
//! Usage:
//!     evershade install      # Validate environment
//!     evershade start        # Start services
//!     evershade stop         # Stop services
//!     evershade status       # Check service health
//!     evershade doctor       # Run diagnostics
//!     evershade logs [svc]   # View logs
//!     evershade capabilities # Query service capabilities
//!     evershade backup       # Backup databases
//!     evershade restore      # Restore from backup
//!     evershade monitoring   # Monitoring diagnostics

mod commands;

use clap::{Parser, Subcommand};
use std::path::PathBuf;

const VERSION: &str = "2.0.0";

#[derive(Parser, Debug)]
#[command(name = "evershade", version = VERSION, about = "Evershade — Self-hosted AI agent platform. Manage your Evershade ecosystem from the command line.")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Validate environment and prepare for installation
    Install {
        /// Project directory
        #[arg(short, long)]
        dir: Option<PathBuf>,
    },
    /// Start all services
    Start {
        /// Project directory
        #[arg(short, long)]
        dir: Option<PathBuf>,
        /// Docker Compose profiles to enable
        #[arg(short, long)]
        profile: Vec<String>,
    },
    /// Stop all services
    Stop {
        /// Project directory
        #[arg(short, long)]
        dir: Option<PathBuf>,
    },
    /// Check service health status
    Status {
        /// Project directory
        #[arg(short, long)]
        dir: Option<PathBuf>,
    },
    /// Run diagnostics
    Doctor,
    /// View service logs
    Logs {
        /// Service name (default: all)
        service: Option<String>,
        /// Number of lines to show
        #[arg(short, long, default_value = "100")]
        tail: i64,
        /// Project directory
        #[arg(short, long)]
        dir: Option<PathBuf>,
    },
    /// Query service capabilities
    Capabilities {
        /// Specific service to query (default: all)
        service: Option<String>,
    },
    /// Backup databases
    Backup {
        /// Backup directory
        #[arg(short, long, default_value = "./backups")]
        output: PathBuf,
    },
    /// Restore from backup
    Restore {
        /// Backup file path
        backup: PathBuf,
    },
    /// Monitoring diagnostics
    Monitoring,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Install { dir } => commands::install::run(dir),
        Commands::Start { dir, profile } => commands::start::run(dir, profile),
        Commands::Stop { dir } => commands::stop::run(dir),
        Commands::Status { dir } => commands::status::run(dir),
        Commands::Doctor => commands::doctor::run(),
        Commands::Logs { service, tail, dir } => {
            commands::logs::run(service, tail, dir)
        }
        Commands::Capabilities { service } => commands::capabilities::run(service),
        Commands::Backup { output } => commands::backup::run(output),
        Commands::Restore { backup } => commands::restore::run(backup),
        Commands::Monitoring => commands::monitoring::run(),
    }
}
