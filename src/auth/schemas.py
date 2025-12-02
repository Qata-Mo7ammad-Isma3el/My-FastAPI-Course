from pydantic import BaseModel, EmailStr, Field
from src.books.schemas import Book
from datetime import datetime
from uuid import UUID
from typing import List
from src.reviews.schemas import ReviewModel

# --- 1. User Create Model ---
class UserCreateModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, strip_whitespace=True)
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(..., min_length=6, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)
    last_name: str = Field(..., min_length=1, max_length=50, strip_whitespace=True)

# --- 2. User Response Model ---
class UserModel(BaseModel):
    uid: UUID = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    is_verified: bool = Field(...)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)

# --- 2a. User with Books Response Model ---
class UserBooksModel(UserModel):
    books: List[Book] 
    reviews: List[ReviewModel]

# --- 3. User Login Model ---
class UserLoginModel(BaseModel):
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(..., min_length=6, max_length=100)
