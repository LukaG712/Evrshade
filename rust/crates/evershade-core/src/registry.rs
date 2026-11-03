//! Service registry for discovery and health aggregation.
//!
//! Provides a central registry where services register on startup and
//! report their status. Other services can query the registry to discover
//! available services and their endpoints.

use axum::{
    extract::Path,
    routing::{delete, get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::info;

/// Service health status.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ServiceStatus {
    #[default]
    Healthy,
    Unhealthy,
    Starting,
    Stopping,
}

/// Information about a registered service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub url: String,
    pub version: String,
    pub status: ServiceStatus,
    pub capabilities: Vec<String>,
    pub registered_at: f64,
    pub last_heartbeat: f64,
}

impl ServiceInfo {
    pub fn to_dict(&self) -> serde_json::Value {
        serde_json::json!({
            "name": self.name,
            "url": self.url,
            "version": self.version,
            "status": self.status,
            "capabilities": self.capabilities,
            "registeredAt": self.registered_at,
            "lastHeartbeat": self.last_heartbeat,
        })
    }
}

fn now_timestamp() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

/// In-memory service registry.
#[derive(Clone)]
pub struct ServiceRegistry {
    inner: Arc<Mutex<HashMap<String, ServiceInfo>>>,
}

impl ServiceRegistry {
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn register(
        &self,
        name: String,
        url: String,
        version: String,
        capabilities: Option<Vec<String>>,
    ) -> ServiceInfo {
        let now = now_timestamp();
        let info = ServiceInfo {
            name: name.clone(),
            url,
            version,
            status: ServiceStatus::Healthy,
            capabilities: capabilities.unwrap_or_default(),
            registered_at: now,
            last_heartbeat: now,
        };
        let mut services = self.inner.lock().unwrap();
        services.insert(name, info.clone());
        info!("Registered service: {}", info.name);
        info
    }

    pub fn deregister(&self, name: &str) -> bool {
        let mut services = self.inner.lock().unwrap();
        if services.remove(name).is_some() {
            info!("Deregistered service: {}", name);
            true
        } else {
            false
        }
    }

    pub fn get(&self, name: &str) -> Option<ServiceInfo> {
        self.inner.lock().unwrap().get(name).cloned()
    }

    pub fn list_services(&self, status: Option<ServiceStatus>) -> Vec<ServiceInfo> {
        let services = self.inner.lock().unwrap();
        let mut result: Vec<ServiceInfo> = services.values().cloned().collect();
        if let Some(s) = status {
            result.retain(|svc| svc.status == s);
        }
        result
    }

    pub fn update_heartbeat(&self, name: &str) -> bool {
        let mut services = self.inner.lock().unwrap();
        if let Some(info) = services.get_mut(name) {
            info.last_heartbeat = now_timestamp();
            true
        } else {
            false
        }
    }

    pub fn update_status(&self, name: &str, status: ServiceStatus) -> bool {
        let mut services = self.inner.lock().unwrap();
        if let Some(info) = services.get_mut(name) {
            info.status = status;
            true
        } else {
            false
        }
    }

    pub fn all_healthy(&self) -> bool {
        self.inner
            .lock()
            .unwrap()
            .values()
            .all(|s| s.status == ServiceStatus::Healthy)
    }

    pub fn summary(&self) -> serde_json::Value {
        let services = self.inner.lock().unwrap();
        let total = services.len();
        let healthy = services
            .values()
            .filter(|s| s.status == ServiceStatus::Healthy)
            .count();
        serde_json::json!({
            "total": total,
            "healthy": healthy,
            "unhealthy": total - healthy,
            "services": services.values().map(|s| s.to_dict()).collect::<Vec<_>>(),
        })
    }
}

impl Default for ServiceRegistry {
    fn default() -> Self {
        Self::new()
    }
}

/// Registry state for Axum.
#[derive(Clone)]
pub struct RegistryState {
    pub registry: ServiceRegistry,
}

// Route handlers
async fn list_services(state: axum::extract::State<RegistryState>) -> Json<serde_json::Value> {
    Json(state.registry.summary())
}

async fn get_service(
    state: axum::extract::State<RegistryState>,
    Path(name): Path<String>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    match state.registry.get(&name) {
        Some(info) => Ok(Json(info.to_dict())),
        None => Err((
            axum::http::StatusCode::NOT_FOUND,
            format!("Service '{}' not found", name),
        )),
    }
}

