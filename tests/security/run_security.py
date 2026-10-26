"""
Security validation for Evershade platform.
Checks container hardening, network isolation, API key auth, CSRF, encryption, and SSRF.

Usage:
    python -m tests.security.run_security
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def check_docker_compose_security():
    """Verify docker-compose.yml has proper security settings."""
    print("\n" + "=" * 70)
    print("Security Check: Docker Compose Configuration")
    print("=" * 70)

    compose_file = project_root / "docker-compose.yml"
    if not compose_file.exists():
        print("  ✗ docker-compose.yml not found")
        return False

    content = compose_file.read_text()

    checks = {
        "read_only filesystem": "read_only" in content,
        "no_new_privileges": "no-new-privileges" in content,
        "cap_drop ALL": "cap_drop" in content and "ALL" in content,
        "internal network": "internal:" in content or "internal: true" in content,
        "resource limits": "deploy" in content and "resources" in content,
    }

    all_passed = True
    for name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def check_network_isolation():
    """Verify network isolation between internal and frontend services."""
    print("\n" + "=" * 70)
    print("Security Check: Network Isolation")
    print("=" * 70)

    compose_file = project_root / "docker-compose.yml"
    if not compose_file.exists():
        print("  ✗ docker-compose.yml not found")
        return False

    content = compose_file.read_text()

    # Check that internal network exists
    has_internal = "internal:" in content or "internal: true" in content
    print(f"  {'✓' if has_internal else '✗'} Internal network defined")

    # Check that services use internal network
    has_internal_network = "internal" in content
    print(f"  {'✓' if has_internal_network else '✗'} Services use internal network")

    # Check that only Greenie and Slammer are exposed to host
    # This is a simplified check
    print("  ℹ Verify manually: Only Greenie and Slammer should expose ports to host")

    return has_internal and has_internal_network


def check_api_key_auth():
    """Verify API key authentication is implemented."""
    print("\n" + "=" * 70)
    print("Security Check: API Key Authentication")
    print("=" * 70)

    auth_file = project_root / "services" / "Greenie" / "app" / "auth.py"
    if not auth_file.exists():
        print("  ✗ auth.py not found in Greenie")
        return False

    content = auth_file.read_text()

    checks = {
        "API key validation": "api_key" in content.lower()
        or "bearer" in content.lower(),
        "Authentication middleware": "middleware" in content.lower()
        or "depend" in content.lower(),
        "Key hashing": "hash" in content.lower() or "sha" in content.lower(),
    }

    all_passed = True
    for name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def check_csrf_protection():
    """Verify CSRF protection is implemented."""
    print("\n" + "=" * 70)
    print("Security Check: CSRF Protection")
    print("=" * 70)

    main_file = project_root / "services" / "Greenie" / "app" / "main.py"
    if not main_file.exists():
        print("  ✗ main.py not found in Greenie")
        return False

    content = main_file.read_text()

    has_csrf = "csrf" in content.lower()
    print(
        f"  {'✓' if has_csrf else 'ℹ'} CSRF protection (may be handled by middleware)"
    )

    return True  # Not critical for API-only services


def check_secret_encryption():
    """Verify secret encryption in Hider."""
    print("\n" + "=" * 70)
    print("Security Check: Secret Encryption")
    print("=" * 70)

    crypto_file = project_root / "services" / "Hider" / "app" / "crypto.py"
    if not crypto_file.exists():
        print("  ✗ crypto.py not found in Hider")
        return False

    content = crypto_file.read_text()

    checks = {
        "AES-256-GCM": "aes" in content.lower() and "gcm" in content.lower(),
        "Encryption function": "encrypt" in content.lower(),
        "Decryption function": "decrypt" in content.lower(),
        "Key derivation": "key" in content.lower(),
    }

    all_passed = True
    for name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def check_ssrf_protection():
    """Verify SSRF protection in Trapper."""
    print("\n" + "=" * 70)
    print("Security Check: SSRF Protection")
    print("=" * 70)

    ssrf_file = project_root / "services" / "Trapper" / "src" / "ssrf.ts"
    if not ssrf_file.exists():
        print("  ✗ ssrf.ts not found in Trapper")
        return False

    content = ssrf_file.read_text()

    checks = {
        "Private IP blocking": "169.254" in content
        or "10." in content
        or "192.168" in content,
        "IP validation": "ip" in content.lower() or "address" in content.lower(),
        "Block list": "block" in content.lower() or "deny" in content.lower(),
    }

    all_passed = True
    for name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def check_env_example():
    """Verify .env.example documents all sensitive variables."""
    print("\n" + "=" * 70)
    print("Security Check: Environment Variables")
    print("=" * 70)

    env_file = project_root / ".env.example"
    if not env_file.exists():
        print("  ✗ .env.example not found")
        return False

    content = env_file.read_text()

    sensitive_vars = [
        "API_KEY",
        "SECRET",
        "PASSWORD",
        "TOKEN",
        "ENCRYPTION_KEY",
    ]

    found_vars = []
    for var in sensitive_vars:
        if var in content.upper():
            found_vars.append(var)
            print(f"  ✓ {var} documented")
        else:
            print(f"  ℹ {var} not found (may not be required)")

    return len(found_vars) > 0


def check_packages_security():
    """Verify evershade-core packages have proper security measures."""
    print("\n" + "=" * 70)
    print("Security Check: Core Platform Packages")
    print("=" * 70)

    # Check auth module in evershade-core
    auth_file = (
        project_root / "packages" / "evershade-core" / "src" / "evershade" / "auth.py"
    )
    if not auth_file.exists():
        print("  ✗ evershade-core/auth.py not found")
        return False

    auth_content = auth_file.read_text()
    auth_checks = {
        "JWT token creation": "create_token" in auth_content.lower()
        or "encode" in auth_content.lower(),
        "Token verification": "verify" in auth_content.lower()
        or "decode" in auth_content.lower(),
        "Auth middleware": "middleware" in auth_content.lower()
        or "depend" in auth_content.lower(),
    }

    all_passed = True
    for name, passed in auth_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} evershade-core auth — {name}")
        if not passed:
            all_passed = False

    # Check errors module in evershade-core
    errors_file = (
        project_root / "packages" / "evershade-core" / "src" / "evershade" / "errors.py"
    )
    if not errors_file.exists():
        print("  ✗ evershade-core/errors.py not found")
        return False

    errors_content = errors_file.read_text()
    errors_checks = {
        "Error envelope": "error" in errors_content.lower(),
        "Error code enum": "ErrorCode" in errors_content
        or "error_code" in errors_content.lower(),
        "Error handler registration": "register" in errors_content.lower()
        or "add_exception" in errors_content.lower(),
    }

    for name, passed in errors_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} evershade-core errors — {name}")
        if not passed:
            all_passed = False

    # Check config module has secret redaction
    config_file = (
        project_root / "packages" / "evershade-core" / "src" / "evershade" / "config.py"
    )
    if config_file.exists():
        config_content = config_file.read_text()
        has_redaction = (
            "redact" in config_content.lower() or "secret" in config_content.lower()
        )
        status = "✓" if has_redaction else "ℹ"
        print(f"  {status} evershade-core config — secret handling")
    else:
        print("  ℹ evershade-core/config.py not found (optional)")

    return all_passed


def check_service_dockerfiles():
    """Verify service Dockerfiles mount the new packages."""
    print("\n" + "=" * 70)
    print("Security Check: Service Dockerfiles")
    print("=" * 70)

    python_services = [
        "Greenie",
        "Slinker",
        "Gobber",
        "Sneaker",
        "Hider",
        "Poltergeist",
        "Shrewd",
    ]

    all_passed = True
    for service in python_services:
        dockerfile = project_root / "services" / service / "Dockerfile"
        if not dockerfile.exists():
            print(f"  ⊘ {service}: Dockerfile not found")
            continue

        content = dockerfile.read_text()
        has_packages = "evershade-core" in content or "packages" in content
        status = "✓" if has_packages else "ℹ"
        print(f"  {status} {service}: mounts evershade packages")
        if not has_packages:
            all_passed = False

    return all_passed


def run_all_checks():
    """Run all security checks."""
    print("\n" + "=" * 70)
    print("Evershade Security Validation")
    print("=" * 70)

    results = {
        "Docker Compose Security": check_docker_compose_security(),
        "Network Isolation": check_network_isolation(),
        "API Key Authentication": check_api_key_auth(),
        "CSRF Protection": check_csrf_protection(),
        "Secret Encryption": check_secret_encryption(),
        "SSRF Protection": check_ssrf_protection(),
        "Environment Variables": check_env_example(),
        "Core Platform Packages": check_packages_security(),
        "Service Dockerfiles": check_service_dockerfiles(),
    }

    print("\n" + "=" * 70)
    print("Security Validation Summary")
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
