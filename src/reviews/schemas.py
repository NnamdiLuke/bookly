from pydantic import BaseModel,Field
from datetime import datetime
import uuid

class ReviewResponseModel(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: uuid.UUID | None
    book_uid: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

class ReviewCreateModel(BaseModel):
    rating: int = Field(le=5)
    review_text:str
    