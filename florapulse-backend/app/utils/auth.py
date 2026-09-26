import hashlib
import secrets
from datetime import datetime, timedelta
from jose import JWTError, jwt

# ============= PASSWORD HASHING (Simple & Reliable) =============

def hash_password(password: str) -> str:
    """
    Hash password using SHA256 + salt.
    
    Simple, reliable, no version conflicts.
    Format: salt$hash
    """
    salt = secrets.token_hex(16)  # 16 bytes of random salt
    pwd_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Extract salt, re-hash, compare.
    """
    try:
        salt, pwd_hash = hashed_password.split('$')
        computed_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return computed_hash == pwd_hash
    except:
        return False


# ============= JWT TOKENS =============

SECRET_KEY = "test-secret-key-change-in-production-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None:
            return None
        return {"username": username, "user_id": user_id}
    except JWTError:
        return None
