from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from typing import List

from src.reviews.schemas import ReviewModel

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
    created_at: datetime
    updated_at: datetime


# --- 3. Request Models ---
class BookCreateModel(BookBase):
    pass  # inherits all fields


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[date] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

## --- 5. Response Models ---
class BookResponse(BaseModel):
    uid: UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # works with SQLModel objects


class BookUpdateResponseModel(BaseModel):
    message: str
    old_book: BookResponse
    updated_book: BookResponse


class BookDeleteResponseModel(BaseModel):
    message: str
    deleted_book: BookResponse


class BookDetailModel(Book):
    reviews: List[ReviewModel]
