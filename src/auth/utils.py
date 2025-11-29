from passlib.context import CryptContext


password_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto"
)

def generate_password_hash(password:str) -> str:
    hash =  password_context.hash(password)
    return hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)

