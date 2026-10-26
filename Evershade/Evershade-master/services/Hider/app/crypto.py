"""Hider — AES-256-GCM encryption utilities.

Provides encrypt/decrypt functions using AES-256-GCM with a key derived from
the HIDER_ENCRYPTION_KEY environment variable.
"""

from __future__ import annotations

import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    """Get the encryption key from environment, deriving a 32-byte key."""
    key_str = os.getenv("HIDER_ENCRYPTION_KEY", "")
    if not key_str:
        raise RuntimeError("HIDER_ENCRYPTION_KEY environment variable is not set")
    # Use the first 32 bytes of the key, padding with zeros if needed
    key_bytes = key_str.encode("utf-8")
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b"\x00")
    return key_bytes[:32]


def encrypt(plaintext: str) -> tuple[bytes, bytes, bytes]:
    """
    Encrypt a string using AES-256-GCM.

    Returns:
        (encrypted_value, iv, tag) tuple for storage in the database.
    """
    key = _get_key()
    aesgcm = AESGCM(key)
    iv = os.urandom(12)  # 96-bit IV for GCM
    ciphertext = aesgcm.encrypt(iv, plaintext.encode("utf-8"), None)
    # ciphertext includes the GCM tag appended
    return ciphertext, iv, b""


def decrypt(encrypted_value: bytes, iv: bytes) -> str:
    """
    Decrypt an encrypted value using AES-256-GCM.

    Args:
        encrypted_value: The ciphertext blob from the database.
        iv: The initialization vector from the database.

    Returns:
        The decrypted plaintext string.
    """
    key = _get_key()
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, encrypted_value, None)
    return plaintext.decode("utf-8")
