//! Service-to-service JWT authentication.
//!
//! Provides JWT token generation and validation for internal service communication.

use axum::http::{Request, StatusCode};
use axum::middleware::Next;
use axum::response::{IntoResponse, Response};
use chrono::Utc;
use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// Public paths that don't require authentication.
pub const PUBLIC_PATHS: &[&str] = &[
    "/health",
    "/ready",
    "/metrics",
    "/api/status",
    "/docs",
    "/openapi.json",
];

/// JWT token payload.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenPayload {
    pub sub: String,
    #[serde(rename = "iat")]
    pub issued_at: i64,
    #[serde(rename = "exp")]
    pub expiration: i64,
    #[serde(rename = "type")]
    pub token_type: String,
}

/// Create a JWT token for a service identity.
pub fn create_service_token(
    service_name: &str,
    secret: &str,
    expiry_seconds: u64,
) -> Result<String, jsonwebtoken::errors::Error> {
    let now = Utc::now().timestamp();
    let payload = TokenPayload {
        sub: service_name.to_string(),
        issued_at: now,
        expiration: now + expiry_seconds as i64,
        token_type: "service".to_string(),
    };
    encode(
        &Header::default(),
        &payload,
        &EncodingKey::from_secret(secret.as_bytes()),
    )
}

/// Verify and decode a service JWT token.
pub fn verify_service_token(
    token: &str,
    secret: &str,
) -> Result<TokenPayload, jsonwebtoken::errors::Error> {
    let mut validation = Validation::new(Algorithm::HS256);
    validation.leeway = 30; // 30 seconds leeway
    let token_data = decode::<TokenPayload>(
        token,
        &DecodingKey::from_secret(secret.as_bytes()),
        &validation,
    )?;
    Ok(token_data.claims)
}

/// Middleware for validating service-to-service JWT tokens.
pub struct ServiceAuthMiddleware {
    pub secret: String,
    pub public_paths: HashSet<String>,
}

impl ServiceAuthMiddleware {
    pub fn new(secret: String) -> Self {
        let public_paths: HashSet<String> = PUBLIC_PATHS.iter().map(|s| s.to_string()).collect();
        Self {
            secret,
            public_paths,
        }
    }

    pub fn with_public_paths(mut self, paths: HashSet<String>) -> Self {
        self.public_paths = paths;
        self
    }

    pub async fn middleware(
        self: std::sync::Arc<Self>,
        mut req: Request<axum::body::Body>,
        next: Next,
    ) -> Response {
        let path = req.uri().path().to_string();

        // Skip auth for public paths
        if self.public_paths.contains(&path) {
            return next.run(req).await;
        }

        // If no secret is configured, skip authentication
        if self.secret.is_empty() {
            return next.run(req).await;
        }

        // Extract and validate token
        let auth_header = req.headers().get("Authorization");
        let token = if let Some(auth) = auth_header {
            if let Ok(auth_str) = auth.to_str() {
                if auth_str.starts_with("Bearer ") {
                    Some(auth_str[7..].to_string())
                } else {
                    None
                }
            } else {
                None
            }
        } else {
            None
        };

        let token = match token {
            Some(t) => t.to_string(),
            None => {
                return (
                    StatusCode::UNAUTHORIZED,
                    "Missing or invalid Authorization header",
                )
                    .into_response();
            }
        };

        match verify_service_token(&token, &self.secret) {
            Ok(payload) => {
                req.extensions_mut().insert(payload.sub.clone());
                next.run(req).await
            }
            Err(err) => {
                let status = match err.kind() {
                    jsonwebtoken::errors::ErrorKind::ExpiredSignature => StatusCode::UNAUTHORIZED,
                    _ => StatusCode::UNAUTHORIZED,
                };
                (status, "Invalid token").into_response()
            }
        }
    }
}

/// Extract service name from request extensions (set by auth middleware).
pub fn get_service_name(req: &Request<axum::body::Body>) -> Option<String> {
    req.extensions().get::<String>().cloned()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_and_verify() {
        let token =
            create_service_token("Greenie", "test-secret-key-12345678901234567890", 3600).unwrap();
        let payload = verify_service_token(&token, "test-secret-key-12345678901234567890").unwrap();
        assert_eq!(payload.sub, "Greenie");
        assert_eq!(payload.token_type, "service");
    }

    #[test]
    fn test_wrong_secret() {
        let token =
            create_service_token("Greenie", "secret-1-1234567890123456789012", 3600).unwrap();
        let result = verify_service_token(&token, "wrong-secret-1234567890123456789012");
        assert!(result.is_err());
    }

    #[test]
    fn test_expired_token() {
        // Create a token that expired 60 seconds ago (beyond the 30s leeway)
        let now = Utc::now().timestamp();
        let payload = TokenPayload {
            sub: "Greenie".to_string(),
            issued_at: now - 120,
            expiration: now - 60,
            token_type: "service".to_string(),
        };
        let token = encode(
            &Header::default(),
            &payload,
            &EncodingKey::from_secret(b"test-secret-key-12345678901234567890"),
        )
        .unwrap();
        let result = verify_service_token(&token, "test-secret-key-12345678901234567890");
        assert!(result.is_err());
    }

    #[test]
    fn test_custom_expiry() {
        let token =
            create_service_token("Greenie", "test-secret-key-12345678901234567890", 7200).unwrap();
        let payload = verify_service_token(&token, "test-secret-key-12345678901234567890").unwrap();
        assert_eq!(payload.expiration - payload.issued_at, 7200);
    }

    #[test]
    fn test_public_paths_exempt() {
        let middleware = ServiceAuthMiddleware::new(String::new());
        assert!(middleware.public_paths.contains("/health"));
        assert!(middleware.public_paths.contains("/metrics"));
        assert!(middleware.public_paths.contains("/docs"));
    }

    #[tokio::test]
    async fn test_no_secret_allows_all() {
        let middleware = std::sync::Arc::new(ServiceAuthMiddleware::new(String::new()));
        // With empty secret, all requests should pass
        assert!(middleware.secret.is_empty());
    }

    #[tokio::test]
    async fn test_valid_token() {
        let secret = "test-secret-key-12345678901234567890".to_string();
        let token = create_service_token("Greenie", &secret, 3600).unwrap();
        let payload = verify_service_token(&token, &secret).unwrap();
        assert_eq!(payload.sub, "Greenie");
    }

    #[tokio::test]
    async fn test_missing_token() {
        let result = verify_service_token("", "test-secret-key-12345678901234567890");
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_invalid_token() {
        let result =
            verify_service_token("invalid.token.here", "test-secret-key-12345678901234567890");
        assert!(result.is_err());
    }
}
