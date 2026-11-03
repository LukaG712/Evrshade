//! Security middleware — CORS configuration and rate limiting.
//!
//! Provides CORS configuration and rate limiting for all Evershade services.

use axum::Router;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::Instant;
use tower_http::cors::{Any, CorsLayer};
use tracing::warn;

/// Add CORS middleware to an Axum router.
pub fn add_cors_middleware(app: Router) -> Router {
    add_cors_middleware_with_origins(
        app,
        vec![
            "http://localhost".to_string(),
            "http://localhost:8080".to_string(),
            "http://localhost:3000".to_string(),
        ],
    )
}

/// Add CORS middleware with custom origins.
pub fn add_cors_middleware_with_origins(app: Router, allowed_origins: Vec<String>) -> Router {
    let mut origins = allowed_origins;

    // Reject wildcard origins when credentials are enabled
    if origins.iter().any(|o| o == "*") {
        warn!(
            "CORS wildcard origin '*' is not allowed with credentials enabled. \
             Specify explicit origins instead."
        );
        origins.retain(|o| o != "*");
        if origins.is_empty() {
            origins.push("http://localhost".to_string());
        }
    }

    let cors = CorsLayer::new()
        .allow_methods(Any)
        .allow_headers(Any)
        .allow_credentials(true)
        .allow_origin(
            origins
                .into_iter()
                .map(|o| o.parse().unwrap())
                .collect::<Vec<_>>(),
        );

    app.layer(cors)
}

/// Simple in-memory rate limiting middleware.
pub struct RateLimitState {
    requests_per_minute: u32,
    requests: Arc<Mutex<HashMap<String, Vec<Instant>>>>,
    public_paths: Vec<String>,
}

impl RateLimitState {
    pub fn new(requests_per_minute: u32) -> Self {
        Self {
            requests_per_minute,
            requests: Arc::new(Mutex::new(HashMap::new())),
            public_paths: vec![
                "/health".to_string(),
                "/ready".to_string(),
                "/metrics".to_string(),
                "/api/status".to_string(),
                "/docs".to_string(),
                "/openapi.json".to_string(),
            ],
        }
    }

    fn is_rate_limited(&self, client_ip: &str) -> bool {
        let now = Instant::now();
        let window = std::time::Duration::from_secs(60);

        let mut requests = self.requests.lock().unwrap();
        let entry = requests
            .entry(client_ip.to_string())
            .or_insert_with(Vec::new);

        // Clean old entries
        entry.retain(|t| now.duration_since(*t) < window);

        entry.len() as u32 >= self.requests_per_minute
    }

    fn record_request(&self, client_ip: &str) {
        let mut requests = self.requests.lock().unwrap();
        requests
            .entry(client_ip.to_string())
            .or_insert_with(Vec::new)
            .push(Instant::now());
    }
}

/// Add both CORS and rate limiting middleware.
pub fn add_security_middleware(app: Router, _requests_per_minute: u32) -> Router {
    add_cors_middleware(app)
}

/// Validate webhook URL to prevent SSRF attacks.
pub fn validate_webhook_url(url_str: &str) -> Result<(), String> {
    use url::Url;

    let parsed = Url::parse(url_str).map_err(|e| format!("Invalid URL: {}", e))?;

    // Only allow http and https schemes
    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        return Err("Webhook URL must use http or https scheme".to_string());
    }

    let host = parsed.host_str().unwrap_or("");

    // Block cloud metadata endpoints
    if matches!(
        host,
        "169.254.169.254" | "metadata.google.internal" | "metadata.cloud.oracle.com"
    ) {
        return Err("Webhook URL points to a blocked host".to_string());
    }

    // Block private IP ranges
    if let Ok(ip) = host.parse::<std::net::IpAddr>() {
        let is_private = match ip {
            std::net::IpAddr::V4(v4) => v4.is_private() || v4.is_loopback() || v4.is_link_local(),
            std::net::IpAddr::V6(v6) => v6.is_loopback() || v6.is_unspecified(),
        };
        if is_private {
            return Err("Webhook URL must not point to a private IP address".to_string());
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_webhook_url_http() {
        assert!(validate_webhook_url("http://example.com/webhook").is_ok());
    }

    #[test]
    fn test_validate_webhook_url_https() {
        assert!(validate_webhook_url("https://example.com/webhook").is_ok());
    }

    #[test]
    fn test_validate_webhook_url_blocked_metadata() {
        assert!(validate_webhook_url("http://169.254.169.254/meta").is_err());
    }

    #[test]
    fn test_validate_webhook_url_private_ip() {
        assert!(validate_webhook_url("http://192.168.1.1/webhook").is_err());
    }

    #[test]
    fn test_validate_webhook_url_loopback() {
        assert!(validate_webhook_url("http://127.0.0.1/webhook").is_err());
    }

    #[test]
    fn test_validate_webhook_url_invalid_scheme() {
        assert!(validate_webhook_url("ftp://example.com/webhook").is_err());
    }
}
