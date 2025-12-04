from pydantic import BaseModel, field_validator
from sqlmodel import Field
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from src.auth.schemas import UserModel
    from src.books.schemas import BookResponse


class ReviewModel(BaseModel):
    # > Unique identifier
    uid: UUID

    # > Reviews fields
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)
    user_uid: Optional[UUID] = None
    book_uid: Optional[UUID] = None 

    # > Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode


class ReviewCreateModel(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)

    @field_validator("review_text")
    def validate_review_text(cls, v):
        if v and len(v.strip()) < 10:
            raise ValueError("Review text must be at least 10 characters long")
        if v and len(v.strip()) > 2000:
            raise ValueError("Review text must be less than 2000 characters")
        return v.strip() if v else v

    @field_validator("rating")
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewUpdateModel(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    review_text: Optional[str] = Field(default=None, max_length=2000)


## -----------------------------------------------
class ReviewResponse(BaseModel):
    uid: UUID
    rating: int
    review_text: Optional[str]
    user_uid: UUID
    book_uid: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewResponseUpdateModel(BaseModel):
    message: str
    old_review: ReviewModel
    updated_review: ReviewModel


class ReviewDeleteResponseModel(BaseModel):
    message: str
    deleted_review: ReviewModel


# Add a detailed response model
class ReviewDetailModel(ReviewModel):
    user: Optional["UserModel"] = None
    book: Optional["BookResponse"] = None


# Rebuild models with forward references
def rebuild_models():
    """Rebuild models to resolve forward references."""
    try:
        from src.auth.schemas import UserModel
        from src.books.schemas import BookResponse

        ReviewDetailModel.model_rebuild()
    except Exception:
        pass  # Ignore if dependencies aren't loaded yet


rebuild_models()
