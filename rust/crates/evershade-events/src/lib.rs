//! Shared event contracts for Evershade inter-service communication.
//!
//! Defines typed event classes and an in-memory event bus for pub/sub
//! communication between services.

use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use uuid::Uuid;

/// Standard event types for Evershade.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum EventType {
    AgentCreated,
    AgentUpdated,
    AgentDeleted,
    MissionStarted,
    MissionCompleted,
    MissionFailed,
    MissionCancelled,
    TaskCreated,
    TaskStarted,
    TaskCompleted,
    TaskFailed,
    NotificationQueued,
    NotificationSent,
    NotificationFailed,
    ServiceRegistered,
    ServiceDeregistered,
    ServiceHealthy,
    ServiceUnhealthy,
}

impl std::fmt::Display for EventType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            EventType::AgentCreated => write!(f, "agent.created"),
            EventType::AgentUpdated => write!(f, "agent.updated"),
            EventType::AgentDeleted => write!(f, "agent.deleted"),
            EventType::MissionStarted => write!(f, "mission.started"),
            EventType::MissionCompleted => write!(f, "mission.completed"),
            EventType::MissionFailed => write!(f, "mission.failed"),
            EventType::MissionCancelled => write!(f, "mission.cancelled"),
            EventType::TaskCreated => write!(f, "task.created"),
            EventType::TaskStarted => write!(f, "task.started"),
            EventType::TaskCompleted => write!(f, "task.completed"),
            EventType::TaskFailed => write!(f, "task.failed"),
            EventType::NotificationQueued => write!(f, "notification.queued"),
            EventType::NotificationSent => write!(f, "notification.sent"),
            EventType::NotificationFailed => write!(f, "notification.failed"),
            EventType::ServiceRegistered => write!(f, "service.registered"),
            EventType::ServiceDeregistered => write!(f, "service.deregistered"),
            EventType::ServiceHealthy => write!(f, "service.healthy"),
            EventType::ServiceUnhealthy => write!(f, "service.unhealthy"),
        }
    }
}

/// Base event class for all Evershade events.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Event {
    pub id: String,
    pub r#type: String,
    pub timestamp: f64,
    pub source: String,
    pub correlation_id: String,
    pub version: String,
    pub payload: serde_json::Value,
}

impl Event {
    pub fn new(r#type: String, payload: serde_json::Value, source: String) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            r#type,
            timestamp: Utc::now().timestamp_millis() as f64 / 1000.0,
            source,
            correlation_id: Uuid::new_v4().to_string(),
            version: "1.0".to_string(),
            payload,
        }
    }

    pub fn with_correlation_id(mut self, correlation_id: String) -> Self {
        self.correlation_id = correlation_id;
        self
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string(self).unwrap_or_default()
    }

    pub fn from_json(data: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(data)
    }
}

/// Typed event for agent creation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentCreatedEvent {
    pub agent_id: String,
    pub name: String,
    pub description: String,
}

impl AgentCreatedEvent {
    pub fn to_event(&self, source: String) -> Event {
        Event::new(
            EventType::AgentCreated.to_string(),
            serde_json::to_value(self).unwrap(),
            source,
        )
    }
}

/// Typed event for mission start.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MissionStartedEvent {
    pub mission_id: String,
    pub agent_id: String,
    pub name: String,
}

impl MissionStartedEvent {
    pub fn to_event(&self, source: String) -> Event {
        Event::new(
            EventType::MissionStarted.to_string(),
            serde_json::to_value(self).unwrap(),
            source,
        )
    }
}

/// Typed event for task completion.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskCompletedEvent {
    pub task_id: String,
    pub worker_id: String,
    pub exit_code: i32,
}

impl TaskCompletedEvent {
    pub fn to_event(&self, source: String) -> Event {
        Event::new(
            EventType::TaskCompleted.to_string(),
            serde_json::to_value(self).unwrap(),
            source,
        )
    }
}

