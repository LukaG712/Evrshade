"""Shared modules for Evershade Python services.

This package provides backward-compatible imports. New services should use
the packages/ directory:
- packages/evershade-core: Config, errors, health, telemetry, middleware, auth, registry
- packages/evershade-events: Event contracts and event bus
- packages/evershade-db: Database utilities and SQLite WAL mode

Legacy files here are kept for backward compatibility with existing services.
"""
