from typing import Optional, List
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


class Answer(BaseModel):
    answer: str
    count: Optional[int]


class GetPollResponse(BaseModel):
    poll_id: int
    owner_id: int
    question: str
    created_at: datetime
    answers: List[Answer]


class CreatePoll(BaseModel):
    question: str
    answers: List[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None
