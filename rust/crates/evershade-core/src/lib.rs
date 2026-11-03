//! Evershade Core — Shared platform foundation.
//!
//! Provides configuration, error handling, health checks, telemetry,
//! middleware, authentication, and service discovery for all Evershade services.

pub mod config;
pub mod error;
pub mod health;
pub mod auth;
pub mod security;
pub mod telemetry;
pub mod registry;

pub use config::{AuthConfig, DatabaseConfig, Environment, ServiceConfig, TelemetryConfig};
pub use error::{CorrelationIdMiddleware, ErrorCode, EvershadeError, RequestLoggingMiddleware, error_response, success_response};
pub use health::register_health_routes;
pub use auth::{ServiceAuthMiddleware, create_service_token, verify_service_token};
pub use security::{RateLimitState, add_cors_middleware, add_security_middleware};
pub use telemetry::{setup_telemetry, create_traced_http_client};
pub use registry::{ServiceDiscoveryClient, ServiceRegistry, ServiceStatus, ServiceInfo, register_service_routes};
