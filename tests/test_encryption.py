# tests/test_encryption.py
"""Tests for the encryption helper functions.

The test verifies that:
1. `secure_encrypt_dict` encrypts all string fields in a dictionary.
2. `secure_decrypt_dict` correctly restores the original dictionary.
3. The encrypted values are not equal to the plaintext (basic sanity check).
"""

import os
import sys
import pytest
# Ensure the project root is on PYTHONPATH for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure a deterministic key for testing – set a fixed key if not already set
if not os.getenv("DATA_ENCRYPTION_KEY"):
    from cryptography.fernet import Fernet
    os.environ["DATA_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

from app.services.encryption import secure_encrypt_dict, secure_decrypt_dict

@pytest.fixture
def sample_email():
    return {
        "email_id": "12345",
        "body": "Hello, this is a test email body.",
        "subject": "Test Subject",
        "from": "sender@example.com",
        "your_reply": "Thanks for your email.",
        "date": "2026-02-04",
        "sentiment": "neutral",
    }

def test_secure_encrypt_decrypt_roundtrip(sample_email):
    encrypted = secure_encrypt_dict(sample_email)
    # All string fields should be encrypted (i.e., different from original)
    for key, value in sample_email.items():
        if isinstance(value, str):
            assert encrypted[key] != value
    # Decrypt back
    decrypted = secure_decrypt_dict(encrypted)
    assert decrypted == sample_email

def test_encrypt_decrypt_individual_functions(sample_email):
    from app.services.encryption import encrypt_text, decrypt_text
    for key, value in sample_email.items():
        if isinstance(value, str):
            enc = encrypt_text(value)
            dec = decrypt_text(enc)
            assert dec == value
