"""Doctor command — comprehensive health diagnostics."""

import click

from speedy.client import ServiceClient
from speedy.config import load_config
from speedy.docker import check_docker_available, find_compose_file
from speedy.utils import (
    console,
    create_status_table,
    print_error,
    print_info,
    print_success,
    print_warning,
)


@click.command(help="Run comprehensive health diagnostics.")
@click.option("--url", "greenie_url", help="Override Greenie API URL.")
def doctor(greenie_url):
    """Run comprehensive health checks and report issues."""
    issues = []
    warnings = []

    # 1. Check Docker
    print_info("Checking Docker...")
    if check_docker_available():
        print_success("Docker is running")
    else:
        issues.append("Docker is not available")
        print_error("Docker is not available")

    # 2. Check compose file
    print_info("Checking project configuration...")
    compose = find_compose_file()
    if compose:
        print_success(f"Found docker-compose.yml at {compose}")
    else:
        warnings.append("docker-compose.yml not found (may be running without Docker)")
        print_warning("docker-compose.yml not found")

    # 3. Check .env file
    env_file = compose.parent / ".env" if compose else None
    if env_file and env_file.exists():
        print_success(".env file found")
    else:
        warnings.append(".env file not found")
        print_warning(".env file not found")

    # 4. Check services
    print_info("Checking service health...")
    config = load_config(greenie_url=greenie_url)
    services = config["services"]

    healthy_count = 0
    table = create_status_table("Service Health Check")

    for name, info in services.items():
        client = ServiceClient(info["url"], info.get("api_key"), timeout=5.0)
        result = client.check_health()

        if result["healthy"]:
            healthy_count += 1
            version = result["data"].get("version", "-") if result["data"] else "-"
            table.add_row(name, "●", version, "ok")
        else:
            issues.append(f"{name} is unreachable")
            table.add_row(name, "○", "-", "unreachable")

    console.print(table)

    # 5. Check API keys
    print_info("Checking API key configuration...")
    missing_keys = []
    for name in services:
        if not config["api_keys"].get(name):
            missing_keys.append(name)

    if missing_keys:
        warnings.append(f"Missing API keys for: {', '.join(missing_keys)}")
        print_warning(f"Missing API keys for: {', '.join(missing_keys)}")
    else:
        print_success("All API keys configured")

    # Summary
    console.print()
    if issues:
        print_error(f"Found {len(issues)} issue(s):")
        for issue in issues:
            console.print(f"  ✗ {issue}")
    if warnings:
        print_warning(f"Found {len(warnings)} warning(s):")
        for warning in warnings:
            console.print(f"  ⚠ {warning}")

    if not issues and not warnings:
        print_success("All checks passed!")
    elif not issues:
        print_info("Services are healthy with minor warnings.")
    else:
        print_error("Some services have issues. See above for details.")

    console.print(f"\nServices healthy: {healthy_count}/{len(services)}")
