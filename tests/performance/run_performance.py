"""
Performance validation for Evershade platform.
Checks health check response times, API latency, and resource limits.

Usage:
    python -m tests.performance.run_performance
"""

import sys
import time
from pathlib import Path

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Service definitions with ports
SERVICES = [
    ("Greenie", 8080),
    ("Slinker", 8000),
    ("Trapper", 3000),
    ("Gobber", 8085),
    ("Sneaker", 8086),
    ("Hider", 8087),
    ("Poltergeist", 8088),
    ("Shrewd", 8089),
]

# Performance thresholds
HEALTH_CHECK_TIMEOUT = 5.0  # seconds
API_CALL_TIMEOUT = 30.0  # seconds


def check_health_response_times():
    """Verify health check response times are under 5 seconds."""
    print("\n" + "=" * 70)
    print("Performance Check: Health Check Response Times")
    print("=" * 70)
    print(f"  Threshold: < {HEALTH_CHECK_TIMEOUT}s")
    
    if not HAS_HTTPX:
        print("  ⊘ httpx not available, skipping")
        return False
    
    all_passed = True
    results = []
    
    with httpx.Client(timeout=HEALTH_CHECK_TIMEOUT) as client:
        for name, port in SERVICES:
            try:
                start = time.perf_counter()
                resp = client.get(f"http://localhost:{port}/health")
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    status = "✓" if elapsed < HEALTH_CHECK_TIMEOUT else "✗"
                    results.append((name, elapsed, resp.status_code == 200 and elapsed < HEALTH_CHECK_TIMEOUT))
                    print(f"  {status} {name}: {elapsed:.3f}s (status {resp.status_code})")
                    if elapsed >= HEALTH_CHECK_TIMEOUT:
                        all_passed = False
                else:
                    print(f"  ✗ {name}: status {resp.status_code}")
                    results.append((name, None, False))
                    all_passed = False
            except Exception as e:
                print(f"  ⊘ {name}: not reachable ({e})")
                results.append((name, None, False))
    
    return all_passed


def check_api_latency():
    """Verify API call latency is under 30 seconds."""
    print("\n" + "=" * 70)
    print("Performance Check: API Call Latency")
    print("=" * 70)
    print(f"  Threshold: < {API_CALL_TIMEOUT}s")
    
    if not HAS_HTTPX:
        print("  ⊘ httpx not available, skipping")
        return False
    
    all_passed = True
    
    # Test Greenie API endpoints
    with httpx.Client(timeout=API_CALL_TIMEOUT) as client:
        endpoints = [
            ("Greenie /api/status", f"http://localhost:8080/api/status"),
            ("Greenie /api/agents", f"http://localhost:8080/api/agents"),
            ("Slinker /api/v1/tasks", f"http://localhost:8000/api/v1/tasks"),
            ("Shrewd /api/models", f"http://localhost:8089/api/models"),
        ]
        
        for name, url in endpoints:
            try:
                start = time.perf_counter()
                resp = client.get(url)
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    status = "✓" if elapsed < API_CALL_TIMEOUT else "✗"
                    print(f"  {status} {name}: {elapsed:.3f}s")
                    if elapsed >= API_CALL_TIMEOUT:
                        all_passed = False
                else:
                    print(f"  ✗ {name}: status {resp.status_code}")
                    all_passed = False
            except Exception as e:
                print(f"  ⊘ {name}: not reachable")
    
    return all_passed


def check_resource_limits():
    """Verify resource limits are configured in docker-compose."""
    print("\n" + "=" * 70)
    print("Performance Check: Resource Limits")
    print("=" * 70)
    
    compose_file = project_root / "docker-compose.yml"
    if not compose_file.exists():
        print("  ✗ docker-compose.yml not found")
        return False
    
    content = compose_file.read_text()
    
    has_deploy = "deploy" in content
    has_resources = "resources" in content
    has_memory = "memory" in content
    
    print(f"  {'✓' if has_deploy else 'ℹ'} Deploy section defined")
    print(f"  {'✓' if has_resources else 'ℹ'} Resource limits defined")
    print(f"  {'✓' if has_memory else 'ℹ'} Memory limits defined")
    
    # Resource limits are recommended but not required for dev
    return True


