from pydantic import BaseModel
from sqlmodel import Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class ReviewModel(BaseModel):
    #> Unique identifier
    uid: UUID 
    
    #> Reviews fields
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)
    user_uid: Optional[UUID] 
    book_uid: Optional[UUID] 
    
    #> Timestamps
    created_at: datetime 
    updated_at: datetime 


class ReviewCreateModel(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review_text: str = Field(default=None, max_length=2000)
    
class ReviewUpdateModel(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    review_text: Optional[str] = Field(default=None, max_length=2000)


## -----------------------------------------------
class ReviewResponseUpdateModel(BaseModel):
    message: str
    old_review: ReviewModel
    updated_review: ReviewModel

class ReviewDeleteResponseModel(BaseModel):
    message: str
    deleted_review: ReviewModel
