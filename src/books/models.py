# > this file is was made to put the database models for the books app
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import date, datetime
from sqlalchemy import Column
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
from typing import Annotated


class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: UUID = Field(
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
            default=uuid4,
        )
    )

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str

    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=sa.func.now(),
            nullable=False,
        )
    )

    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        )
    )

    def __repr__(self):
        return f"<BOOK {self.title} by {self.author}>"
