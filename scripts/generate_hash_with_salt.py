import hashlib
import os

  def get_secure_hash(password: str) -> str:
    """Generate secure hash of password."""
    salt = "dashboard_salt"  # Using the same salt as in the running app
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
  if __name__ == "__main__":
    print(get_secure_hash("admin"))
