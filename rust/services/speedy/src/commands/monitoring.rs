//! Monitoring command — monitoring diagnostics.

use std::time::Duration;

pub fn run() {
    println!("📊 Evershade monitoring diagnostics:\n");

    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(10))
        .build()
        .unwrap_or_else(|_| reqwest::blocking::Client::new());

    let services = [
        ("Hider", "http://localhost:8087"),
        ("Greenie", "http://localhost:8080"),
        ("Slinker", "http://localhost:8000"),
        ("Sneaker", "http://localhost:8085"),
    ];

    println!("  Metrics Endpoints:");
    for (name, url) in &services {
        match client.get(format!("{}/metrics", url)).send() {
            Ok(resp) if resp.status().is_success() => {
                println!("    ✅ {} metrics available", name);
            }
            Ok(_) => {
                println!("    ⚠️  {} metrics endpoint non-200", name);
            }
            Err(_) => {
                println!("    ❌ {} unreachable", name);
            }
        }
    }

    println!("\n  OTLP Collector (Sneaker):");
    let api_key = std::env::var("API_KEY").unwrap_or_default();
    let mut headers = reqwest::blocking::header::HeaderMap::new();
    if !api_key.is_empty() {
        headers.insert(
            "Authorization",
            format!("Bearer {}", api_key).parse().unwrap(),
        );
    }

    match client
        .get("http://localhost:8085/api/otlp/stats")
        .headers(headers)
        .send()
    {
        Ok(resp) if resp.status().is_success() => {
            let data: serde_json::Value = resp.json().unwrap_or_default();
            println!("    ✅ OTLP stats available");
            if let Some(stats) = data.get("stats") {
                println!("      {}", serde_json::to_string_pretty(stats).unwrap());
            }
        }
        _ => println!("    ❌ Sneaker OTLP stats unreachable"),
    }

    println!("\n✅ Monitoring diagnostics complete");
}
