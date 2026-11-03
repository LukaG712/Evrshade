//! Data models for Greenie mission orchestration service.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use uuid::Uuid;

/// Generate a new UUID string.
pub fn gen_id() -> String {
    Uuid::new_v4().to_string()
}

/// Return the current UTC time in ISO 8601 format.
pub fn now_iso() -> String {
    chrono::Utc::now().format("%Y-%m-%dT%H:%M:%SZ").to_string()
}

/// Escape single quotes in SQL strings.
pub fn escape_sql(s: &str) -> String {
    s.replace('\'', "''")
}

// ─── Agents ────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct AgentCreate {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub model: String,
    #[serde(default)]
    pub system_prompt: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentResponse {
    pub id: String,
    pub name: String,
    pub description: String,
    pub model: String,
    pub system_prompt: String,
    pub status: String,
    #[serde(default)]
    pub metadata: HashMap<String, serde_json::Value>,
    pub created_at: String,
    pub updated_at: String,
}

// ─── Missions ──────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct MissionCreate {
    pub name: String,
    #[serde(default)]
    pub description: String,
    pub agent_id: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MissionResponse {
    pub id: String,
    pub name: String,
    pub description: String,
    pub agent_id: String,
    pub status: String,
    #[serde(default)]
    pub progress: f64,
    #[serde(default)]
    pub result: String,
    #[serde(default)]
    pub error: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub completed_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

// ─── Tasks ─────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
pub struct TaskCreate {
    pub mission_id: String,
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default = "default_task_type")]
    pub task_type: String,
    #[serde(default)]
    pub payload: HashMap<String, serde_json::Value>,
}

fn default_task_type() -> String {
    "execution".to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskResponse {
    pub id: String,
    pub mission_id: String,
    pub name: String,
    pub description: String,
    #[serde(rename = "type")]
    pub task_type: String,
    pub status: String,
    #[serde(default)]
    pub payload: HashMap<String, serde_json::Value>,
    #[serde(default)]
    pub result: String,
    #[serde(default)]
    pub error: String,
    #[serde(default)]
    pub assigned_to: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub completed_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

// ─── Plugins ───────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginResponse {
    pub id: String,
    pub name: String,
    pub description: String,
    #[serde(rename = "type")]
    pub plugin_type: String,
    pub source: String,
    #[serde(default)]
    pub config: HashMap<String, serde_json::Value>,
    #[serde(default = "default_true")]
    pub enabled: bool,
    pub installed_at: String,
}

fn default_true() -> bool {
    true
}

#[derive(Debug, Deserialize)]
pub struct PluginInstall {
    pub name: String,
    pub source: String,
    #[serde(default = "default_plugin_type")]
    #[serde(rename = "type")]
    pub plugin_type: String,
    #[serde(default)]
    pub description: String,
}

fn default_plugin_type() -> String {
    "tool".to_string()
}

#[derive(Debug, Deserialize)]
pub struct PluginUpdate {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub enabled: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub config: Option<HashMap<String, serde_json::Value>>,
}

// ─── MCP Servers ───────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct McpServerResponse {
    pub id: String,
    pub name: String,
    pub url: String,
    pub transport: String,
    #[serde(default)]
    pub config: HashMap<String, serde_json::Value>,
    #[serde(default)]
    pub tools: Vec<serde_json::Value>,
    #[serde(default)]
    pub connected: bool,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct McpServerAdd {
    pub name: String,
    pub url: String,
}

// ─── Workstations ──────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkstationResponse {
    pub id: String,
    pub name: String,
    pub description: String,
    pub agent_name: String,
    pub status: String,
    pub container_id: String,
    pub container_name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub started_at: Option<String>,
    pub image: String,
    #[serde(default)]
    pub tags: Vec<String>,
    pub error: String,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct WorkstationCreate {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub agent_name: String,
    #[serde(default)]
    pub tags: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkstationStats {
    pub total: i64,
    pub running: i64,
    pub stopped: i64,
    pub error: i64,
    pub docker_available: bool,
}
