//! OTLP ingestion endpoints for traces, metrics, and logs.
//!
//! Accepts JSON-encoded OTLP data, redacts secrets in attributes,
//! stores in SQLite, and tracks statistics.

use axum::{extract::State, Json};
use regex::Regex;
use sea_orm::{ConnectionTrait, Statement};
use std::sync::atomic::{AtomicU64, Ordering};
use tracing::info;

use crate::{
    models::{LogEntry, MetricPoint, OtlpStats, TraceSpan},
    AppState,
};

/// Max entries per OTLP call to prevent memory exhaustion.
const MAX_OTLP_ENTRIES_PER_CALL: usize = 1000;

/// Counters for OTLP stats.
static TRACES_RECEIVED: AtomicU64 = AtomicU64::new(0);
static METRICS_RECEIVED: AtomicU64 = AtomicU64::new(0);
static LOGS_RECEIVED: AtomicU64 = AtomicU64::new(0);
static TRACES_DROPPED: AtomicU64 = AtomicU64::new(0);
static METRICS_DROPPED: AtomicU64 = AtomicU64::new(0);
static LOGS_DROPPED: AtomicU64 = AtomicU64::new(0);

/// Patterns that indicate a value is likely a secret.
lazy_static::lazy_static! {
    static ref SECRET_PATTERNS: Vec<Regex> = vec![
        Regex::new(r"(?:^|[^A-Za-z0-9_])(?:api[_-]?key|apikey|token|secret|password|passwd|pwd|auth|credential|access[_-]?key|private[_-]?key)(?:[^A-Za-z0-9_]|$)").unwrap(),
        Regex::new(r"(?:^|[^A-Za-z0-9_])(?:aws|azure|gcp|google)[_-]?(?:access|secret|key|token|credential)(?:[^A-Za-z0-9_]|$)").unwrap(),
    ];
    static ref INSECURE_VALUES: std::collections::HashSet<&'static str> = [
        "changeme", "password", "admin", "secret", "default", "test",
        "your-api-key", "your-api-key-here", "your-secret-here",
        "insert-key-here", "replace-me", "xxx", "12345",
    ].iter().cloned().collect();
}

fn is_secret_key(key: &str) -> bool {
    SECRET_PATTERNS.iter().any(|p| p.is_match(key))
}

fn should_redact_value(value: &str) -> bool {
    let lower = value.trim().to_lowercase();
    if INSECURE_VALUES.contains(lower.as_str()) {
        return true;
    }
    value.len() > 30 && Regex::new(r"^[A-Za-z0-9+/=_\-]+$").unwrap().is_match(value)
}

fn redact_secrets_in_attributes(attributes: Option<&serde_json::Value>) -> serde_json::Value {
    let attrs = attributes.unwrap_or(&serde_json::json!([])).clone();
    match attrs {
        serde_json::Value::Array(attrs) => {
            let redacted: Vec<serde_json::Value> = attrs
                .iter()
                .map(|attr| {
                    if let Some(obj) = attr.as_object() {
                        let mut new_obj = obj.clone();
                        let key = new_obj
                            .get("key")
                            .and_then(|k| k.as_str())
                            .map(|s| s.to_string());
                        if let Some(key_str) = key {
                            if let Some(value) = new_obj.get_mut("value") {
                                if let Some(vobj) = value.as_object_mut() {
                                    if let Some(str_val) =
                                        vobj.get("stringValue").and_then(|s| s.as_str())
                                    {
                                        if is_secret_key(&key_str) || should_redact_value(str_val) {
                                            vobj.insert(
                                                "stringValue".to_string(),
                                                serde_json::json!("**REDACTED**"),
                                            );
                                        }
                                    }
                                }
                            }
                        }
                        serde_json::Value::Object(new_obj)
                    } else {
                        attr.clone()
                    }
                })
                .collect();
            serde_json::Value::Array(redacted)
        }
        _ => attrs,
    }
}

