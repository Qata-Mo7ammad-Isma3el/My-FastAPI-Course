from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime, date
from sqlmodel import SQLModel, Field # Assuming SQLModel is used for the DB model

# --- 1. Base Database/Response Model ---
class BookBase(BaseModel):
    # Fields that MUST be present for a full representation
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

# If this class is your SQLModel table (contains all DB fields):
class Book(BookBase, SQLModel, table=True):
    # Primary Key/Unique ID (DB-generated)
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    
    # Timestamps (DB-generated, optional on creation)
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)

# --- 2. Request Models ---

# Model for creating a book (requires all non-DB generated fields)
class BookCreateModel(BookBase):
    pass # Inherits all required fields from BookBase

# Model for updating a book (all fields should be optional)
class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    # published_date is usually excluded from updates

##---------------- API Response Models ----------------##
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
        orm_mode = True          # let Pydantic read SQLAlchemy objects

class BookUpdateResponseModel(BaseModel):
    message: str
    old_book: BookResponse
    updated_book: BookResponse

class BookDeleteResponseModel(BaseModel):
    message: str
    deleted_book: BookResponse