//! Centralized configuration with environment variable loading and validation.
//!
//! Every Evershade service loads its configuration through this module.
//! It provides environment variable loading with type coercion and schema validation.

use serde::{Deserialize, Serialize};
use std::fmt;

/// Deployment environment.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum Environment {
    Dev,
    Staging,
    Prod,
}

impl fmt::Display for Environment {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Environment::Dev => write!(f, "dev"),
            Environment::Staging => write!(f, "staging"),
            Environment::Prod => write!(f, "prod"),
        }
    }
}

impl Default for Environment {
    fn default() -> Self {
        Environment::Dev
    }
}

/// Database connection settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub pool_size: u32,
    pub max_overflow: u32,
    pub echo: bool,
    pub wal_mode: bool,
}

impl Default for DatabaseConfig {
    fn default() -> Self {
        Self {
            url: "sqlite:///./app.db".to_string(),
            pool_size: 5,
            max_overflow: 10,
            echo: false,
            wal_mode: true,
        }
    }
}

impl DatabaseConfig {
    pub fn new() -> Self {
        let mut cfg = Self::default();
        if let Ok(url) = std::env::var("DB_URL") {
            cfg.url = url;
        }
        if let Ok(pool_size) = std::env::var("DB_POOL_SIZE") {
            if let Ok(v) = pool_size.parse::<u32>() {
                cfg.pool_size = v;
            }
        }
        if let Ok(echo) = std::env::var("DB_ECHO") {
            cfg.echo = echo == "true" || echo == "1";
        }
        cfg
    }

    pub fn validate(&self) -> Result<(), String> {
        if self.url.is_empty() {
            return Err("Database URL must not be empty".to_string());
        }
        if self.pool_size < 1 || self.pool_size > 20 {
            return Err("Pool size must be between 1 and 20".to_string());
        }
        Ok(())
    }
}

/// OpenTelemetry and metrics configuration.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryConfig {
    pub otlp_endpoint: String,
    pub enabled: bool,
    pub sample_rate: f64,
}

impl Default for TelemetryConfig {
    fn default() -> Self {
        Self {
            otlp_endpoint: String::new(),
            enabled: false,
            sample_rate: 1.0,
        }
    }
}

impl TelemetryConfig {
    pub fn new() -> Self {
        let mut cfg = Self::default();
        if let Ok(endpoint) = std::env::var("OTEL_OTLP_ENDPOINT") {
            cfg.otlp_endpoint = endpoint;
        }
        if let Ok(enabled) = std::env::var("OTEL_ENABLED") {
            cfg.enabled = enabled == "true" || enabled == "1";
        }
        if let Ok(sample_rate) = std::env::var("OTEL_SAMPLE_RATE") {
            if let Ok(v) = sample_rate.parse::<f64>() {
                cfg.sample_rate = v.clamp(0.0, 1.0);
            }
        }
        cfg
    }

    pub fn is_configured(&self) -> bool {
        !self.otlp_endpoint.is_empty() || self.enabled
    }
}

/// Service-to-service authentication settings.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthConfig {
    pub jwt_secret: String,
    pub token_expiry_seconds: u64,
    pub enabled: bool,
}

impl Default for AuthConfig {
    fn default() -> Self {
        Self {
            jwt_secret: String::new(),
            token_expiry_seconds: 3600,
            enabled: false,
        }
    }
}

impl AuthConfig {
    pub fn new() -> Self {
        let mut cfg = Self::default();
        if let Ok(secret) = std::env::var("AUTH_JWT_SECRET") {
            cfg.jwt_secret = secret;
        }
        if let Ok(expiry) = std::env::var("AUTH_TOKEN_EXPIRY_SECONDS") {
            if let Ok(v) = expiry.parse::<u64>() {
                cfg.token_expiry_seconds = v.clamp(60, 86400);
            }
        }
        if let Ok(enabled) = std::env::var("AUTH_ENABLED") {
            cfg.enabled = enabled == "true" || enabled == "1";
        }
        cfg
    }

    pub fn validate(&self) -> Result<(), String> {
        if self.enabled && self.jwt_secret.is_empty() {
            return Err("JWT secret is required when auth is enabled".to_string());
        }
        Ok(())
    }
}

