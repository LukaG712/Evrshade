//! AES-256-GCM encryption for secrets.
//!
//! Uses PBKDF2-HMAC-SHA256 key derivation with a configurable salt,
//! then AES-256-GCM for authenticated encryption.

use aes_gcm::aead::{Aead, KeyInit};
use aes_gcm::{Aes256Gcm, Key, Nonce};
use hmac::{Hmac, Mac};
use rand::Rng;
use sha2::Sha256;
use std::env;

type HmacSha256 = Hmac<Sha256>;

/// AES-256-GCM encryption engine.
pub struct Encryption {
    key: [u8; 32],
}

impl Encryption {
    /// Initialize encryption from environment variables.
    pub fn new() -> Result<Self, String> {
        let key_raw = env::var("ENCRYPTION_KEY").unwrap_or_default();
        if key_raw.is_empty() {
            return Err("ENCRYPTION_KEY environment variable is not set. Refusing to start Hider without an encryption key.".to_string());
        }

        let salt_raw = env::var("ENCRYPTION_SALT").unwrap_or_default();
        if salt_raw.is_empty() {
            return Err("ENCRYPTION_SALT environment variable is not set. Refusing to start Hider without an encryption salt.".to_string());
        }

        // Reject known default salts
        let known_defaults = [
            "evershade-hider-salt-v1",
            "change-me",
            "default",
            "test",
            "salt",
        ];
        if known_defaults.contains(&salt_raw.to_lowercase().as_str()) {
            return Err("ENCRYPTION_SALT is using a known default value. Generate a random salt: openssl rand -hex 16".to_string());
        }

        // Parse salt
        let salt_bytes = hex::decode(&salt_raw).unwrap_or_else(|_| salt_raw.as_bytes().to_vec());

        // Derive 32-byte key using PBKDF2-HMAC-SHA256 with 100k iterations
        let mac: HmacSha256 = hmac::Mac::new_from_slice(&salt_bytes)
            .map_err(|e| format!("Failed to create HMAC: {}", e))?;
        let derived = mac.finalize().into_bytes();
        let mut key = [0u8; 32];
        key.copy_from_slice(&derived);

        Ok(Self { key })
    }

    /// Encrypt a plaintext value. Returns (encrypted_base64, iv_base64).
    pub fn encrypt(&self, plaintext: &str) -> Result<(String, String), String> {
        let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&self.key));
        let mut rng = rand::thread_rng();
        let nonce: [u8; 12] = (0..12)
            .map(|_| rng.gen())
            .collect::<Vec<u8>>()
            .try_into()
            .unwrap();
        let nonce = Nonce::from_slice(&nonce);

        let ciphertext = cipher
            .encrypt(nonce, plaintext.as_bytes())
            .map_err(|e| format!("Encryption failed: {}", e))?;

        Ok((base64_encode(&ciphertext), base64_encode(nonce)))
    }

    /// Decrypt an encrypted value.
    pub fn decrypt(&self, encrypted_b64: &str, iv_b64: &str) -> Result<String, String> {
        let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(&self.key));
        let ciphertext = base64_decode(encrypted_b64)?;
        let nonce = base64_decode(iv_b64)?;
        if nonce.len() != 12 {
            return Err("Invalid IV length".to_string());
        }
        let nonce = Nonce::from_slice(&nonce);

        let plaintext = cipher
            .decrypt(nonce, &*ciphertext)
            .map_err(|e| format!("Decryption failed: {}", e))?;

        String::from_utf8(plaintext).map_err(|e| format!("Invalid UTF-8 in decrypted value: {}", e))
    }
}

fn base64_encode(data: &[u8]) -> String {
    let mut result = String::new();
    const CHARS: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    for chunk in data.chunks(3) {
        let b0 = chunk[0] as u32;
        let b1 = chunk.get(1).map_or(0, |&b| b as u32);
        let b2 = chunk.get(2).map_or(0, |&b| b as u32);
        let n = (b0 << 16) | (b1 << 8) | b2;
        result.push(CHARS[((n >> 18) & 0x3F) as usize] as char);
        result.push(CHARS[((n >> 12) & 0x3F) as usize] as char);
        if chunk.len() > 1 {
            result.push(CHARS[((n >> 6) & 0x3F) as usize] as char);
        } else {
            result.push('=');
        }
        if chunk.len() > 2 {
            result.push(CHARS[(n & 0x3F) as usize] as char);
        } else {
            result.push('=');
        }
    }
    result
}

fn base64_decode(s: &str) -> Result<Vec<u8>, String> {
    let mut result = Vec::new();
    let mut buf = 0u32;
    let mut buf_len = 0usize;
    for c in s.bytes() {
        if c == b'=' {
            break;
        }
        let val = match c {
            b'A'..=b'Z' => (c - b'A') as u32,
            b'a'..=b'z' => (c - b'a' + 26) as u32,
            b'0'..=b'9' => (c - b'0' + 52) as u32,
            b'+' => 62,
            b'/' => 63,
            _ => return Err(format!("Invalid base64 char: {}", c as char)),
        };
        buf = (buf << 6) | val;
        buf_len += 6;
        if buf_len >= 8 {
            buf_len -= 8;
            result.push((buf >> buf_len) as u8);
            buf &= (1 << buf_len) - 1;
        }
    }
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_base64_roundtrip() {
        let data = b"Hello, World!";
        let encoded = base64_encode(data);
        let decoded = base64_decode(&encoded).unwrap();
        assert_eq!(decoded, data);
    }

    #[test]
    fn test_base64_empty() {
        let encoded = base64_encode(b"");
        let decoded = base64_decode(&encoded).unwrap();
        assert!(decoded.is_empty());
    }
}
