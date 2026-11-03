//! Model routing with cost tracking and privacy classification.
//!
//! Routes chat requests to the appropriate provider based on model name,
//! tracks token usage and estimated costs, and classifies models as public
//! or private (local-only) for data privacy compliance.

use chrono::Utc;
use once_cell::sync::Lazy;
use std::collections::HashMap;
use std::sync::Mutex;
use tracing::info;

use crate::models::{
    ChatMessage, ChatResponse, CostEntry, CostSummary, ModelCost, ModelInfo, Provider, ProviderCost,
};
use crate::providers::{get_provider, LlmProvider};

/// Model registry: maps model names to provider and metadata.
pub static MODEL_REGISTRY: Lazy<HashMap<&'static str, ModelMeta>> = Lazy::new(|| {
    let mut map = HashMap::new();
    // OpenAI
    map.insert(
        "gpt-4o",
        ModelMeta {
            provider: Provider::OpenAI,
            context_window: 128_000,
            is_private: false,
        },
    );
    map.insert(
        "gpt-4o-mini",
        ModelMeta {
            provider: Provider::OpenAI,
            context_window: 128_000,
            is_private: false,
        },
    );
    map.insert(
        "gpt-3.5-turbo",
        ModelMeta {
            provider: Provider::OpenAI,
            context_window: 16_385,
            is_private: false,
        },
    );
    // Anthropic
    map.insert(
        "claude-3-opus",
        ModelMeta {
            provider: Provider::Anthropic,
            context_window: 200_000,
            is_private: false,
        },
    );
    map.insert(
        "claude-3-sonnet",
        ModelMeta {
            provider: Provider::Anthropic,
            context_window: 200_000,
            is_private: false,
        },
    );
    map.insert(
        "claude-3-haiku",
        ModelMeta {
            provider: Provider::Anthropic,
            context_window: 200_000,
            is_private: false,
        },
    );
    // Google
    map.insert(
        "gemini-pro",
        ModelMeta {
            provider: Provider::Google,
            context_window: 32_768,
            is_private: false,
        },
    );
    map.insert(
        "gemini-1.5-pro",
        ModelMeta {
            provider: Provider::Google,
            context_window: 1_048_576,
            is_private: false,
        },
    );
    map.insert(
        "gemini-1.5-flash",
        ModelMeta {
            provider: Provider::Google,
            context_window: 1_048_576,
            is_private: false,
        },
    );
    // Ollama (local/private)
    map.insert(
        "llama3",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 8_192,
            is_private: true,
        },
    );
    map.insert(
        "llama3.1",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 131_072,
            is_private: true,
        },
    );
    map.insert(
        "llama3.2",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 131_072,
            is_private: true,
        },
    );
    map.insert(
        "gemma2",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 8_192,
            is_private: true,
        },
    );
    map.insert(
        "gemma4:12b",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 8_192,
            is_private: true,
        },
    );
    map.insert(
        "mistral",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 8_192,
            is_private: true,
        },
    );
    map.insert(
        "phi3",
        ModelMeta {
            provider: Provider::Ollama,
            context_window: 4_096,
            is_private: true,
        },
    );
    map
});

#[derive(Clone)]
struct ModelMeta {
    provider: Provider,
    context_window: usize,
    is_private: bool,
}

/// Estimated costs per 1M tokens (input/output) for public models.
static COST_PER_MILLION: Lazy<HashMap<&'static str, (f64, f64)>> = Lazy::new(|| {
    let mut map = HashMap::new();
    map.insert("gpt-4o", (2.50, 10.00));
    map.insert("gpt-4o-mini", (0.15, 0.60));
    map.insert("gpt-3.5-turbo", (0.50, 1.50));
    map.insert("claude-3-opus", (15.00, 75.00));
    map.insert("claude-3-sonnet", (3.00, 15.00));
    map.insert("claude-3-haiku", (0.25, 1.25));
    map.insert("gemini-pro", (0.50, 1.50));
    map.insert("gemini-1.5-pro", (3.50, 10.50));
    map.insert("gemini-1.5-flash", (0.075, 0.30));
    map
});

/// In-memory cost tracker (capped to prevent unbounded memory growth).
static COST_LOG: Lazy<Mutex<Vec<CostEntry>>> = Lazy::new(|| Mutex::new(Vec::new()));
const MAX_COST_LOG_SIZE: usize = 10_000;

/// Resolve the provider and metadata for a model name.
pub fn resolve_provider(model: &str) -> Result<(Provider, usize, bool), String> {
    if let Some(meta) = MODEL_REGISTRY.get(model) {
        Ok((meta.provider, meta.context_window, meta.is_private))
    } else {
        let available: Vec<&str> = MODEL_REGISTRY.keys().copied().collect();
        Err(format!(
            "Model '{}' not found in registry. Available models: {:?}",
            model, available
        ))
    }
}

/// Estimate the cost of a completion in USD.
pub fn estimate_cost(model: &str, prompt_tokens: usize, completion_tokens: usize) -> f64 {
    let rates = match COST_PER_MILLION.get(model) {
        Some(r) => *r,
        None => return 0.0,
    };
    let (input_rate, output_rate) = rates;
    let cost = (prompt_tokens as f64 / 1_000_000.0) * input_rate
        + (completion_tokens as f64 / 1_000_000.0) * output_rate;
    (cost * 1_000_000.0).round() / 1_000_000.0
}

