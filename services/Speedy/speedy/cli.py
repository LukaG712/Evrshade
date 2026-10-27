"""Speedy — CLI for the Evershade ecosystem.

Provides commands to install, manage, and diagnose the Evershade platform.

Usage:
    evershade install      # Validate environment
    evershade start        # Start services
    evershade stop         # Stop services
    evershade status       # Check service health
    evershade doctor       # Run diagnostics
    evershade logs [svc]   # View logs
    evershade capabilities # Query service capabilities
    evershade backup       # Backup databases
    evershade restore      # Restore from backup
    evershade monitoring   # Monitoring diagnostics
"""

import click

from speedy import __version__
from speedy.commands.backup import backup as backup_cmd
from speedy.commands.capabilities import capabilities as capabilities_cmd
from speedy.commands.doctor import doctor as doctor_cmd
from speedy.commands.install import install as install_cmd
from speedy.commands.logs import logs as logs_cmd
from speedy.commands.monitoring import monitoring as monitoring_cmd
from speedy.commands.restore import restore as restore_cmd
from speedy.commands.start import start as start_cmd
from speedy.commands.status import status as status_cmd
from speedy.commands.stop import stop as stop_cmd


@click.group()
@click.version_option(version=__version__, prog_name="evershade")
def main():
    """Evershade — Self-hosted AI agent platform.

    Manage your Evershade ecosystem from the command line.
    """


# Docker management commands
main.add_command(install_cmd, name="install")
main.add_command(start_cmd, name="start")
main.add_command(stop_cmd, name="stop")

# Service management commands
main.add_command(status_cmd, name="status")
main.add_command(doctor_cmd, name="doctor")
main.add_command(logs_cmd, name="logs")
main.add_command(capabilities_cmd, name="capabilities")

# Data management commands
main.add_command(backup_cmd, name="backup")
main.add_command(restore_cmd, name="restore")

# Monitoring commands
main.add_command(monitoring_cmd, name="monitoring")


if __name__ == "__main__":
    main()
