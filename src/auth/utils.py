from passlib.context import CryptContext
from datetime import timedelta, datetime
import jwt 
import uuid 
from src.config import settings
password_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

# > in seconds (1 hour)
def generate_password_hash(password:str) -> str:
    hash =  password_context.hash(password)
    return hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

def create_access_token(user_data: dict , expiry:timedelta = None, refresh: bool = False) -> str:
    payload = {}
    payload['user'] = user_data 
    exp =datetime.now() + (expiry if expiry is not None else timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY))
    payload['exp'] = int(exp.timestamp())
    payload['jti'] = str(uuid.uuid4())
    payload['refresh'] = refresh
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