/// Main configuration for an Evershade service.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceConfig {
    pub service_name: String,
    pub port: u16,
    pub version: String,
    pub environment: Environment,
    pub log_level: String,
    pub host: String,
    pub api_key: String,
    pub slinker_url: String,
    pub trapper_url: String,
    pub gobber_url: String,
    pub sneaker_url: String,
    pub hider_url: String,
    pub poltergeist_url: String,
    pub shrewd_url: String,
    pub greenie_url: String,
    pub database: DatabaseConfig,
    pub telemetry: TelemetryConfig,
    pub auth: AuthConfig,
}

impl ServiceConfig {
    pub fn new(service_name: String, port: u16) -> Self {
        let version = std::env::var("EVERSHADE_VERSION").unwrap_or_else(|_| "2.0.0".to_string());
        let environment: Environment = std::env::var("EVERSHADE_ENVIRONMENT")
            .ok()
            .and_then(|v| match v.as_str() {
                "staging" => Some(Environment::Staging),
                "prod" => Some(Environment::Prod),
                _ => Some(Environment::Dev),
            })
            .unwrap_or_default();
        let log_level = std::env::var("EVERSHADE_LOG_LEVEL").unwrap_or_else(|_| "INFO".to_string());
        let host = std::env::var("EVERSHADE_HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
        let api_key = std::env::var("EVERSHADE_API_KEY").unwrap_or_default();

        Self {
            service_name,
            port,
            version,
            environment,
            log_level,
            host,
            api_key,
            slinker_url: std::env::var("EVERSHADE_SLINKER_URL")
                .unwrap_or_else(|_| "http://Slinker:8000".to_string()),
            trapper_url: std::env::var("EVERSHADE_TRAPPER_URL")
                .unwrap_or_else(|_| "http://Trapper-api:3000".to_string()),
            gobber_url: std::env::var("EVERSHADE_GOBBER_URL")
                .unwrap_or_else(|_| "http://Gobber:8085".to_string()),
            sneaker_url: std::env::var("EVERSHADE_SNEAKER_URL")
                .unwrap_or_else(|_| "http://Sneaker:8086".to_string()),
            hider_url: std::env::var("EVERSHADE_HIDER_URL")
                .unwrap_or_else(|_| "http://Hider:8087".to_string()),
            poltergeist_url: std::env::var("EVERSHADE_POLTERGEIST_URL")
                .unwrap_or_else(|_| "http://Poltergeist:8088".to_string()),
            shrewd_url: std::env::var("EVERSHADE_SHREWD_URL")
                .unwrap_or_else(|_| "http://Shrewd:8089".to_string()),
            greenie_url: std::env::var("EVERSHADE_GREENIE_URL")
                .unwrap_or_else(|_| "http://Greenie:8080".to_string()),
            database: DatabaseConfig::new(),
            telemetry: TelemetryConfig::new(),
            auth: AuthConfig::new(),
        }
    }

    /// Validate configuration and return any warnings.
    pub fn validate(&self) -> Result<Vec<String>, String> {
        let mut warnings = Vec::new();

        if self.service_name.trim().is_empty() {
            return Err("Service name must not be empty".to_string());
        }

        let valid_names = [
            "Greenie",
            "Slinker",
            "Trapper",
            "Gobber",
            "Sneaker",
            "Hider",
            "Poltergeist",
            "Shrewd",
            "Slammer",
            "Speedy",
        ];
        if !valid_names.contains(&self.service_name.as_str()) {
            warnings.push(format!(
                "Unknown service name '{}', expected one of {:?}",
                self.service_name, valid_names
            ));
        }

        match self.log_level.as_str() {
            "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL" => {}
            _ => return Err(format!("Invalid log level: {}", self.log_level)),
        }

        if self.port < 1 || self.port > 65535 {
            return Err(format!(
                "Port must be between 1 and 65535, got {}",
                self.port
            ));
        }

        if self.environment == Environment::Prod && self.api_key.is_empty() {
            warnings.push("API key is recommended in production".to_string());
        }

        if self.environment == Environment::Prod && self.log_level == "DEBUG" {
            warnings.push("DEBUG logging is not recommended in production".to_string());
        }

        if self.telemetry.is_configured() && self.telemetry.otlp_endpoint.is_empty() {
            warnings.push("Telemetry enabled but no OTLP endpoint configured".to_string());
        }

        self.database.validate()?;
        self.auth.validate()?;

        Ok(warnings)
    }

    /// Return configuration with secrets redacted.
    pub fn dict_without_secrets(&self) -> serde_json::Value {
        let mut map = serde_json::Map::new();
        map.insert("service_name".into(), serde_json::json!(&self.service_name));
        map.insert("port".into(), serde_json::json!(self.port));
        map.insert("version".into(), serde_json::json!(&self.version));
        map.insert("environment".into(), serde_json::json!(self.environment));
        map.insert("log_level".into(), serde_json::json!(&self.log_level));
        map.insert("host".into(), serde_json::json!(&self.host));
        if !self.api_key.is_empty() {
            map.insert("api_key".into(), serde_json::json!("***REDACTED***"));
        }
        if !self.auth.jwt_secret.is_empty() {
            let mut auth_map = serde_json::Map::new();
            auth_map.insert("jwt_secret".into(), serde_json::json!("***REDACTED***"));
            auth_map.insert("enabled".into(), serde_json::json!(self.auth.enabled));
            map.insert("auth".into(), serde_json::Value::Object(auth_map));
        }
        serde_json::Value::Object(map)
    }
}

impl fmt::Display for ServiceConfig {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "ServiceConfig(name={}, port={}, env={}, version={})",
            self.service_name, self.port, self.environment, self.version
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = ServiceConfig::new("Greenie".to_string(), 8080);
        assert_eq!(config.service_name, "Greenie");
        assert_eq!(config.port, 8080);
        assert_eq!(config.environment, Environment::Dev);
        assert_eq!(config.log_level, "INFO");
    }

