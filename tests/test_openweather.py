import sys
sys.path.append('.')

from cryptography.fernet import Fernet
from openweather.util.key_gen_menu import encrypt_message, decrypt_message


def test_encrypt_decrypt_roundtrip():
    key = Fernet.generate_key()
    message = "hello"
    encrypted = encrypt_message(key, message)
    assert decrypt_message(key, encrypted) == message


def test_decrypt_invalid_returns_none():
    key = Fernet.generate_key()
    assert decrypt_message(key, b"bad") is None

