from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import jwt
from repositories.user_repository import update_user_by_id,delete_user_by_id, search_user, get_all_users,get_user_by_username,get_user_by_id
from utils.helpers import hash_password
from core.config import settings


def update_user(db: Session, user_id,username: str, email: str, first_name: str,last_name:str,  phone_number: str,password: str):
    hashed_password = hash_password(password)
    print(" haedhed password ", hashed_password)
    user = get_user_by_username(db, username)
    if not user:
        return {"Message":"Sorry no user found"}
    return update_user_by_id(db, user_id,username, email, first_name, last_name, phone_number,hashed_password),

def delete_user(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    print(" user ", user)
    if not user:
        return {"Message":"Sorry no user found"}
    return delete_user_by_id(db, user_id),

def search_user_all(db: Session, username: str = None, email: str = None, first_name: str = None):
    users = search_user(db, username, email, first_name)
    if not users:
        return {"message": "No users found"}
    return users

def fetch_all_users(db: Session):
    return get_all_users(db)