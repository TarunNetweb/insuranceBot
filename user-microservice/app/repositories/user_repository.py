from sqlalchemy.orm import Session
from models.base_model import User

def get_user_by_username(db: Session, username: str):
    print(type(db))
    a = db.query(User).filter(User.username == username).first()
    print(" a",a)
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def search_user(db: Session, username: str = None, email: str = None, first_name: str = None):
    query = db.query(User)
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if first_name:
        query = query.filter(User.first_name.ilike(f"%{first_name}%"))
    return query.all()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, username: str, email: str, first_name, last_name,hashed_password: str, role: str, phone_number):
    user = User(username=username, 
                first_name=first_name,
                last_name=last_name,
                email=email, 
                password=hashed_password, 
                role=role, 
                phone_number = phone_number)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
