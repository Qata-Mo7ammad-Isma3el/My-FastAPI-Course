# in this file were going to put the service functions for the books app
#! any async function you have to call it using await thats not optional
#! every thing starts with async must be used with await
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel, BookUpdateModel, BookSearchModel
from sqlmodel import select, desc, func
from sqlalchemy.orm import selectinload
from src.db.models import Book
from typing import Optional, List  # Recommended for better type hinting
from datetime import datetime
from uuid import UUID
from src.errors import BookNotFound, InsufficientPermission


class BookService:
    async def get_all_books(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[Book]:
        statement = (
            select(Book).order_by(desc(Book.created_at)).offset(skip).limit(limit)
        )
        results = await session.exec(statement)
        return results.all()

    async def get_user_books(self, user_uid: UUID, session: AsyncSession) -> List[Book]:
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        results = await session.exec(statement)
        return results.all()

    async def get_book(self, book_uid: UUID, session: AsyncSession) -> Optional[Book]:
        statement = (
            select(Book)
            .where(Book.uid == book_uid)
            .options(selectinload(Book.reviews), selectinload(Book.tags))
        )
        results = await session.exec(statement)
        book = results.first()
        if not book:
            raise BookNotFound()
        return book  # Returns Book or None

    async def create_book(
        self, book_data: BookCreateModel, user_uid: str, session: AsyncSession
    ) -> Book:
        book_data_dict = book_data.model_dump()
        new_book = Book.model_validate(book_data_dict)
        new_book.user_uid = user_uid
        session.add(
            new_book
        )  # > you dont have to use await with this because it's done in python memory
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_book(
        self,
        book_uid: UUID,
        user_uid: UUID,
        update_data: BookUpdateModel,
        session: AsyncSession,
    ) -> Book:
        book_to_update = await self.get_book(book_uid, session=session)
        if book_to_update is not None:
            #! Use exclude_unset=True to only update provided fields
            book_update_dict = update_data.model_dump(exclude_unset=True)
            if book_to_update.user_uid != user_uid:
                raise InsufficientPermission()
            for k, v in book_update_dict.items():
                setattr(book_to_update, k, v)
            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        return None

    # > ... delete_book (CRITICAL fix: await, and removed unnecessary refresh)
    async def delete_book(self, book_uid: UUID, session: AsyncSession) -> Book:
        book_to_delete = await self.get_book(book_uid, session=session)
        await session.delete(book_to_delete)
        await session.commit()
        # // Removed unnecessary await session.refresh()
        return book_to_delete

    async def search_books(
        self,
        session: AsyncSession,
        search_params: BookSearchModel,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Book]:
        statement = select(Book)

        if search_params.title:
            statement = statement.where(
                func.lower(Book.title).ilike(f"%{search_params.title}%")
            )
        if search_params.author:
            statement = statement.where(
                func.lower(Book.title).ilike(f"%{search_params.author}%")
            )
        if search_params.publisher:
            statement = statement.where(
                func.lower(Book.title).ilike(f"%{search_params.publisher}%")
            )

        statement = statement.order_by(desc(Book.created_at)).offset(skip).limit(limit)
        results = await session.exec(statement)
        return results.all()
