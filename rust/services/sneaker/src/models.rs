//! Data models for Sneaker observability service.

use serde::{Deserialize, Serialize};

/// A trace span from OTLP.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceSpan {
    pub trace_id: String,
    pub span_id: String,
    pub parent_span_id: Option<String>,
    pub name: String,
    pub duration_ms: Option<f64>,
    pub status: Option<String>,
    pub attributes: serde_json::Value,
    pub timestamp: String,
}

/// A metric data point from OTLP.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricPoint {
    pub name: String,
    pub value: f64,
    pub labels: serde_json::Value,
    pub timestamp: String,
}

/// A log entry from OTLP.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LogEntry {
    pub level: String,
    pub message: String,
    pub service: Option<String>,
    pub attributes: serde_json::Value,
    pub timestamp: String,
}

/// OTLP stats response.
#[derive(Serialize)]
pub struct OtlpStats {
    pub traces_received: u64,
    pub metrics_received: u64,
    pub logs_received: u64,
    pub traces_dropped: u64,
    pub metrics_dropped: u64,
    pub logs_dropped: u64,
}