#[derive(Deserialize)]
struct RegisterRequest {
    url: String,
    version: String,
    capabilities: Option<Vec<String>>,
}

async fn register_service(
    state: axum::extract::State<RegistryState>,
    Path(name): Path<String>,
    Json(req): Json<RegisterRequest>,
) -> Json<serde_json::Value> {
    let info = state
        .registry
        .register(name, req.url, req.version, req.capabilities);
    Json(info.to_dict())
}

async fn deregister_service(
    state: axum::extract::State<RegistryState>,
    Path(name): Path<String>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    if state.registry.deregister(&name) {
        Ok(Json(serde_json::json!({
            "status": "ok",
            "message": format!("Service '{}' deregistered", name),
        })))
    } else {
        Err((
            axum::http::StatusCode::NOT_FOUND,
            format!("Service '{}' not found", name),
        ))
    }
}

async fn heartbeat(
    state: axum::extract::State<RegistryState>,
    Path(name): Path<String>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    if state.registry.update_heartbeat(&name) {
        Ok(Json(serde_json::json!({"status": "ok"})))
    } else {
        Err((
            axum::http::StatusCode::NOT_FOUND,
            format!("Service '{}' not found", name),
        ))
    }
}

#[derive(Deserialize)]
struct StatusRequest {
    status: String,
}

async fn update_status(
    state: axum::extract::State<RegistryState>,
    Path(name): Path<String>,
    Json(req): Json<StatusRequest>,
) -> Result<Json<serde_json::Value>, (axum::http::StatusCode, String)> {
    let status = match req.status.as_str() {
        "healthy" => ServiceStatus::Healthy,
        "unhealthy" => ServiceStatus::Unhealthy,
        "starting" => ServiceStatus::Starting,
        "stopping" => ServiceStatus::Stopping,
        _ => ServiceStatus::Healthy,
    };
    if state.registry.update_status(&name, status) {
        Ok(Json(serde_json::json!({"status": "ok"})))
    } else {
        Err((
            axum::http::StatusCode::NOT_FOUND,
            format!("Service '{}' not found", name),
        ))
    }
}

/// Register service registry endpoints on an Axum router.
pub fn register_service_routes(registry: ServiceRegistry) -> Router {
    let state = RegistryState { registry };
    Router::new()
        .route("/api/registry/", get(list_services))
        .route("/api/registry/{name}", get(get_service))
        .route("/api/registry/{name}", post(register_service))
        .route("/api/registry/{name}", delete(deregister_service))
        .route("/api/registry/{name}/heartbeat", post(heartbeat))
        .route("/api/registry/{name}/status", post(update_status))
        .with_state(state)
}

/// Client for interacting with the service registry.
pub struct ServiceDiscoveryClient {
    registry_url: String,
    client: reqwest::Client,
}

impl ServiceDiscoveryClient {
    pub fn new(registry_url: String) -> Self {
        Self {
            registry_url: registry_url.trim_end_matches('/').to_string(),
            client: reqwest::Client::builder()
                .timeout(std::time::Duration::from_secs(10))
                .build()
                .unwrap(),
        }
    }

    pub async fn register(
        &self,
        name: &str,
        url: &str,
        version: &str,
        capabilities: Option<Vec<String>>,
    ) -> Result<serde_json::Value, reqwest::Error> {
        let body = serde_json::json!({
            "url": url,
            "version": version,
            "capabilities": capabilities.unwrap_or_default(),
        });
        let resp = self
            .client
            .post(format!("{}/api/registry/{}", self.registry_url, name))
            .json(&body)
            .send()
            .await?;
        let resp = resp.error_for_status()?;
        resp.json().await
    }

    pub async fn deregister(&self, name: &str) -> Result<serde_json::Value, reqwest::Error> {
        let resp = self
            .client
            .delete(format!("{}/api/registry/{}", self.registry_url, name))
            .send()
            .await?;
        let resp = resp.error_for_status()?;
        resp.json().await
    }

    pub async fn heartbeat(&self, name: &str) -> Result<serde_json::Value, reqwest::Error> {
        let resp = self
            .client
            .post(format!(
                "{}/api/registry/{}/heartbeat",
                self.registry_url, name
            ))
            .send()
            .await?;
        let resp = resp.error_for_status()?;
        resp.json().await
    }

