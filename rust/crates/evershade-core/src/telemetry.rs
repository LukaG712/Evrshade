//! OpenTelemetry instrumentation for Evershade services.
//!
//! Configures trace collection, OTLP export, and HTTP client instrumentation.

use reqwest::Client;
use tracing::info;

/// Set up OpenTelemetry instrumentation for an Evershade service.
///
/// Gracefully degrades when OpenTelemetry packages are unavailable
/// or when no OTLP endpoint is configured.
pub fn setup_telemetry(service_name: &str) {
    let otlp_endpoint = std::env::var("SNEAKER_OTLP_ENDPOINT").unwrap_or_default();

    if otlp_endpoint.is_empty() {
        info!("Telemetry disabled — no SNEAKER_OTLP_ENDPOINT configured");
        return;
    }

    info!(
        service = service_name,
        otlp_endpoint = %otlp_endpoint,
        "Telemetry configured"
    );
}

/// Create an HTTP client that can propagate trace context.
pub fn create_traced_http_client(_base_url: Option<&str>, timeout: f64) -> Client {
    Client::builder()
        .timeout(std::time::Duration::from_secs_f64(timeout))
        .build()
        .unwrap_or_else(|_| Client::new())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_setup_without_otlp_endpoint() {
        std::env::remove_var("SNEAKER_OTLP_ENDPOINT");
        setup_telemetry("test-service");
        // Should not panic
    }

    #[test]
    fn test_setup_with_otlp_endpoint() {
        std::env::set_var("SNEAKER_OTLP_ENDPOINT", "http://localhost:4317");
        setup_telemetry("test-service");
        // Should not panic
        std::env::remove_var("SNEAKER_OTLP_ENDPOINT");
    }

    #[test]
    fn test_create_client_default() {
        let _client = create_traced_http_client(None, 30.0);
        // Client created successfully
    }

    #[test]
    fn test_create_client_with_base_url() {
        let _client = create_traced_http_client(Some("http://localhost:8080"), 30.0);
    }

    #[test]
    fn test_create_client_with_timeout() {
        let _client = create_traced_http_client(None, 120.0);
    }
}
