from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from .schemas import Book, BookUpdate, BookCreateModel,BookDetailModel
from src.db.main import get_session
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@book_router.get("/", response_model=list[BookDetailModel])
async def get_all_book(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    books = await book_service.get_all_books(session)
    return books

@book_router.get("/user/{user_uid}", response_model=list[Book])
async def get_user_book_submissions(
    user_uid:str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    books = await book_service.get_user_books(user_uid,session)
    return books


@book_router.post("/book", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_a_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    user_uid = token_details.get('user', {}).get('user_uid')
    new_book = await book_service.create_books(book_data,user_uid,session)
    return new_book


@book_router.get("/{book_uid}", response_model=BookDetailModel)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    book = await book_service.get_books(book_uid, session)
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.patch("/{book_uid}")
async def update_book(
    book_uid: str,
    book_update_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    update_book = await book_service.update_books(book_uid, book_update_data, session)
    if update_book:
        return update_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )


@book_router.delete("/{book_uid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
    _: bool = Depends(role_checker),
):
    book_to_delete = await book_service.delete_books(book_uid, session)
    if book_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    else:
        return {}
