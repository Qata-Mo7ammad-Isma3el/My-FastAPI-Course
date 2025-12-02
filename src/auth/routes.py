from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from src.auth.schemas import UserCreateModel, UserModel, UserLoginModel, UserBooksModel
from src.auth.service import UserService
from src.db.main import get_session
from src.auth.utils import create_access_token, decode_token, verify_password
from datetime import timedelta
from src.config import settings
from src.auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_BlockList
from datetime import datetime

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
async def create_user_account(
    user_data: UserCreateModel, session: Annotated[AsyncSession, Depends(get_session)]
):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this email '({email})' already exists.",
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_user(
    login_data: UserLoginModel, session: Annotated[AsyncSession, Depends(get_session)]
):

    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
        if password_valid:
            access_token = create_access_token(
                user_data={
                    "uid": str(user.uid),
                    "email": user.email,
                    "role": user.role,
                },
            )
            refresh_token = create_access_token(
                user_data={
                    "uid": str(user.uid),
                    "email": user.email,
                },
                expiry=timedelta(days=settings.REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "Login Successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "uid": str(user.uid),
                        "email": user.email,
                    },
                    "token_type": "bearer",
                },
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )


@auth_router.get("/refresh_token")
async def get_new_access_token(
    token_details: Annotated[dict, Depends(RefreshTokenBearer())],
):
    expiry_timestamp = token_details.get("exp")
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(
            user_data={
                "uid": token_details.get("uid"),
                "email": token_details.get("email"),
            },
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "access_token": new_access_token,
                "token_type": "bearer",
            },
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh token has expired. Please log in again.",
    )


@auth_router.get("/me", response_model=UserBooksModel)
async def get_logged_in_user(
    current_user: Annotated[dict, Depends(get_current_user)],
    _: bool = Depends(role_checker),
):
    return current_user  # TODO try to add uid in a good looking way


@auth_router.post("/logout")
async def revoke_token(token_details: Annotated[dict, Depends(AccessTokenBearer())]):
    jti = token_details.get("jti")
    await add_jti_to_BlockList(jti)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Token has been revoked successfully."},
    )
