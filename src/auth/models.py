from sqlmodel import SQLModel, Field, Column
from uuid import UUID, uuid4
import sqlalchemy.dialects.postgresql as pg
import sqlalchemy as sa
from datetime import datetime


# > in this way we are using the explicit way of defining the models in sqlmodel
# > this is more flexible and more powerful when you want to use advanced features of sqlalchemy
# > but sqlmodel also allows you to use the implicit way of defining the models
# > which is more concise and easier to read but less flexible
# > this is done by just defining the fields as class attributes without using Column
# > both ways are valid and can be used together in the same project


class User(SQLModel, table=True):
    __tablename__ = "users_table"
    uid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(
            pg.UUID,
            primary_key=True,
            nullable=False,
        ),
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR,
            nullable=False,
            server_default="user",
        )
    )

    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            pg.TIMESTAMP,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
    )

    class Config:
        from_attributes = True

    def __repr__(self):
        return f"<USER {self.username} ({self.email})>"
