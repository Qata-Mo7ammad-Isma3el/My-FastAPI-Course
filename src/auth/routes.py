from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from src.auth.schemas import UserCreateModel, UserModel
from src.auth.service import user_service
from src.db.main import get_session

auth_router = APIRouter()
User_Service = user_service()


@auth_router.post(
    "/signup", status_code=status.HTTP_201_CREATED, response_model=UserModel
)
async def create_user_account(
    user_data: UserCreateModel, session: Annotated[AsyncSession, Depends(get_session)]
):
    email = user_data.email
    user_exists = await User_Service.user_exists(email, session)

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with this email '({email})' already exists.",
        )
    new_user = await User_Service.create_user(user_data, session)
    return new_user
