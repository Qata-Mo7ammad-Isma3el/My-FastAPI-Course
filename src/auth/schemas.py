from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class UserCreateModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, strip_whitespace=True)
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(..., min_length=6, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)


class UserModel(BaseModel):
    uid: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime

class UserLoginModel(BaseModel):
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(..., min_length=6, max_length=100)