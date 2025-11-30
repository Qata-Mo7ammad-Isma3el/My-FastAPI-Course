from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from typing import Union, Annotated, List
from fastapi.security.http import HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.utils import decode_token
from src.db.redis import token_in_BlockList
from src.db.main import get_session
from src.auth.models import User
from src.auth.service import user_service

User_Service = user_service()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> Union[HTTPAuthorizationCredentials, None]:
        cred = await super().__call__(request)
        # print(cred.scheme) #> Bearer
        # print(cred.credentials) #> actual token
        token = cred.credentials
        token_data = decode_token(token)
        if not self.token_valid(token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token.",
            )
        if await token_in_BlockList(token_data["jti"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token has been revoked. Please login again.",
            )
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        return True if decode_token(token) is not None else False

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("please override this method in subclass!!")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="please provide a valid access token.",
            )


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Refresh token cannot be used as access token. please provide a valid access Refresh token.",
            )


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_data:Annotated[dict , Depends(AccessTokenBearer())],
):
    user_email = token_data['user']['email']
    user = await User_Service.get_user_by_email(user_email, session)
    
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or missing email"
        )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have the necessary permissions to access this resource.",
            )
        return True