/// Receive traces via OTLP protocol.
pub async fn receive_traces(
    state: State<AppState>,
    body: axum::body::Bytes,
) -> axum::response::Response {
    let data = body.to_vec();

    let spans: Vec<TraceSpan> = if data.is_empty() {
        Vec::new()
    } else {
        match serde_json::from_slice::<serde_json::Value>(&data) {
            Ok(json_val) => {
                // Parse OTLP JSON format
                let mut spans = Vec::new();
                if let Some(resource_spans) =
                    json_val.get("resourceSpans").and_then(|v| v.as_array())
                {
                    for rs in resource_spans {
                        if let Some(scope_spans) = rs.get("scopeSpans").and_then(|v| v.as_array()) {
                            for ss in scope_spans {
                                if let Some(spans_arr) = ss.get("spans").and_then(|v| v.as_array())
                                {
                                    for span in spans_arr {
                                        let trace_id = span
                                            .get("traceId")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("")
                                            .to_string();
                                        let span_id = span
                                            .get("spanId")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("")
                                            .to_string();
                                        let parent_span_id = span
                                            .get("parentSpanId")
                                            .and_then(|v| v.as_str())
                                            .map(|s| s.to_string());
                                        let name = span
                                            .get("name")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("")
                                            .to_string();
                                        let attributes =
                                            redact_secrets_in_attributes(span.get("attributes"));
                                        let timestamp = chrono::Utc::now().to_rfc3339();

                                        spans.push(TraceSpan {
                                            trace_id,
                                            span_id,
                                            parent_span_id,
                                            name,
                                            duration_ms: None,
                                            status: None,
                                            attributes,
                                            timestamp,
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                spans
            }
            Err(_) => {
                // Protobuf — log and skip parsing
                info!("Received {} bytes of OTLP protobuf traces", data.len());
                Vec::new()
            }
        }
    };

    // Enforce size limit
    let total = spans.len();
    let limited: Vec<TraceSpan> = spans.into_iter().take(MAX_OTLP_ENTRIES_PER_CALL).collect();
    let dropped = total.saturating_sub(MAX_OTLP_ENTRIES_PER_CALL);
    TRACES_RECEIVED.fetch_add(limited.len() as u64, Ordering::Relaxed);
    if dropped > 0 {
        TRACES_DROPPED.fetch_add(dropped as u64, Ordering::Relaxed);
    }

    // Store in SQLite
    for span in &limited {
        let parent_span_id = span.parent_span_id.as_deref().unwrap_or("");
        let attributes_json = serde_json::to_string(&span.attributes).unwrap_or_default();
        state.db.execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT INTO traces (trace_id, span_id, parent_span_id, name, attributes, timestamp) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')",
                span.trace_id, span.span_id, parent_span_id, span.name, attributes_json, span.timestamp
            ),
        )).await.ok();
    }

    info!(
        "Received {} spans via OTLP{}",
        limited.len(),
        if dropped > 0 {
            format!(" (dropped {} due to limit)", dropped)
        } else {
            String::new()
        }
    );

    axum::response::Response::new(axum::body::Body::empty())
}

/// Receive metrics via OTLP protocol.
pub async fn receive_metrics(
    state: State<AppState>,
    body: axum::body::Bytes,
) -> axum::response::Response {
    let data = body.to_vec();

    let metrics: Vec<MetricPoint> = if data.is_empty() {
        Vec::new()
    } else {
        match serde_json::from_slice::<serde_json::Value>(&data) {
            Ok(json_val) => {
                let mut metrics = Vec::new();
                if let Some(resource_metrics) =
                    json_val.get("resourceMetrics").and_then(|v| v.as_array())
                {
                    for rm in resource_metrics {
                        if let Some(scope_metrics) =
                            rm.get("scopeMetrics").and_then(|v| v.as_array())
                        {
                            for sm in scope_metrics {
                                if let Some(metrics_arr) =
                                    sm.get("metrics").and_then(|v| v.as_array())
                                {
                                    for metric in metrics_arr {
                                        let name = metric
                                            .get("name")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("")
                                            .to_string();
                                        let timestamp = chrono::Utc::now().to_rfc3339();

                                        // Extract value from various OTLP metric types
                                        let value = metric
                                            .get("gauge")
                                            .and_then(|g| g.get("dataPoints"))
                                            .or_else(|| {
                                                metric.get("sum").and_then(|s| s.get("dataPoints"))
                                            })
                                            .and_then(|dp| dp.as_array())
                                            .and_then(|dp| dp.first())
                                            .and_then(|dp| dp.get("asDouble"))
                                            .or_else(|| {
                                                metric
                                                    .get("gauge")
                                                    .and_then(|g| g.get("dataPoints"))
                                                    .or_else(|| {
                                                        metric
                                                            .get("sum")
                                                            .and_then(|s| s.get("dataPoints"))
                                                    })
                                                    .and_then(|dp| dp.as_array())
                                                    .and_then(|dp| dp.first())
                                                    .and_then(|dp| dp.get("asInt"))
                                            })
                                            .map(|v| v.as_f64().unwrap_or(0.0))
                                            .unwrap_or(0.0);

                                        let labels =
                                            redact_secrets_in_attributes(metric.get("attributes"));

                                        metrics.push(MetricPoint {
                                            name,
                                            value,
                                            labels,
                                            timestamp,
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                metrics
            }
            Err(_) => {
                info!("Received {} bytes of OTLP protobuf metrics", data.len());
                Vec::new()
            }
        }
    };

    let total = metrics.len();
    let limited: Vec<MetricPoint> = metrics
        .into_iter()
        .take(MAX_OTLP_ENTRIES_PER_CALL)
        .collect();
    let dropped = total.saturating_sub(MAX_OTLP_ENTRIES_PER_CALL);
    METRICS_RECEIVED.fetch_add(limited.len() as u64, Ordering::Relaxed);
    if dropped > 0 {
        METRICS_DROPPED.fetch_add(dropped as u64, Ordering::Relaxed);
    }

    for metric in &limited {
        let labels_json = serde_json::to_string(&metric.labels).unwrap_or_default();
        state.db.execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT INTO metrics (name, value, labels, timestamp) VALUES ('{}', {}, '{}', '{}')",
                metric.name, metric.value, labels_json, metric.timestamp
            ),
        )).await.ok();
    }

    info!(
        "Received {} metrics via OTLP{}",
        limited.len(),
        if dropped > 0 {
            format!(" (dropped {} due to limit)", dropped)
        } else {
            String::new()
        }
    );

    axum::response::Response::new(axum::body::Body::empty())
}

/// Receive logs via OTLP protocol.
pub async fn receive_logs(
    state: State<AppState>,
    body: axum::body::Bytes,
) -> axum::response::Response {
    let data = body.to_vec();

    let logs: Vec<LogEntry> = if data.is_empty() {
        Vec::new()
    } else {
        match serde_json::from_slice::<serde_json::Value>(&data) {
            Ok(json_val) => {
                let mut logs = Vec::new();
                if let Some(resource_logs) = json_val.get("resourceLogs").and_then(|v| v.as_array())
                {
                    for rl in resource_logs {
                        if let Some(scope_logs) = rl.get("scopeLogs").and_then(|v| v.as_array()) {
                            for sl in scope_logs {
                                if let Some(logs_arr) =
                                    sl.get("logRecords").and_then(|v| v.as_array())
                                {
                                    for log in logs_arr {
                                        let body_val = log
                                            .get("body")
                                            .cloned()
                                            .unwrap_or(serde_json::json!(""));
                                        let message = body_val
                                            .get("stringValue")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or(&body_val.to_string())
                                            .to_string();
                                        let severity = log
                                            .get("severityText")
                                            .and_then(|v| v.as_str())
                                            .unwrap_or("INFO")
                                            .to_string();
                                        let service = log.get("attributes").and_then(|attrs| {
                                            if let Some(arr) = attrs.as_array() {
                                                for attr in arr {
                                                    if let Some(obj) = attr.as_object() {
                                                        if let Some(key) =
                                                            obj.get("key").and_then(|k| k.as_str())
                                                        {
                                                            if key == "service.name" {
                                                                if let Some(val) =
                                                                    obj.get("value").and_then(|v| {
                                                                        v.get("stringValue")
                                                                    })
                                                                {
                                                                    return Some(
                                                                        val.as_str()
                                                                            .unwrap_or("")
                                                                            .to_string(),
                                                                    );
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                            None
                                        });
                                        let attributes =
                                            redact_secrets_in_attributes(log.get("attributes"));
                                        let timestamp = chrono::Utc::now().to_rfc3339();

                                        logs.push(LogEntry {
                                            level: severity,
                                            message,
                                            service,
                                            attributes,
                                            timestamp,
                                        });
                                    }
                                }
                            }
                        }
                    }
                }
                logs
            }
            Err(_) => {
                info!("Received {} bytes of OTLP protobuf logs", data.len());
                Vec::new()
            }
        }
    };

    let total = logs.len();
    let limited: Vec<LogEntry> = logs.into_iter().take(MAX_OTLP_ENTRIES_PER_CALL).collect();
    let dropped = total.saturating_sub(MAX_OTLP_ENTRIES_PER_CALL);
    LOGS_RECEIVED.fetch_add(limited.len() as u64, Ordering::Relaxed);
    if dropped > 0 {
        LOGS_DROPPED.fetch_add(dropped as u64, Ordering::Relaxed);
    }

    for log in &limited {
        let service_val = log.service.as_deref().unwrap_or("");
        let attributes_json = serde_json::to_string(&log.attributes).unwrap_or_default();
        state.db.execute(Statement::from_string(
            state.db.get_database_backend(),
            format!(
                "INSERT INTO logs (level, message, service, attributes, timestamp) VALUES ('{}', '{}', '{}', '{}', '{}')",
                log.level, log.message, service_val, attributes_json, log.timestamp
            ),
        )).await.ok();
    }

    info!(
        "Received {} logs via OTLP{}",
        limited.len(),
        if dropped > 0 {
            format!(" (dropped {} due to limit)", dropped)
        } else {
            String::new()
        }
    );

    axum::response::Response::new(axum::body::Body::empty())
}

/// Get OTLP stats.
pub async fn get_otlp_stats() -> Json<OtlpStats> {
    Json(OtlpStats {
        traces_received: TRACES_RECEIVED.load(Ordering::Relaxed),
        metrics_received: METRICS_RECEIVED.load(Ordering::Relaxed),
        logs_received: LOGS_RECEIVED.load(Ordering::Relaxed),
        traces_dropped: TRACES_DROPPED.load(Ordering::Relaxed),
        metrics_dropped: METRICS_DROPPED.load(Ordering::Relaxed),
        logs_dropped: LOGS_DROPPED.load(Ordering::Relaxed),
    })
}
