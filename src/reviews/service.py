from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel, ReviewUpdateModel, ReviewDetailModel
from typing import Annotated, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc, func
from uuid import UUID
from fastapi import HTTPException, status
import logging
from typing import List
from decimal import Decimal

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: UUID,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ) -> ReviewDetailModel:
        try:
            book = await book_service.get_book(book_uid, session)  ## BOOK object
            user = await user_service.get_user_by_email(
                user_email, session
            )  ## USER object
            # Check if the user has already reviewed this book
            statement = select(Review).where(
                Review.user_uid == user.uid, Review.book_uid == book_uid
            )
            result = await session.exec(statement)
            existing_review = result.first()

            if existing_review:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already reviewed this book. Update your existing review instead.",
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

    async def get_all_reviews(
        self,
        session: AsyncSession,
        book_uid: Optional[UUID] = None,
        user_uid: Optional[UUID] = None,
        min_rating: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Review]:

        statement = select(Review)

        if book_uid:
            statement = statement.where(Review.book_uid == book_uid)
        if user_uid:
            statement = statement.where(Review.user_uid == user_uid)
        if min_rating:
            statement = statement.where(Review.rating >= min_rating)

        statement = (
            statement.order_by(desc(Review.created_at)).offset(skip).limit(limit)
        )
        result = await session.exec(statement)
        return result.all()

    async def delete_review_from_book(
        self, review_uid: UUID, user_email: str, session: AsyncSession
    ) -> Review:
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)

        if review.user_uid != user.uid : # and user.role != "admin"
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this review or user id incorrect",
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

    async def get_book_review_stats(self, book_uid: UUID, session: AsyncSession) -> dict:
        """Get review statistics for a book"""
        
        statement = select(
            func.count(Review.uid).label("total_reviews"),
            func.coalesce(func.avg(Review.rating), 0).label("average_rating"),
            func.coalesce(func.min(Review.rating), 0).label("min_rating"),
            func.coalesce(func.max(Review.rating), 0).label("max_rating")
        ).where(Review.book_uid == book_uid)
        
        result = await session.exec(statement)
        stats = result.one()
        
        # Handle None values safely
        avg_rating = float(stats.average_rating) if stats.average_rating is not None else 0.0
        
        return {
            "book_uid": book_uid,
            "total_reviews": stats.total_reviews,  
            "average_rating": round(avg_rating, 2),
            "min_rating": stats.min_rating or 0,
            "max_rating": stats.max_rating or 0,
            "rating_distribution": await self.get_rating_distribution(book_uid, session)
        }

    async def get_rating_distribution(self, book_uid: UUID, session: AsyncSession) -> dict:
        """Get count of each rating (1-5) for a book"""
        statement = select(
            Review.rating,
            func.count(Review.uid).label("count")
        ).where(
            Review.book_uid == book_uid
        ).group_by(Review.rating).order_by(Review.rating)
        
        result = await session.exec(statement)
        distribution = {row.rating: row.count for row in result.all()}
        
        # Ensure all ratings 1-5 are present
        return {rating: distribution.get(rating, 0) for rating in range(1, 6)}