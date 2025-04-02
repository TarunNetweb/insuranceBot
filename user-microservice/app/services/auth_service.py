from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt
from repositories.user_repository import get_user_by_username, create_user
from utils.helpers import hash_password, verify_password, create_access_token
from core.config import settings

def register_user(db: Session, username: str, email: str, first_name: str,last_name:str,password: str, role: str, phone_number: str):
    if get_user_by_username(db, username):
        raise ValueError("Username already taken")
    hashed_password = hash_password(password)
    return create_user(db, username, email, first_name, last_name,hashed_password,role,phone_number),

def authenticate_user( db: Session,username: str, password: str):
    print(type(db))
    user = get_user_by_username(db, username)
    print("user ", user)
    if not user or not verify_password(password, user.password):  
        return None

    token_data = {"sub": user.username, "role": user.role}  
    access_token = create_access_token(token_data)
    
    return access_token

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# def generate_jwt(user):
#     access_token = create_access_token({"sub": user.username,"role": user.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
#     return access_token