from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel, ReviewUpdateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from uuid import UUID
from fastapi import HTTPException, status
import logging
from typing import List

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: UUID,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> Review:
        try:
            book = await book_service.get_book(book_uid, session)  ## BOOK object
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found",
                )
            user = await user_service.get_user_by_email(
                user_email, session
            )  ## USER object
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            new_review = Review.model_validate(review_data.model_dump())
            new_review.book = book  # > Associate review with book
            new_review.user = user  # > Associate review with user
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except Exception as e:
            logging.error(f"Error adding review to book: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add review to book",
            ) from e

    async def get_review(self, review_uid: UUID, session: AsyncSession) -> Review:
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        review = result.first()
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return review

    async def get_all_reviews(self, session: AsyncSession) -> List[Review]:
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        reviews = result.all()
        return reviews

    async def delete_review_from_book(
        self, review_uid: UUID, user_email: str, session: AsyncSession
    ) -> Review:
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)
        print('*'*50)
        print(f'DELETING REVIEW: {review}')
        print('*'*50)
        
        if not review or (review.user.uid != user.uid):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        await session.delete(review)
        await session.commit()
        return review

    async def update_review(
        self,
        review_uid: UUID,
        user_email: str,
        review_data: ReviewUpdateModel,
        session: AsyncSession,
    ):
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)
        if not review or (review.user.uid != user.uid):
            raise HTTPException(
                detail="Cannot update this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        for key, value in review_data.model_dump().items():
            setattr(review, key, value)
        session.add(review)
        await session.commit()
        await session.refresh(review)
        return review
