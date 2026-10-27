"""Shared utilities for Speedy CLI.

Provides Rich table formatting and common output helpers.
"""

from rich.console import Console
from rich.table import Table

console = Console()


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]✓[/] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]✗[/] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/] {message}")


def create_status_table(title: str = "Service Status") -> Table:
    """Create a Rich table for service status display.

    Args:
        title: Table title.

    Returns:
        Configured Rich Table.
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Details", style="dim")
    return table


def create_capabilities_table(title: str = "Service Capabilities") -> Table:
    """Create a Rich table for capabilities display.

    Args:
        title: Table title.

    Returns:
        Configured Rich Table.
    """
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Version", style="yellow")
    table.add_column("Features", style="green")
    return table


def status_icon(healthy: bool) -> str:
    """Return a status icon string.

    Args:
        healthy: Whether the service is healthy.

    Returns:
        Green check or red X.
    """
    return "[bold green]●[/]" if healthy else "[bold red]●[/]"


def feature_list(features: list[str]) -> str:
    """Format a list of features as a comma-separated string.

    Args:
        features: List of feature names.

    Returns:
        Comma-separated string, truncated if too long.
    """
    text = ", ".join(features)
    if len(text) > 60:
        text = text[:57] + "..."
    return text
