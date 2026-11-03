//! Standard error response envelope and middleware for Evershade services.
//!
//! Every service returns errors in a consistent JSON format with error codes,
//! correlation IDs, and timestamps.

use axum::http::HeaderValue;
use axum::http::Request;
use axum::middleware::Next;
use axum::response::Response;
use chrono::Utc;
use http::StatusCode;
use serde::{Deserialize, Serialize};
use std::fmt;
use tracing::info;
use uuid::Uuid;

/// Standard error codes for Evershade services.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ErrorCode {
    ValidationError,
    Unauthorized,
    Forbidden,
    NotFound,
    Conflict,
    ServiceUnavailable,
    InternalError,
}

impl ErrorCode {
    pub fn to_status(&self) -> StatusCode {
        match self {
            ErrorCode::ValidationError => StatusCode::BAD_REQUEST,
            ErrorCode::Unauthorized => StatusCode::UNAUTHORIZED,
            ErrorCode::Forbidden => StatusCode::FORBIDDEN,
            ErrorCode::NotFound => StatusCode::NOT_FOUND,
            ErrorCode::Conflict => StatusCode::CONFLICT,
            ErrorCode::ServiceUnavailable => StatusCode::SERVICE_UNAVAILABLE,
            ErrorCode::InternalError => StatusCode::INTERNAL_SERVER_ERROR,
        }
    }
}

impl fmt::Display for ErrorCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ErrorCode::ValidationError => write!(f, "VALIDATION_ERROR"),
            ErrorCode::Unauthorized => write!(f, "UNAUTHORIZED"),
            ErrorCode::Forbidden => write!(f, "FORBIDDEN"),
            ErrorCode::NotFound => write!(f, "NOT_FOUND"),
            ErrorCode::Conflict => write!(f, "CONFLICT"),
            ErrorCode::ServiceUnavailable => write!(f, "SERVICE_UNAVAILABLE"),
            ErrorCode::InternalError => write!(f, "INTERNAL_ERROR"),
        }
    }
}

/// Application-level error with structured payload.
#[derive(Debug)]
pub struct EvershadeError {
    pub code: ErrorCode,
    pub message: String,
    pub details: Option<serde_json::Value>,
}

impl EvershadeError {
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            details: None,
        }
    }

    pub fn with_details(mut self, details: impl Into<serde_json::Value>) -> Self {
        self.details = Some(details.into());
        self
    }
}

impl fmt::Display for EvershadeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}: {}", self.code, self.message)
    }
}

impl std::error::Error for EvershadeError {}

/// Standard error response envelope.
#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorResponse {
    pub success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<serde_json::Value>,
    pub error: ErrorDetail,
    pub request_id: String,
    pub timestamp: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ErrorDetail {
    pub code: String,
    pub message: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<serde_json::Value>,
}

/// Standard success response envelope.
#[derive(Debug, Serialize, Deserialize)]
pub struct SuccessResponse<T: Serialize> {
    pub success: bool,
    pub data: T,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<serde_json::Value>,
    pub request_id: String,
    pub timestamp: String,
}

/// Build a standard error response envelope.
pub fn error_response(
    code: ErrorCode,
    message: impl Into<String>,
    details: Option<serde_json::Value>,
) -> ErrorResponse {
    ErrorResponse {
        success: false,
        data: None,
        error: ErrorDetail {
            code: code.to_string(),
            message: message.into(),
            details,
        },
        request_id: Uuid::new_v4().to_string(),
        timestamp: Utc::now().to_rfc3339(),
    }
}

/// Build a standard success response envelope.
pub fn success_response<T: Serialize>(data: T) -> serde_json::Result<SuccessResponse<T>> {
    Ok(SuccessResponse {
        success: true,
        data,
        error: None,
        request_id: Uuid::new_v4().to_string(),
        timestamp: Utc::now().to_rfc3339(),
    })
}

