from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from typing import Union, Annotated, List
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import decode_token
from src.db.redis import RedisClient, get_redis
from src.db.main import get_session
from src.db.models import User
from src.auth.service import UserService
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request, redis_client: Annotated[RedisClient, Depends(get_redis)]
    ) -> Union[HTTPAuthorizationCredentials, None]:
        cred = await super().__call__(request)
        # print(cred.scheme) #> Bearer
        # print(cred.credentials) #> actual token
        token = cred.credentials

        if not self.token_valid(token):
            raise InvalidToken()

        token_data = decode_token(token)

        if await redis_client.token_in_BlockList(token_data["jti"]):
            raise InvalidToken()

        self.verify_token_data(token_data)
        return token_data

    ## ch1QATA
    def token_valid(self, token: str) -> bool:
        try:
            decode_token(token)
            return True
        except Exception as e:
            print(f"Token validation failed: {type(e).__name__}: {str(e)}")
            return False

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("please override this method in subclass!!")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_data: Annotated[dict, Depends(AccessTokenBearer())],
):
    user_email = token_data["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or missing email",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
    ):
        if current_user.role not in self.allowed_roles:
            raise InsufficientPermission()
        return True