    pub async fn get_service(
        &self,
        name: &str,
    ) -> Result<Option<serde_json::Value>, reqwest::Error> {
        let resp = self
            .client
            .get(format!("{}/api/registry/{}", self.registry_url, name))
            .send()
            .await?;
        if resp.status().as_u16() == 404 {
            return Ok(None);
        }
        let resp = resp.error_for_status()?;
        Ok(Some(resp.json().await?))
    }

    pub async fn list_services(&self) -> Result<serde_json::Value, reqwest::Error> {
        let resp = self
            .client
            .get(format!("{}/api/registry/", self.registry_url))
            .send()
            .await?;
        let resp = resp.error_for_status()?;
        resp.json().await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_register() {
        let registry = ServiceRegistry::new();
        let info = registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            None,
        );
        assert_eq!(info.name, "Test");
    }

    #[test]
    fn test_get() {
        let registry = ServiceRegistry::new();
        registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            None,
        );
        let info = registry.get("Test").unwrap();
        assert_eq!(info.name, "Test");
    }

    #[test]
    fn test_get_missing() {
        let registry = ServiceRegistry::new();
        assert!(registry.get("Missing").is_none());
    }

    #[test]
    fn test_deregister() {
        let registry = ServiceRegistry::new();
        registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            None,
        );
        assert!(registry.deregister("Test"));
    }

    #[test]
    fn test_deregister_missing() {
        let registry = ServiceRegistry::new();
        assert!(!registry.deregister("Missing"));
    }

    #[test]
    fn test_list_services() {
        let registry = ServiceRegistry::new();
        registry.register(
            "A".to_string(),
            "http://a".to_string(),
            "1.0".to_string(),
            None,
        );
        registry.register(
            "B".to_string(),
            "http://b".to_string(),
            "1.0".to_string(),
            None,
        );
        assert_eq!(registry.list_services(None).len(), 2);
    }

    #[test]
    fn test_list_services_filtered() {
        let registry = ServiceRegistry::new();
        registry.register(
            "A".to_string(),
            "http://a".to_string(),
            "1.0".to_string(),
            None,
        );
        let mut info = registry.register(
            "B".to_string(),
            "http://b".to_string(),
            "1.0".to_string(),
            None,
        );
        info.status = ServiceStatus::Unhealthy;
        {
            let mut services = registry.inner.lock().unwrap();
            services.insert("B".to_string(), info);
        }
        let healthy = registry.list_services(Some(ServiceStatus::Healthy));
        assert_eq!(healthy.len(), 1);
    }

    #[test]
    fn test_update_heartbeat() {
        let registry = ServiceRegistry::new();
        registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            None,
        );
        assert!(registry.update_heartbeat("Test"));
    }

    #[test]
    fn test_update_status() {
        let registry = ServiceRegistry::new();
        registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            None,
        );
        assert!(registry.update_status("Test", ServiceStatus::Unhealthy));
    }

    #[test]
    fn test_all_healthy() {
        let registry = ServiceRegistry::new();
        registry.register(
            "A".to_string(),
            "http://a".to_string(),
            "1.0".to_string(),
            None,
        );
        assert!(registry.all_healthy());
    }

    #[test]
    fn test_summary() {
        let registry = ServiceRegistry::new();
        registry.register(
            "A".to_string(),
            "http://a".to_string(),
            "1.0".to_string(),
            None,
        );
        let summary = registry.summary();
        assert_eq!(summary["total"], 1);
    }

    #[test]
    fn test_capabilities() {
        let registry = ServiceRegistry::new();
        let info = registry.register(
            "Test".to_string(),
            "http://localhost:8080".to_string(),
            "1.0.0".to_string(),
            Some(vec!["feature1".to_string()]),
        );
        assert_eq!(info.capabilities, vec!["feature1"]);
    }

    #[test]
    fn test_to_dict() {
        let info = ServiceInfo {
            name: "Test".to_string(),
            url: "http://localhost:8080".to_string(),
            version: "1.0.0".to_string(),
            status: ServiceStatus::Healthy,
            capabilities: vec![],
            registered_at: 0.0,
            last_heartbeat: 0.0,
        };
        let dict = info.to_dict();
        assert_eq!(dict["name"], "Test");
    }
}
