from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, date
from typing import Optional, List



#> in this way we are using the explicit way of defining the models in sqlmodel
#> this is more flexible and more powerful when you want to use advanced features of sqlalchemy
#> but sqlmodel also allows you to use the implicit way of defining the models
#> which is more concise and easier to read but less flexible
#> this is done by just defining the fields as class attributes without using Column
#> both ways are valid and can be used together in the same project


class User(SQLModel, table=True):
    __tablename__ = "users_table"

    #> Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    #> Basic info
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(default="user")

    #> Auth / verification
    is_verified: bool = Field(default=False)
    password_hash: str = Field(..., exclude=True)

    #> Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    #> Relationships
    books: List['Book'] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List['Review'] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<USER {self.username} ({self.email})>"


class Book(SQLModel, table=True):
    __tablename__ = "books"

    #> Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)

    #> Book fields
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users_table.uid")

    #> Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    #> Relationships
    user: Optional['User'] = Relationship(back_populates="books")
    reviews: List['Review'] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    def __repr__(self):
        return f"<BOOK {self.title} by {self.author}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    
    #> Primary Key
    uid: UUID = Field(default_factory=uuid4, primary_key=True)
    
    #> Reviews fields
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)
    user_uid: Optional[UUID] = Field(default=None, foreign_key="users_table.uid")
    book_uid: Optional[UUID] = Field(default=None, foreign_key="books.uid")
    
    #> Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    #> Relationships
    user: Optional['User'] = Relationship(back_populates="reviews")
    book: Optional['Book'] = Relationship(back_populates="reviews")
    def __repr__(self):
        return f"<REVIEW {self.rating} stars by User {self.user_uid} for Book {self.book_uid}>"