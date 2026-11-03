//! Notification delivery backends.
//!
//! Supports Slack (webhook), Email (stub), Telegram (HTTP), and generic webhooks.
//! Includes SSRF protection for webhook URLs.

use tracing::info;
use regex::Regex;

/// Deliver a notification to the specified channel.
pub async fn deliver(channel: &str, recipient: &str, title: &str, body: &str) -> Result<(), String> {
    match channel {
        "slack" => deliver_slack(recipient, title, body).await,
        "email" => deliver_email(recipient, title, body).await,
        "telegram" => deliver_telegram(recipient, title, body).await,
        "webhook" => deliver_webhook(recipient, title, body).await,
        _ => Err(format!("Unknown channel: {}", channel)),
    }
}

/// Deliver via Slack webhook.
async fn deliver_slack(webhook_url: &str, title: &str, body: &str) -> Result<(), String> {
    validate_webhook_url(webhook_url)?;

    let payload = serde_json::json!({
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title.chars().take(150).collect::<String>(),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": body.chars().take(3000).collect::<String>(),
                },
            },
        ],
    });

    let client = reqwest::Client::new();
    let resp = client
        .post(webhook_url)
        .json(&payload)
        .send()
        .await
        .map_err(|e| format!("Slack request failed: {}", e))?;

    if resp.status().is_success() {
        info!("Slack notification sent to {}", webhook_url);
        Ok(())
    } else {
        Err(format!("Slack returned status {}", resp.status()))
    }
}

/// Deliver via Email (stub — requires SMTP config).
async fn deliver_email(recipient: &str, title: &str, _body: &str) -> Result<(), String> {
    if !recipient.contains('@') {
        return Err("Email recipient must contain '@'".to_string());
    }

    // Sanitize subject to prevent email header injection
    let _subject = title.replace('\n', " ").replace('\r', " ");

    info!("Email notification queued for {} (SMTP not configured)", recipient);
    Ok(())
}

/// Deliver via Telegram bot.
async fn deliver_telegram(chat_id: &str, title: &str, body: &str) -> Result<(), String> {
    if chat_id.is_empty() {
        return Err("Telegram chat_id (recipient) is required".to_string());
    }

    // Validate chat_id is numeric to prevent injection
    let re = Regex::new(r"^-?\d+$").unwrap();
    if !re.is_match(chat_id) {
        return Err("Telegram chat_id must be numeric".to_string());
    }

    let bot_token = std::env::var("TELEGRAM_BOT_TOKEN").unwrap_or_default();
    if bot_token.is_empty() {
        return Err("TELEGRAM_BOT_TOKEN not configured".to_string());
    }

    let base_url = std::env::var("TELEGRAM_BASE_URL").unwrap_or_else(|_| "https://api.telegram.org".to_string());
    let url = format!("{}/bot{}/sendMessage", base_url, bot_token);

    let message = if title.is_empty() {
        body.to_string()
    } else {
        format!("*{}*\n\n{}", title, body)
    };

    let client = reqwest::Client::new();
    let resp = client
        .post(&url)
        .form(&[("chat_id", chat_id), ("text", &message), ("parse_mode", "Markdown")])
        .send()
        .await
        .map_err(|e| format!("Telegram request failed: {}", e))?;

    if resp.status().is_success() {
        info!("Telegram notification sent to chat {}", chat_id);
        Ok(())
    } else {
        Err(format!("Telegram returned status {}", resp.status()))
    }
}

/// Deliver via generic webhook.
async fn deliver_webhook(url: &str, title: &str, body: &str) -> Result<(), String> {
    validate_webhook_url(url)?;

    let payload = serde_json::json!({
        "title": title,
        "body": body,
    });

    let client = reqwest::Client::new();
    let resp = client
        .post(url)
        .json(&payload)
        .send()
        .await
        .map_err(|e| format!("Webhook request failed: {}", e))?;

    if resp.status().is_success() {
        info!("Webhook notification sent to {}", url);
        Ok(())
    } else {
        Err(format!("Webhook returned status {}", resp.status()))
    }
}

/// Validate webhook URL to prevent SSRF attacks.
fn validate_webhook_url(url_str: &str) -> Result<(), String> {
    use url::Url;

    let parsed = Url::parse(url_str).map_err(|e| format!("Invalid URL: {}", e))?;

    if parsed.scheme() != "http" && parsed.scheme() != "https" {
        return Err("Webhook URL must use http or https scheme".to_string());
    }

    let host = parsed.host_str().unwrap_or("");

    if matches!(host, "169.254.169.254" | "metadata.google.internal" | "metadata.cloud.oracle.com") {
        return Err("Webhook URL points to a blocked host".to_string());
    }

    if let Ok(ip) = host.parse::<std::net::IpAddr>() {
        let is_private = match ip {
            std::net::IpAddr::V4(v4) => v4.is_private() || v4.is_loopback() || v4.is_link_local(),
            std::net::IpAddr::V6(v6) => v6.is_loopback() || v6.is_unspecified(),
        };
        if is_private {
            return Err("Webhook URL must not point to a private IP address".to_string());
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validate_webhook_url_http() {
        assert!(validate_webhook_url("http://example.com/webhook").is_ok());
    }

    #[test]
    fn test_validate_webhook_url_blocked_metadata() {
        assert!(validate_webhook_url("http://169.254.169.254/meta").is_err());
    }

    #[test]
    fn test_validate_webhook_url_private_ip() {
        assert!(validate_webhook_url("http://192.168.1.1/webhook").is_err());
    }

    #[test]
    fn test_validate_webhook_url_loopback() {
        assert!(validate_webhook_url("http://127.0.0.1/webhook").is_err());
    }

    #[test]
    fn test_validate_webhook_url_invalid_scheme() {
        assert!(validate_webhook_url("ftp://example.com/webhook").is_err());
    }

    #[test]
    fn test_telegram_chat_id_validation() {
        let re = Regex::new(r"^-?\d+$").unwrap();
        assert!(re.is_match("-1001234567890"));
        assert!(re.is_match("123456789"));
        assert!(!re.is_match("abc123"));
    }
}
