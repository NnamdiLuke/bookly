from typing import Optional,List
from pydantic import BaseModel
import uuid
from datetime import datetime
from datetime import date
from src.db.models import Review
from src.tags.schemas import TagModel

class Book(BaseModel):
    uid:uuid.UUID
    title:str
    author:str
    publisher:str
    published_date:date
    page_count: int
    language:str
    created_at:datetime
    updated_at:datetime
    
class BookDetailModel(Book):
    reviews:List[Review]
    tags:List[TagModel]
    


class BookCreateModel(BaseModel):
    title:str
    author:str
    publisher:str
    published_date:date
    page_count: int
    language:str

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
