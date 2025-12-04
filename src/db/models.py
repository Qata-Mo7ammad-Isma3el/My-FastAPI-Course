from sqlmodel import SQLModel, Field, Relationship, Index
from uuid import UUID, uuid4
from datetime import datetime, date, timezone
from typing import Optional, List


# > in this way we are using the explicit way of defining the models in sqlmodel
# > this is more flexible and more powerful when you want to use advanced features of sqlalchemy
# > but sqlmodel also allows you to use the implicit way of defining the models
# > which is more concise and easier to read but less flexible
# > this is done by just defining the fields as class attributes without using Column
# > both ways are valid and can be used together in the same project


class TimestampMixin:
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)  
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)  
    )

    def update_timestamp(self):
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

class User(SQLModel, TimestampMixin, table=True):
    __tablename__ = "users_table"
    __table_args__ = (
        Index("idx_user_email", "email", unique=True),
        Index("idx_user_username", "username", unique=True),
    )
    # > Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    # > Basic info
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(default="user")

    # > Auth / verification
    is_verified: bool = Field(default=False)
    password_hash: str = Field(..., exclude=True)

    # > Relationships
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<USER {self.username} ({self.email})>"


class BookTag(SQLModel, table=True):
    __tablename__ = "book_tags"
    book_id: UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Book(SQLModel, TimestampMixin, table=True):
    __tablename__ = "books"
    __table_args__ = (
        Index("idx_book_title", "title"),
        Index("idx_book_author", "author"),
        Index("idx_book_user", "user_uid"),
        Index("idx_book_created", "created_at"),
    )
    # > Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # > Book fields
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users_table.uid")

    # > Relationships
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    ## Validation methods
    def validate_page_count(self):
        if self.page_count <= 0:
            raise ValueError("Page count must be positive")

    def validate_published_date(self):
        if self.published_date > date.today():
            raise ValueError("Published date cannot be in the future")

    def before_insert(self):
        """Called before inserting into database"""
        self.validate_page_count()
        self.validate_published_date()
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<BOOK {self.title} by {self.author}>"


class Review(SQLModel, TimestampMixin, table=True):
    __tablename__ = "reviews"
    __table_args__ = (
        Index("idx_review_user_book", "user_uid", "book_uid"),
        Index("idx_review_rating", "rating"),
        Index("idx_review_created", "created_at"),
    )
    # > Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    # > Reviews fields
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users_table.uid")
    book_uid: Optional[UUID] = Field(default=None, foreign_key="books.uid")

    # > Relationships
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    ## Validation methods
    def validate_rating(self):
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

    def before_insert(self):
        self.validate_rating()
        self.updated_at = datetime.now(timezone.utc)

    def __repr__(self):
        return f"<REVIEW {self.rating} stars by User {self.user_uid} for Book {self.book_uid}>"


class Tag(SQLModel, TimestampMixin, table=True):
    __tablename__ = "tags"
    __table_args__ = (Index("idx_tag_name", "name", unique=True),)
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(...)

    # > Relationships
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


# >           ┌─────────────────────┐
# >           │        User         │
# >           │  uid (PK)           │
# >           │  username           │
# >           └─────────┬───────────┘
# >                     │ 1-to-many
# >                     │
# >            ┌────────▼─────────┐
# >            │       Book       │
# >            │  uid (PK)        │
# >            │  user_uid (FK)───────┐
# >            └────────┬─────────┘   │
# >                     │ 1-to-many   │
# >                     │             │
# >            ┌────────▼─────────┐   │
# >            │      Review      │   │
# >            │ user_uid (FK)────┘   │
# >            │ book_uid (FK)────────┘
# >            └──────────────────────┘
# >
# >
# >    Books ⬅── Many-to-Many ──➡ Tags
# > BookTag table
# >
# > BookTag Table:
# > -------------------------
# > book_id (FK → books.uid)
# > tag_id  (FK → tags.uid)
# > PRIMARY KEY(book_id, tag_id)
