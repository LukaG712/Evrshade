//! Evershade Core — Shared platform foundation.
//!
//! Provides configuration, error handling, health checks, telemetry,
//! middleware, authentication, and service discovery for all Evershade services.

pub mod auth;
pub mod config;
pub mod error;
pub mod health;
pub mod registry;
pub mod security;
pub mod telemetry;

pub use auth::{create_service_token, verify_service_token, ServiceAuthMiddleware};
pub use config::{AuthConfig, DatabaseConfig, Environment, ServiceConfig, TelemetryConfig};
pub use error::{
    error_response, success_response, CorrelationIdMiddleware, ErrorCode, EvershadeError,
    RequestLoggingMiddleware,
};
pub use health::register_health_routes;
pub use registry::{
    register_service_routes, ServiceDiscoveryClient, ServiceInfo, ServiceRegistry, ServiceStatus,
};
pub use security::{add_cors_middleware, add_security_middleware, RateLimitState};
pub use telemetry::{create_traced_http_client, setup_telemetry};
