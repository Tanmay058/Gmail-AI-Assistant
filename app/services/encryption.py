# app/services/encryption.py
"""Central encryption utilities used across the project.

- Loads a single Fernet key from the environment variable ``DATA_ENCRYPTION_KEY``.
- Provides ``encrypt_text`` / ``decrypt_text`` wrappers (already exist in ``rag_service``) but re‑exposed here for reuse.
- ``secure_encrypt_dict`` walks a ``dict`` and encrypts every ``str`` value.
- ``secure_decrypt_dict`` does the inverse, returning a new dict with decrypted strings.

The key is loaded once at import time, so all modules share the same instance.
"""

import os
from typing import Any, Dict
from cryptography.fernet import Fernet

# Load the key from the environment (or generate a temporary one for dev).
_key = os.getenv("DATA_ENCRYPTION_KEY")
if not _key:
    # In production you should set this env var; for local dev we generate a throw‑away key.
    _key = Fernet.generate_key().decode()
    print(f"[INFO] Generated temporary DATA_ENCRYPTION_KEY: {_key}")

fernet = Fernet(_key.encode())


def encrypt_text(text: str) -> str:
    """Encrypt a plain‑text string and return the base64 ciphertext."""
    if not text:
        return ""
    return fernet.encrypt(text.encode()).decode()


def decrypt_text(cipher: str) -> str:
    """Decrypt a base64 ciphertext back to plain text."""
    if not cipher:
        return ""
    return fernet.decrypt(cipher.encode()).decode()


def _process_value(value: Any, func) -> Any:
    """Recursively apply ``func`` to strings inside mappings or iterables.
    ``func`` should be either ``encrypt_text`` or ``decrypt_text``.
    """
    if isinstance(value, str):
        return func(value)
    if isinstance(value, dict):
        return {k: _process_value(v, func) for k, v in value.items()}
    if isinstance(value, list):
        return [_process_value(v, func) for v in value]
    # Non‑string scalar types are returned unchanged.
    return value


def secure_encrypt_dict(data: Dict) -> Dict:
    """Return a new dict with every string value encrypted.
    Nested structures (dicts/lists) are processed recursively.
    """
    return _process_value(data, encrypt_text)  # type: ignore[arg-type]


def secure_decrypt_dict(data: Dict) -> Dict:
    """Return a new dict with every encrypted string decrypted.
    Mirrors ``secure_encrypt_dict``.
    """
    return _process_value(data, decrypt_text)  # type: ignore[arg-type]
