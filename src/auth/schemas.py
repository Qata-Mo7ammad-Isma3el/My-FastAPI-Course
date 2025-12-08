from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.books.schemas import Book
    from src.reviews.schemas import ReviewModel


# --- 1. User Create Model ---
class UserCreateModel(BaseModel):
    ## ch7 QATA
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=40)
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    @field_validator("password")
    def validate_password_strength(cls, v):
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# --- 2. User Response Model ---
class UserModel(BaseModel):
    uid: UUID = Field(...)
    username: str = Field(...)
    email: EmailStr = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    is_verified: bool = Field(...)
    ## ch5QATA
    # // password_hash: str = Field(exclude=True)
    role: str = Field(...)  # Add role field
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)


# --- 2a. User with Books Response Model ---
class UserBooksModel(UserModel):
    books: List["Book"] = []
    reviews: List["ReviewModel"] = []


# --- 3. User Login Model ---
class UserLoginModel(BaseModel):
    email: EmailStr = Field(..., max_length=40, description="User's email address")
    password: str = Field(..., min_length=6, max_length=100)

# -- 4. Email Model ---
class EmailModel(BaseModel):
    addresses: List[EmailStr] = Field(..., description="List of recipient email addresses")
    # subject: str = Field(..., max_length=150, description="Subject of the email")
    # body: str = Field(..., description="Body content of the email")




# Rebuild models with forward references
def rebuild_models():
    """Rebuild models to resolve forward references."""
    try:
        from src.books.schemas import Book
        from src.reviews.schemas import ReviewModel

        UserBooksModel.model_rebuild()
    except Exception:
        pass  # Ignore if dependencies aren't loaded yet


rebuild_models()
