from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class CreateUser(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    email: EmailStr
    password: str


class GetUserResponse(BaseModel):
    id: int
    email: EmailStr

    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
