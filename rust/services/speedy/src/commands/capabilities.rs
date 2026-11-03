//! Capabilities command — queries service capabilities.

use std::time::Duration;

pub fn run(service: Option<String>) {
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .unwrap_or_else(|_| reqwest::blocking::Client::new());

    let api_key = std::env::var("API_KEY").unwrap_or_default();
    let mut headers = reqwest::blocking::header::HeaderMap::new();
    if !api_key.is_empty() {
        headers.insert(
            "Authorization",
            format!("Bearer {}", api_key).parse().unwrap(),
        );
    }

    let services = [
        ("Hider", "http://localhost:8087"),
        ("Greenie", "http://localhost:8080"),
        ("Slinker", "http://localhost:8000"),
        ("Sneaker", "http://localhost:8085"),
        ("Poltergeist", "http://localhost:8086"),
        ("Shrewd", "http://localhost:8083"),
        ("Gobber", "http://localhost:8084"),
    ];

    if let Some(ref svc) = service {
        let (name, url) = services
            .iter()
            .find(|(n, _)| n.to_lowercase() == svc.to_lowercase())
            .unwrap_or_else(|| {
                eprintln!("Unknown service: {}", svc);
                std::process::exit(1);
            });

        match client
            .get(format!("{}/api/capabilities", url))
            .headers(headers.clone())
            .send()
        {
            Ok(resp) if resp.status().is_success() => {
                let data: serde_json::Value = resp.json().unwrap_or_else(|_| {
                    serde_json::json!({"error": "Failed to parse response"})
                });
                println!("{}", serde_json::to_string_pretty(&data).unwrap());
            }
            Ok(resp) => {
                eprintln!(
                    "Error: {} {}",
                    resp.status(),
                    resp.status()
                        .canonical_reason()
                        .unwrap_or("Unknown")
                );
                std::process::exit(1);
            }
            Err(e) => {
                eprintln!("Error: {} is unreachable: {}", name, e);
                std::process::exit(1);
            }
        }
    } else {
        println!("📋 Evershade service capabilities:\n");
        for (name, url) in &services {
            match client
                .get(format!("{}/api/capabilities", url))
                .headers(headers.clone())
                .send()
            {
                Ok(resp) if resp.status().is_success() => {
                    let data: serde_json::Value = resp.json().unwrap_or_default();
                    let caps = data
                        .get("capabilities")
                        .and_then(|c| c.as_array())
                        .unwrap_or(&vec![]);
                    println!("  {} ({})", name, url);
                    for cap in caps {
                        if let Some(cap_str) = cap.as_str() {
                            println!("    - {}", cap_str);
                        }
                    }
                    println!();
                }
                _ => {
                    println!("  {} — ❌ unreachable\n", name);
                }
            }
        }
    }
}
