from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
import jwt
import uuid
from src.config import settings
from itsdangerous import URLSafeTimedSerializer
from typing import Dict

password_context = CryptContext(schemes=["argon2"], deprecated="auto")


# > in seconds (1 hour)
def generate_password_hash(password: str) -> str:
    hash = password_context.hash(password)
    return hash


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
) -> str:
    payload = {}
    payload["user"] = user_data
    exp = datetime.now(timezone.utc) + (
        expiry
        if expiry is not None
        else timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY)
    )
    payload["exp"] = int(exp.timestamp())
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh
    token = jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALGO,
    )
    return token


def decode_token(token: str) -> dict:
    try:
        decoded_payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGO],
        )
        return decoded_payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


serializer = URLSafeTimedSerializer(
    secret_key=settings.JWT_SECRET,
    salt="email-verification-salt",
)


def create_url_safe_token(data: dict) -> str:
    token = serializer.dumps(data)
    return token


def decode_url_safe_token(token: str, max_age: int = 3600) -> Dict:
    """Decode URL safe token with max_age in seconds (default 1 hour)"""
    try:
        token_data = serializer.loads(token, max_age=max_age)
        return token_data
    except Exception as e:
        print(f"Token decode error: {type(e).__name__}: {str(e)}")
        raise Exception(f"Invalid or expired token: {str(e)}")
