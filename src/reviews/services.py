from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from fastapi import status
from sqlmodel import desc, select

user_service = UserService()
book_service = BookService()


class ReviewService:
    
    async def add_review_to_book(self,user_email:str,book_uid:str, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            book = await book_service.get_books(book_uid=book_uid,session=session)
            user = await user_service.get_user_by_email(email=user_email,session=session)
            
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail='Book not found')
            
            review_data_dict = review_data.model_dump()
            new_review = Review(**review_data_dict)
            new_review.user = user
            new_review.book = book
            
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Oops ... Something went wrong')


    async def get_review(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)

        result = await session.exec(statement)

        return result.first()
    
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))

        result = await session.exec(statement)

        return result.all()
    
    async def delete_review_to_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)

        review = await self.get_review(review_uid, session)

        if not review or (review.user != user):
            raise HTTPException(
                detail="Cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        await session.delete(review)

        await session.commit()