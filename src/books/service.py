from sqlalchemy.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel, BookUpdate
from src.db.models import Book
from sqlalchemy import select, desc
from datetime import date, datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))  # type: ignore

        result = await session.execute(statement)
        return result.scalars().all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))  # type: ignore

        result = await session.execute(statement)
        return result.scalars().all()

    async def get_books(self, book_uid: str, session: AsyncSession):
        # statement = select(Book).where(Book.uid == book_uid)
        # result = await session.execute(statement)
        # return result.first()
        statement = select(Book).filter_by(uid=book_uid)
        result = await session.execute(statement)
        # book = result.first()
        book = result.scalars().first()

        return book if book is not None else None

    async def create_books(
        self, book_data: BookCreateModel, user_uid, session: AsyncSession
    ):
        book_data_dick = book_data.model_dump()

        new_book = Book(**book_data_dick)
        new_book.user_uid = user_uid
        # new_book.published_date = datetime.strptime(book_data_dick['published_date'],"%Y-%m-%d")

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

    async def update_books(
        self, book_uid: str, booke_data: BookUpdate, session: AsyncSession
    ):
        book_t0_update = await self.get_books(book_uid, session)
        if not book_t0_update:
            return None

        for key, value in booke_data.model_dump().items():
            setattr(book_t0_update, key, value)

        await session.commit()
        await session.refresh(book_t0_update)
        return book_t0_update

    async def delete_books(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_books(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
