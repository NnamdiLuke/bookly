from pydantic import BaseModel,Field
from datetime import datetime
import uuid
from typing import List
from src.books.schemas import Book
from src.reviews.schemas import ReviewResponseModel

class UserCreateModel(BaseModel):
    username:str = Field(max_length=8)
    first_name: str
    last_name: str
    email:str = Field(max_length=40)
    password:str = Field(min_length=8)
    
class UserResponseModel(BaseModel):
    uid:uuid.UUID
    username:str
    email:str
    first_name:str
    last_name:str
    is_verified:bool
    password_hash: str = Field(exclude=True)
    created_at:datetime
    updated_at:datetime
    
class UserBooksModel(UserResponseModel):
    books:List[Book]
    reviews:List[ReviewResponseModel]
    
class UserLoginModel(BaseModel):
    email:str = Field(max_length=40)
    password:str = Field(min_length=8)