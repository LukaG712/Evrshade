//! Alerting rules and evaluation for Sneaker.
//!
//! Provides configurable alert rules that evaluate against stored metrics
//! and logs, with support for Slack/Email/Telegram/webhook notifications.

use axum::Json;
use serde::{Deserialize, Serialize};

/// Alert rule definition.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertRule {
    pub id: String,
    pub name: String,
    pub description: String,
    pub metric_name: String,
    pub condition: String,
    pub threshold: f64,
    pub window_seconds: u64,
    pub enabled: bool,
    pub notification_channels: Vec<String>,
}

/// Alert state.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Alert {
    pub id: String,
    pub rule_id: String,
    pub rule_name: String,
    pub status: String,
    pub triggered_at: String,
    pub value: f64,
    pub threshold: f64,
}

/// In-memory alert rules store.
fn get_default_rules() -> Vec<AlertRule> {
    vec![
        AlertRule {
            id: "rule-1".to_string(),
            name: "High Error Rate".to_string(),
            description: "Alert when error rate exceeds 5%".to_string(),
            metric_name: "http_errors_total".to_string(),
            condition: "greater_than".to_string(),
            threshold: 5.0,
            window_seconds: 300,
            enabled: true,
            notification_channels: vec!["slack".to_string()],
        },
        AlertRule {
            id: "rule-2".to_string(),
            name: "High Latency".to_string(),
            description: "Alert when p99 latency exceeds 1000ms".to_string(),
            metric_name: "http_request_duration_p99".to_string(),
            condition: "greater_than".to_string(),
            threshold: 1000.0,
            window_seconds: 300,
            enabled: true,
            notification_channels: vec!["slack".to_string()],
        },
    ]
}

/// List all alerts.
pub async fn list_alerts() -> Json<Vec<Alert>> {
    Json(Vec::new())
}

/// List all alert rules.
pub async fn list_rules() -> Json<Vec<AlertRule>> {
    Json(get_default_rules())
}
