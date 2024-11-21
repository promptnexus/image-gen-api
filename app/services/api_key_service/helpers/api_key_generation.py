import hmac
import secrets
import hashlib
from typing import Tuple


def generate_api_key(prefix: str = "sk") -> str:
    """Generate a secure API key with prefix."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


def create_api_key() -> Tuple[str, str]:
    """Create an API key and return (key, hash) pair."""
    api_key = generate_api_key()
    hashed_key = hash_api_key(api_key)
    return api_key, hashed_key


def verify_api_key(incoming_key: str, stored_hash: str) -> bool:
    """Verify an incoming API key against a stored hash."""
    return hmac.compare_digest(hash_api_key(incoming_key), stored_hash)


# def main():
#   api_key, hashed_key = create_api_key()
#   print(f"API Key: {api_key}")
#   print(f"Hashed Key: {hashed_key}")


# if __name__ == "__main__":
#   main()
