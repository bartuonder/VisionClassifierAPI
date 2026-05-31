from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=9, max_length=20)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=9, max_length=20)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


class TaskSubmitResponse(BaseModel):
    message: str
    task_id: int
    status_url: str


class TaskStatusResponse(BaseModel):
    task_id: int
    status: str
    prediction: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True