from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1450, le=2100)
    isbn: Optional[str] = Field(None, max_length=13)

    @validator('isbn')
    def validate_isbn(cls, v):
        if v and len(v) not in [10, 13]:
            raise ValueError('ISBN moet 10 of 13 karakters zijn')
        return v

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1450, le=2100)
    isbn: Optional[str] = Field(None, max_length=13)

class Book(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True