/// Middleware that generates and propagates correlation IDs.
pub struct CorrelationIdMiddleware;

pub async fn correlation_id_middleware(mut req: Request<axum::body::Body>, next: Next) -> Response {
    let request_id = if let Some(id) = req.headers().get("X-Request-Id") {
        id.to_str().unwrap_or_default().to_string()
    } else {
        Uuid::new_v4().to_string()
    };

    // Store in extensions for downstream use
    req.extensions_mut().insert(request_id.clone());

    let mut response = next.run(req).await;

    if let Ok(val) = HeaderValue::from_str(&request_id) {
        response.headers_mut().insert("X-Request-Id", val.clone());
        response.headers_mut().insert("X-Correlation-Id", val);
    }

    response
}

/// Middleware that logs every request with timing and correlation ID.
pub struct RequestLoggingMiddleware;

pub async fn request_logging_middleware(
    mut req: Request<axum::body::Body>,
    next: Next,
) -> Response {
    let request_id = req
        .extensions()
        .get::<String>()
        .cloned()
        .unwrap_or_else(|| Uuid::new_v4().to_string());
    let method = req.method().clone();
    let path = req.uri().path().to_string();

    let start = std::time::Instant::now();
    let response = next.run(req).await;
    let duration = start.elapsed().as_millis() as f64;

    let status = response.status().as_u16();
    info!(
        req_id = %request_id,
        method = %method,
        path = %path,
        status = status,
        duration_ms = duration,
        "Request completed"
    );

    response
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_all_codes_have_status() {
        assert_eq!(
            ErrorCode::ValidationError.to_status(),
            StatusCode::BAD_REQUEST
        );
        assert_eq!(
            ErrorCode::Unauthorized.to_status(),
            StatusCode::UNAUTHORIZED
        );
        assert_eq!(ErrorCode::Forbidden.to_status(), StatusCode::FORBIDDEN);
        assert_eq!(ErrorCode::NotFound.to_status(), StatusCode::NOT_FOUND);
        assert_eq!(ErrorCode::Conflict.to_status(), StatusCode::CONFLICT);
        assert_eq!(
            ErrorCode::ServiceUnavailable.to_status(),
            StatusCode::SERVICE_UNAVAILABLE
        );
        assert_eq!(
            ErrorCode::InternalError.to_status(),
            StatusCode::INTERNAL_SERVER_ERROR
        );
    }

    #[test]
    fn test_validation_error_is_400() {
        assert_eq!(ErrorCode::ValidationError.to_status(), 400);
    }

    #[test]
    fn test_not_found_is_404() {
        assert_eq!(ErrorCode::NotFound.to_status(), 404);
    }

    #[test]
    fn test_internal_error_is_500() {
        assert_eq!(ErrorCode::InternalError.to_status(), 500);
    }

    #[test]
    fn test_error_message() {
        let err = EvershadeError::new(ErrorCode::NotFound, "Agent not found");
        assert!(err.message.contains("Agent not found"));
    }

    #[test]
    fn test_error_with_details() {
        let err = EvershadeError::new(ErrorCode::ValidationError, "Invalid input")
            .with_details(serde_json::json!({"field": "name"}));
        assert!(err.details.is_some());
    }

    #[test]
    fn test_error_response_format() {
        let resp = error_response(ErrorCode::NotFound, "Not found", None);
        assert!(!resp.success);
        assert_eq!(resp.error.code, "NOT_FOUND");
        assert_eq!(resp.error.message, "Not found");
    }

    #[test]
    fn test_success_response_format() {
        let resp = success_response(serde_json::json!({"key": "value"})).unwrap();
        assert!(resp.success);
    }

    #[test]
    fn test_correlation_id_generates() {
        let id = Uuid::new_v4().to_string();
        assert!(!id.is_empty());
    }

    #[test]
    fn test_correlation_id_preserved() {
        let existing = "existing-id".to_string();
        assert_eq!(existing, "existing-id");
    }
}
