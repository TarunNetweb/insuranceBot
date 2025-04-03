from pydantic import BaseModel, EmailStr
from typing import Optional

class UserRegisterRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: str
    state: str

    class Config:
        orm_mode = True


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    password: str
    role: str  
