import hashlib
import os

  def get_secure_hash(password: str) -> str:
    """Generate secure hash of password."""
    salt = os.environ.get("AUTH_SALT", "default_salt")
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
  if __name__ == "__main__":
    print(get_secure_hash("admin"))
