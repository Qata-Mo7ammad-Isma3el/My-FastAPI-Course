from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Optional
from uuid import UUID
from src.db.main import get_session
from src.reviews.service import ReviewService
from src.db.models import User
from src.reviews.schemas import (
    ReviewCreateModel,
    ReviewUpdateModel,
    ReviewDeleteResponseModel,
    ReviewResponseUpdateModel,
    ReviewDetailModel,
    ReviewResponse,
    ReviewModel,
)
from src.auth.dependencies import get_current_user, RoleChecker


review_service = ReviewService()
Reviews_router = APIRouter()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


# > get all reviews
@Reviews_router.get("/", response_model=list[ReviewModel])
async def get_all_reviews(
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
    book_uid: Optional[UUID] = None,
    user_uid: Optional[UUID] = None,
    min_rating: Optional[int] = Query(None, ge=1, le=5),
    skip: int = 0,
    limit: int = 100,
):
    books = await review_service.get_all_reviews(session)
    return books


# > get a single review
@Reviews_router.get("/{review_uid}", response_model=ReviewDetailModel)
async def get_review(
    review_uid: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
) -> ReviewDetailModel:
    review = await review_service.get_review(review_uid, session)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review


# > get review statistics for a book
@Reviews_router.get("/book/{book_uid}/stats")
async def get_book_review_stats(
    book_uid: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
):
    stats = await review_service.get_book_review_stats(book_uid, session)
    return stats


# > add a review to a book
@Reviews_router.post(
    "/book/{book_uid}",
    status_code=status.HTTP_201_CREATED,
    response_model=ReviewDetailModel,
)
async def add_review_to_book(
    book_uid: UUID,
    review_data: ReviewCreateModel,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
) -> ReviewDetailModel:
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )
    if not new_review:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add review",
        )
    return new_review


# > update a review
@Reviews_router.patch(
    "/{review_uid}",
    response_model=ReviewResponseUpdateModel,
)
async def update_review(
    review_uid: UUID,
    review_data: ReviewUpdateModel,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
):
    current_review = await review_service.get_review(review_uid, session)
    old_review = current_review.model_copy()

    if not current_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    updated_review = await review_service.update_review(
        review_uid=review_uid,
        user_email=current_user.email,
        review_data=review_data,
        session=session,
    )
    if updated_review:
        return {
            "message": "Review updated successfully",
            "old_review": old_review,
            "updated_review": updated_review,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review",
        )


# > delete a review
@Reviews_router.delete(
    "/{review_uid}",
    response_model=ReviewDeleteResponseModel,
)
async def delete_review(
    review_uid: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    _: Annotated[bool, Depends(role_checker)],
):

    deleted_review = await review_service.delete_review_from_book(
        review_uid=review_uid,
        user_email=current_user.email,
        session=session,
    )
    if deleted_review:
        return {
            "message": "Review deleted successfully",
            "deleted_review": deleted_review,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review",
        )
