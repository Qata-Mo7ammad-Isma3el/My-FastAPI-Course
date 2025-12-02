from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List, Annotated, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Assuming these are imported, including the new response schemas
from src.books.schemas import (
    Book,
    BookUpdateModel,
    BookUpdateResponseModel,
    BookDeleteResponseModel,
    BookCreateModel,
    BookResponse,
    BookDetailModel,
)
from src.db.main import get_session
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


#! --- GET ALL BOOKS ---
@book_router.get("/", response_model=List[Book])
async def get_all_books(
    session: Annotated[AsyncSession, Depends(get_session)],
    User_token: Annotated[dict, Depends(access_token_bearer)],
    _: Annotated[bool, Depends(role_checker)],
) -> List[
    Book
]:  # > Changed Optional[List[Book]] to List[Book] since it returns an empty list [] if none found, not None
    books = await book_service.get_all_books(session)
    return books

#! --- GET SINGLE BOOK ---
@book_router.get("/{book_uid}", response_model=BookDetailModel)
async def get_book(
    book_uid: Annotated[UUID, "Book UID from path"],
    session: Annotated[AsyncSession, Depends(get_session)],
    User_token: Annotated[dict, Depends(access_token_bearer)],
    _: Annotated[bool, Depends(role_checker)],
) -> Book:
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


#! --- GET ALL User BOOKS ---
@book_router.get("/user{user_uid}", response_model=List[Book])
async def get_user_book_submissions(
    user_uid: Annotated[UUID, "User UID from path"],
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
) -> List[Book]:
    books = await book_service.get_user_books(user_uid, session)
    return books


#! --- CREATE BOOK ---
@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel,
    session: Annotated[AsyncSession, Depends(get_session)],
    User_token: Annotated[dict, Depends(access_token_bearer)],
    _: Annotated[bool, Depends(role_checker)],
) -> Book:
    user_uid = User_token.get("user")["uid"]
    new_book = await book_service.create_book(book_data, user_uid, session)
    return new_book





#! --- UPDATE BOOK (CRITICAL FIX APPLIED) ---
@book_router.patch("/{book_uid}", response_model=BookUpdateResponseModel)
async def update_book(
    book_uid: Annotated[UUID, "Book UID from path"],
    book_update_data: BookUpdateModel,
    session: Annotated[AsyncSession, Depends(get_session)],
    User_token: Annotated[dict, Depends(access_token_bearer)],
    _: Annotated[bool, Depends(role_checker)],
) -> BookUpdateResponseModel:

    current_book = await book_service.get_book(book_uid, session)
    if not current_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    old_book_data = current_book.model_copy()
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    response_data = {
        "message": "Book Updated Successfully!",
        "old_book": old_book_data,  # This is the *unmodified* copy
        "updated_book": updated_book,  # This is the modified object
    }
    return response_data


#! --- DELETE BOOK ---
@book_router.delete(
    "/{book_uid}",
    status_code=status.HTTP_200_OK,
    response_model=BookDeleteResponseModel,
)
async def delete_book(
    book_uid: Annotated[UUID, "Book UID from path"],
    session: Annotated[AsyncSession, Depends(get_session)],
    User_token: Annotated[dict, Depends(access_token_bearer)],
    _: Annotated[bool, Depends(role_checker)],
) -> BookDeleteResponseModel:
    book_to_delete = await book_service.delete_book(book_uid, session)

    if book_to_delete:
        response_data = {
            "message": "Book Deleted Successfully!",
            "deleted_book": book_to_delete,
        }
        return response_data
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
