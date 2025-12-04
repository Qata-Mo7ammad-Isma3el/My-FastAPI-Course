from uuid import UUID
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel
from pydantic import field_validator, Field
import re

if TYPE_CHECKING:
    from src.books.schemas import BookResponse, Book


class TagModel(BaseModel):
    uid: UUID
    name: str
    created_at: datetime


class TagCreateModel(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

    @field_validator("name")
    def validate_tag_name(cls, v: str):
        # Remove extra whitespace
        v = v.strip()

        # Ensure it's not empty after stripping
        if not v:
            raise ValueError("Tag name cannot be empty")

        # Validate format (alphanumeric, spaces, hyphens, underscores)
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", v):
            raise ValueError(
                "Tag name can only contain letters, numbers, spaces, hyphens, and underscores"
            )

        # Convert to lowercase for consistency
        return v.lower()

    @field_validator("name")
    def prevent_common_bad_words(cls, v: str):
        bad_words = ["admin", "system", "root", "null", "undefined"]
        if v.lower() in bad_words:
            raise ValueError(f'Tag name "{v}" is not allowed')
        return v


class TagAddModel(BaseModel):
    tags: List[TagCreateModel]


# schemas.py
class TagResponseModel(BaseModel):
    uid: UUID
    name: str
    created_at: datetime
    book_count: int = 0  # Number of books with this tag

    class Config:
        from_attributes = True


class TagWithBooksModel(TagResponseModel):
    books: List["Book"] = []  # You'll need to import Book schema


class TagUpdateModel(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)

    @field_validator("name")
    def validate_tag_name(cls, v):
        if v is not None:
            return TagCreateModel.validate_tag_name(v)
        return v


class TagDetailModel(TagModel):
    # Use string forward reference
    books: List["BookResponse"] = []