    #[test]
    fn test_env_variable_override() {
        std::env::set_var("EVERSHADE_LOG_LEVEL", "DEBUG");
        let config = ServiceConfig::new("Test".to_string(), 3000);
        assert_eq!(config.log_level, "DEBUG");
        std::env::remove_var("EVERSHADE_LOG_LEVEL");
    }

    #[test]
    fn test_invalid_log_level() {
        let mut config = ServiceConfig::new("Test".to_string(), 3000);
        config.log_level = "INVALID".to_string();
        assert!(config.validate().is_err());
    }

    #[test]
    fn test_port_range() {
        let config = ServiceConfig::new("Test".to_string(), 3000);
        assert!(config.validate().is_ok());
    }

    #[test]
    fn test_empty_service_name() {
        let config = ServiceConfig::new("".to_string(), 3000);
        assert!(config.validate().is_err());
    }

    #[test]
    fn test_validate_warnings() {
        let mut config = ServiceConfig::new("Greenie".to_string(), 8080);
        config.environment = Environment::Prod;
        let warnings = config.validate().unwrap();
        assert!(warnings.iter().any(|w| w.contains("API key")));
    }

    #[test]
    fn test_dict_without_secrets() {
        let mut config = ServiceConfig::new("Greenie".to_string(), 8080);
        config.api_key = "secret-key".to_string();
        config.auth.jwt_secret = "secret".to_string();
        let redacted = config.dict_without_secrets();
        let api_key = redacted.get("api_key").unwrap().as_str().unwrap();
        assert_eq!(api_key, "***REDACTED***");
    }

    #[test]
    fn test_service_urls() {
        let config = ServiceConfig::new("Greenie".to_string(), 8080);
        assert_eq!(config.slinker_url, "http://Slinker:8000");
        assert_eq!(config.gobber_url, "http://Gobber:8085");
    }

    #[test]
    fn test_repr() {
        let config = ServiceConfig::new("Greenie".to_string(), 8080);
        let repr = format!("{}", config);
        assert!(repr.contains("Greenie"));
        assert!(repr.contains("8080"));
    }

    #[test]
    fn test_database_config_default() {
        let db = DatabaseConfig::default();
        assert_eq!(db.pool_size, 5);
        assert!(db.wal_mode);
    }

    #[test]
    fn test_empty_db_url() {
        let mut db = DatabaseConfig::default();
        db.url = String::new();
        assert!(db.validate().is_err());
    }

    #[test]
    fn test_telemetry_is_configured() {
        let t = TelemetryConfig::default();
        assert!(!t.is_configured());
        let mut t2 = TelemetryConfig::default();
        t2.otlp_endpoint = "http://localhost:4317".to_string();
        assert!(t2.is_configured());
    }

    #[test]
    fn test_auth_secret_required() {
        let mut auth = AuthConfig::default();
        auth.enabled = true;
        assert!(auth.validate().is_err());
        auth.jwt_secret = "secret".to_string();
        assert!(auth.validate().is_ok());
    }

    #[test]
    fn test_auth_disabled_without_secret() {
        let auth = AuthConfig::default();
        assert!(auth.validate().is_ok());
    }
}