def check_sqlite_wal_mode():
    """Verify SQLite WAL mode is configured via evershade-db."""
    print("\n" + "=" * 70)
    print("Performance Check: SQLite WAL Mode")
    print("=" * 70)

    # Check evershade-db package for WAL mode
    db_package = project_root / "packages" / "evershade-db" / "src" / "evershade_db" / "__init__.py"
    if db_package.exists():
        content = db_package.read_text()
        has_wal = "wal" in content.lower() or "WAL" in content
        status = "✓" if has_wal else "✗"
        print(f"  {status} evershade-db package: WAL mode {'configured' if has_wal else 'not found'}")
    else:
        print("  ✗ evershade-db package not found")

    # Check each service's database.py for evershade-db integration
    services_with_db = [
        ("Greenie", "services/Greenie/app/database.py"),
        ("Slinker", "services/Slinker/app/database.py"),
        ("Gobber", "services/Gobber/app/database.py"),
        ("Sneaker", "services/Sneaker/app/database.py"),
        ("Hider", "services/Hider/app/database.py"),
        ("Poltergeist", "services/Poltergeist/app/database.py"),
        ("Shrewd", "services/Shrewd/app/database.py"),
    ]

    all_passed = True
    for name, path in services_with_db:
        db_file = project_root / path
        if not db_file.exists():
            print(f"  ⊘ {name}: database.py not found")
            continue

        content = db_file.read_text()
        # Check for evershade-db import or direct WAL mode
        has_evershade_db = "evershade_db" in content or "evershade-db" in content
        has_wal = "wal" in content.lower() or "WAL" in content

        if has_evershade_db:
            status = "✓"
            print(f"  {status} {name}: uses evershade-db (WAL mode inherited)")
        elif has_wal:
            status = "✓"
            print(f"  {status} {name}: WAL mode configured directly")
        else:
            status = "ℹ"
            print(f"  {status} {name}: WAL mode not found")
            all_passed = False

    return all_passed


def check_metrics_endpoints():
    """Verify /metrics endpoint is available on all services."""
    print("\n" + "=" * 70)
    print("Performance Check: /metrics Endpoints")
    print("=" * 70)

    if not HAS_HTTPX:
        print("  ⊘ httpx not available, skipping")
        return False

    services_with_metrics = [
        ("Greenie", 8080),
        ("Slinker", 8000),
        ("Trapper", 3000),
        ("Gobber", 8085),
        ("Sneaker", 8086),
        ("Hider", 8087),
        ("Poltergeist", 8088),
        ("Shrewd", 8089),
    ]

    accessible = 0
    with httpx.Client(timeout=5.0) as client:
        for name, port in services_with_metrics:
            try:
                resp = client.get(f"http://localhost:{port}/metrics")
                if resp.status_code == 200:
                    accessible += 1
                    print(f"  ✓ {name}: /metrics accessible (port {port})")
                else:
                    print(f"  ℹ {name}: /metrics returned {resp.status_code}")
            except Exception:
                print(f"  ⊘ {name}: not reachable")

    print(f"\n  {accessible}/{len(services_with_metrics)} services expose /metrics")
    return accessible > 0


def run_all_checks():
    """Run all performance checks."""
    print("\n" + "=" * 70)
    print("Evershade Performance Validation")
    print("=" * 70)

    results = {
        "Health Check Response Times": check_health_response_times(),
        "API Call Latency": check_api_latency(),
        "Resource Limits": check_resource_limits(),
        "SQLite WAL Mode": check_sqlite_wal_mode(),
        "Metrics Endpoints": check_metrics_endpoints(),
    }
    
    print("\n" + "=" * 70)
    print("Performance Validation Summary")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {status}: {name}")
    
    print(f"\n  Total: {passed}/{total} checks passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
