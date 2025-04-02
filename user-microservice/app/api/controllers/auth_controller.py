from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.session import get_db
from services.auth_service import register_user, authenticate_user
from models.user_model import UserRegisterRequest, UserLoginRequest
from middleware.auth_middleware import admin_required

from fastapi import APIRouter, Depends


router = APIRouter()

@router.post("/signup")
def signup(request: UserRegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, request.username, request.email, request.first_name, request.last_name, request.password,request.role,request.phone_number)
        return {"message": "User created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail="error came " + str(e))

@router.post("/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {"access_token": user, "token_type": "bearer"}


@router.get("/admin-only")
def admin_only_route(user: dict = Depends(admin_required)):
    return {"message": f"Welcome Admin {user['username']}! This is a restricted area."}
