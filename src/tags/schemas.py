from uuid import UUID
from datetime import datetime
from typing import List

from pydantic import BaseModel


class TagModel(BaseModel):
    uid: UUID
    name: str
    created_at: datetime

class TagCreateModel(BaseModel):
    name: str

class TagAddModel(BaseModel):
    tags: List[TagCreateModel]