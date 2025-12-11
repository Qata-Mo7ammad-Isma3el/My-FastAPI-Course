from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from datetime import datetime, date
from pydantic import ConfigDict
if TYPE_CHECKING:
    from src.reviews.schemas import ReviewModel
    from src.tags.schemas import TagModel


# --- 1. Base Schema Model ---
class BookBase(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


# --- 2. Book Schemas ---
class Book(BookBase):
    uid: UUID
    user_uid: UUID
    created_at: datetime
    updated_at: datetime


# --- 3. Request Models ---
class BookCreateModel(BookBase):
    @field_validator("page_count")
    def page_count_positive(cls, v):
        if v <= 0:
            raise ValueError("page_count must be positive")
        return v

    @field_validator("published_date")
    def published_date_not_future(cls, v):
        if v > date.today():
            raise ValueError("published_date cannot be in the future")
        return v


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None


class BookSearchModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None


## --- 4. Detailed Book Model for Relationships ---
class BookDetailModel(Book):
    reviews: List["ReviewModel"] = []
    tags: List["TagModel"] = []


## --- 5. Response Models ---
class BookResponse(BaseModel):
    uid: UUID
    user_uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)  # works with SQLModel objects


class BookUpdateResponseModel(BaseModel):
    message: str
    old_book: BookResponse
    updated_book: BookResponse


class BookDeleteResponseModel(BaseModel):
    message: str
    deleted_book: BookResponse


# Rebuild models with forward references after all classes are defined
def rebuild_models():
    """Rebuild models to resolve forward references."""
    try:
        from src.reviews.schemas import ReviewModel
        from src.tags.schemas import TagModel

        BookDetailModel.model_rebuild()
    except Exception:
        pass  # Ignore if dependencies aren't loaded yet


rebuild_models()