/// Typed event for notification sent.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NotificationSentEvent {
    pub notification_id: String,
    pub channel: String,
    pub recipient: String,
}

impl NotificationSentEvent {
    pub fn to_event(&self, source: String) -> Event {
        Event::new(
            EventType::NotificationSent.to_string(),
            serde_json::to_value(self).unwrap(),
            source,
        )
    }
}

/// Event handler type alias.
pub type EventHandler = Arc<dyn Fn(Event) + Send + Sync>;

/// Event bus for publishing and subscribing to events.
#[derive(Clone)]
pub struct EventBus {
    handlers: Arc<Mutex<HashMap<String, Vec<EventHandler>>>>,
}

impl EventBus {
    pub fn new() -> Self {
        Self {
            handlers: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub async fn subscribe(&self, event_type: String, handler: EventHandler) {
        let mut handlers = self.handlers.lock().unwrap();
        handlers
            .entry(event_type)
            .or_insert_with(Vec::new)
            .push(handler);
    }

    pub async fn publish(&self, event: Event) {
        let handlers_map = self.handlers.lock().unwrap().clone();
        let event_type = event.r#type.clone();

        for (pattern, handler_list) in handlers_map.iter() {
            if Self::matches(pattern, &event_type) {
                for handler in handler_list {
                    let e = event.clone();
                    let h = handler.clone();
                    std::thread::spawn(move || {
                        h(e);
                    });
                }
            }
        }
    }

    fn matches(pattern: &str, event_type: &str) -> bool {
        if pattern == event_type {
            return true;
        }
        if let Some(prefix) = pattern.strip_suffix(".*") {
            return event_type.starts_with(&format!("{}.{}", prefix, ""));
        }
        false
    }
}

impl Default for EventBus {
    fn default() -> Self {
        Self::new()
    }
}

/// Publish events via HTTP to a central event collector.
pub struct HttpEventPublisher {
    collector_url: String,
    client: reqwest::Client,
}

impl HttpEventPublisher {
    pub fn new(collector_url: String) -> Self {
        Self {
            collector_url: collector_url.trim_end_matches('/').to_string(),
            client: reqwest::Client::builder()
                .timeout(std::time::Duration::from_secs(10))
                .build()
                .unwrap(),
        }
    }

    pub async fn publish(&self, event: &Event) -> Result<(), reqwest::Error> {
        let _ = self
            .client
            .post(format!("{}/api/events", self.collector_url))
            .header("Content-Type", "application/json")
            .body(event.to_json())
            .send()
            .await?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_event_creation() {
        let event = Event::new(
            "agent.created".to_string(),
            serde_json::json!({"id": "123"}),
            "Greenie".to_string(),
        );
        assert_eq!(event.r#type, "agent.created");
        assert_eq!(event.source, "Greenie");
    }

    #[test]
    fn test_event_to_json() {
        let event = Event::new(
            "agent.created".to_string(),
            serde_json::json!({"id": "123"}),
            "Greenie".to_string(),
        );
        let json = event.to_json();
        assert!(json.contains("agent.created"));
    }

    #[test]
    fn test_event_from_json() {
        let event = Event::new(
            "agent.created".to_string(),
            serde_json::json!({"id": "123"}),
            "Greenie".to_string(),
        );
        let json = event.to_json();
        let parsed = Event::from_json(&json).unwrap();
        assert_eq!(parsed.r#type, "agent.created");
    }

    #[test]
    fn test_event_type_display() {
        assert_eq!(EventType::AgentCreated.to_string(), "agent.created");
        assert_eq!(EventType::TaskCompleted.to_string(), "task.completed");
    }

    #[test]
    fn test_agent_created_event() {
        let evt = AgentCreatedEvent {
            agent_id: "abc-123".to_string(),
            name: "My Agent".to_string(),
            description: "Test agent".to_string(),
        };
        let event = evt.to_event("Greenie".to_string());
        assert_eq!(event.r#type, "agent.created");
    }
}
