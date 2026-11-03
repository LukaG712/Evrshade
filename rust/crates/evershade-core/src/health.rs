//! Shared health check endpoints for Evershade services.
//!
//! Provides standard liveness, readiness, status, and metrics endpoints.

use axum::{routing::get, Json, Router};
use chrono::Utc;
use serde::Serialize;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::Instant;

/// Health check state shared across routes.
#[derive(Clone)]
pub struct HealthState {
    pub service_name: String,
    pub version: String,
    pub start_time: Instant,
    pub ready: Arc<AtomicBool>,
    pub request_count: Arc<AtomicU64>,
    pub dependencies: Vec<String>,
}

impl HealthState {
    pub fn new(service_name: impl Into<String>, version: impl Into<String>) -> Self {
        Self {
            service_name: service_name.into(),
            version: version.into(),
            start_time: Instant::now(),
            ready: Arc::new(AtomicBool::new(true)),
            request_count: Arc::new(AtomicU64::new(0)),
            dependencies: Vec::new(),
        }
    }

    pub fn with_dependencies(mut self, deps: Vec<String>) -> Self {
        self.dependencies = deps;
        self
    }
}

#[derive(Serialize)]
struct HealthResponse {
    status: String,
    service: String,
    version: String,
}

#[derive(Serialize)]
struct ReadyResponse {
    status: String,
    service: String,
}

#[derive(Serialize)]
struct StatusResponse {
    service: String,
    version: String,
    status: String,
    uptime_seconds: f64,
    start_time: String,
    dependencies: serde_json::Map<String, serde_json::Value>,
}

async fn health_handler(state: axum::extract::State<HealthState>) -> Json<HealthResponse> {
    state.request_count.fetch_add(1, Ordering::Relaxed);
    Json(HealthResponse {
        status: "ok".to_string(),
        service: state.service_name.clone(),
        version: state.version.clone(),
    })
}

async fn ready_handler(state: axum::extract::State<HealthState>) -> Json<ReadyResponse> {
    state.request_count.fetch_add(1, Ordering::Relaxed);
    let status = if state.ready.load(Ordering::Relaxed) {
        "ready".to_string()
    } else {
        "not_ready".to_string()
    };
    Json(ReadyResponse {
        status,
        service: state.service_name.clone(),
    })
}

async fn status_handler(state: axum::extract::State<HealthState>) -> Json<StatusResponse> {
    state.request_count.fetch_add(1, Ordering::Relaxed);
    let uptime = state.start_time.elapsed().as_secs_f64();

    let mut deps = serde_json::Map::new();
    for dep in &state.dependencies {
        deps.insert(dep.clone(), serde_json::json!("unknown"));
    }

    Json(StatusResponse {
        service: state.service_name.clone(),
        version: state.version.clone(),
        status: "running".to_string(),
        uptime_seconds: (uptime * 10.0).round() / 10.0,
        start_time: Utc::now().to_rfc3339(),
        dependencies: deps,
    })
}

async fn metrics_handler(state: axum::extract::State<HealthState>) -> String {
    state.request_count.fetch_add(1, Ordering::Relaxed);
    let uptime = state.start_time.elapsed().as_secs_f64();
    let ready = if state.ready.load(Ordering::Relaxed) {
        1
    } else {
        0
    };
    let requests = state.request_count.load(Ordering::Relaxed);
    let service = state.service_name.to_lowercase();

    format!(
        "# HELP {}_uptime_seconds Service uptime in seconds.\n\
         # TYPE {}_uptime_seconds gauge\n\
         {}_uptime_seconds {:.1}\n\
         # HELP {}_requests_total Total HTTP requests.\n\
         # TYPE {}_requests_total counter\n\
         {}_requests_total {}\n\
         # HELP {}_ready Service readiness (1=ready, 0=not ready).\n\
         # TYPE {}_ready gauge\n\
         {}_ready {}\n",
        service,
        service,
        service,
        uptime,
        service,
        service,
        service,
        requests,
        service,
        service,
        service,
        ready,
    )
}

/// Register standard health check routes on an Axum router.
pub fn register_health_routes(
    service_name: impl Into<String>,
    version: impl Into<String>,
) -> Router {
    let state = HealthState::new(service_name, version);
    Router::new()
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        .with_state(state)
}

/// Register health routes with dependencies.
pub fn register_health_routes_with_deps(
    service_name: impl Into<String>,
    version: impl Into<String>,
    dependencies: Vec<String>,
) -> Router {
    let state = HealthState::new(service_name, version).with_dependencies(dependencies);
    Router::new()
        .route("/health", get(health_handler))
        .route("/ready", get(ready_handler))
        .route("/api/status", get(status_handler))
        .route("/metrics", get(metrics_handler))
        .with_state(state)
}

#[cfg(test)]
mod tests {
    use super::*;
    use axum::body::Body;
    use http::{Request, StatusCode};
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_health_is_public() {
        let app = register_health_routes("TestService", "1.0.0");
        let response = app
            .oneshot(
                Request::builder()
                    .uri("/health")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_metrics_is_public() {
        let app = register_health_routes("TestService", "1.0.0");
        let response = app
            .oneshot(
                Request::builder()
                    .uri("/metrics")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_ready_endpoint() {
        let app = register_health_routes("TestService", "1.0.0");
        let response = app
            .oneshot(
                Request::builder()
                    .uri("/ready")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_status_endpoint() {
        let app = register_health_routes("TestService", "1.0.0");
        let response = app
            .oneshot(
                Request::builder()
                    .uri("/api/status")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }
}