/// Record token usage and cost for tracking.
fn record_usage(
    model: &str,
    provider: Provider,
    prompt_tokens: usize,
    completion_tokens: usize,
    cost: f64,
) {
    let entry = CostEntry {
        timestamp: Utc::now(),
        model: model.to_string(),
        provider: provider.as_str().to_string(),
        prompt_tokens,
        completion_tokens,
        total_tokens: prompt_tokens + completion_tokens,
        cost_usd: cost,
    };
    let mut log = COST_LOG.lock().unwrap();
    log.push(entry);
    if log.len() > MAX_COST_LOG_SIZE {
        let excess = log.len() - MAX_COST_LOG_SIZE;
        log.drain(..excess);
    }
    info!(
        "Usage: model={} provider={} prompt={} completion={} cost=${:.6}",
        model, provider, prompt_tokens, completion_tokens, cost
    );
}

/// Get a summary of all tracked costs.
pub fn get_cost_summary() -> CostSummary {
    let log = COST_LOG.lock().unwrap();
    if log.is_empty() {
        return CostSummary {
            total_cost_usd: 0.0,
            total_tokens: 0,
            requests: 0,
            by_provider: HashMap::new(),
            by_model: HashMap::new(),
        };
    }

    let mut total_cost = 0.0;
    let mut total_tokens = 0usize;
    let mut by_provider: HashMap<String, ProviderCost> = HashMap::new();
    let mut by_model: HashMap<String, ModelCost> = HashMap::new();

    for entry in log.iter() {
        total_cost += entry.cost_usd;
        total_tokens += entry.total_tokens;

        let prov = by_provider
            .entry(entry.provider.clone())
            .or_insert(ProviderCost {
                cost_usd: 0.0,
                tokens: 0,
                requests: 0,
            });
        prov.cost_usd += entry.cost_usd;
        prov.tokens += entry.total_tokens;
        prov.requests += 1;

        let m = by_model.entry(entry.model.clone()).or_insert(ModelCost {
            cost_usd: 0.0,
            tokens: 0,
            requests: 0,
        });
        m.cost_usd += entry.cost_usd;
        m.tokens += entry.total_tokens;
        m.requests += 1;
    }

    // Round costs
    for v in by_provider.values_mut() {
        v.cost_usd = (v.cost_usd * 1_000_000.0).round() / 1_000_000.0;
    }
    for v in by_model.values_mut() {
        v.cost_usd = (v.cost_usd * 1_000_000.0).round() / 1_000_000.0;
    }

    CostSummary {
        total_cost_usd: (total_cost * 1_000_000.0).round() / 1_000_000.0,
        total_tokens,
        requests: log.len(),
        by_provider,
        by_model,
    }
}

/// Route a chat request to the appropriate provider.
pub async fn route_chat(
    messages: &[ChatMessage],
    model: Option<&str>,
    temperature: f64,
    max_tokens: usize,
    require_private: bool,
) -> Result<ChatResponse, String> {
    // Determine model
    let model = model.unwrap_or_else(|| {
        std::env::var("SHREWD_DEFAULT_MODEL").unwrap_or_else(|_| "llama3".to_string())
    });

    let (resolved_provider, _context_window, is_private) =
        resolve_provider(&model).map_err(|e| format!("Model resolution failed: {}", e))?;

    // Privacy check
    if require_private && !is_private {
        return Err(format!(
            "Model '{}' ({}) is not private. Use a local model (Ollama) for private data.",
            model, resolved_provider
        ));
    }

    // Get provider instance and check availability
    let provider: Box<dyn LlmProvider> = get_provider(resolved_provider);
    if !provider.check_available() {
        return Err(format!(
            "Provider '{}' is not configured. Set the required API key environment variable.",
            resolved_provider
        ));
    }

    // Execute the chat request
    let response = provider
        .chat(messages, &model, temperature, max_tokens)
        .await
        .map_err(|e| format!("Provider error: {}", e))?;

    // Track cost
    let cost = estimate_cost(&model, response.prompt_tokens, response.completion_tokens);
    record_usage(
        &model,
        resolved_provider,
        response.prompt_tokens,
        response.completion_tokens,
        cost,
    );

    // Return response with cost
    Ok(ChatResponse {
        cost_usd: cost,
        ..response
    })
}

/// List available models with optional provider filter.
pub fn list_models(provider_filter: Option<Provider>) -> Vec<ModelInfo> {
    let mut results = Vec::new();
    for (name, meta) in MODEL_REGISTRY.iter() {
        if let Some(filter) = provider_filter {
            if meta.provider != filter {
                continue;
            }
        }
        let prov_instance = get_provider(meta.provider);
        results.push(ModelInfo {
            name: (*name).to_string(),
            provider: meta.provider,
            context_window: meta.context_window,
            is_private: meta.is_private,
            is_available: prov_instance.check_available(),
        });
    }
    results
}

/// List available providers with availability status.
pub fn list_providers() -> Vec<(Provider, bool)> {
    let providers = [
        Provider::OpenAI,
        Provider::Anthropic,
        Provider::Google,
        Provider::Ollama,
    ];
    providers
        .into_iter()
        .map(|p| {
            let inst = get_provider(p);
            (p, inst.check_available())
        })
        .collect()
}
