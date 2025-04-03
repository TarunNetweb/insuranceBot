from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from middleware.auth_middleware import admin_required
from repositories.user_repository import search_user, get_all_users

from database.session import get_db
router = APIRouter()

@router.get("/admin/search-user")
def search_user_endpoint(
    username: str = None, 
    email: str = None, 
    first_name: str = None, 
    db: Session = Depends(get_db),
    user: dict = Depends(admin_required)  # Restrict to admins only
):
    users = search_user(db, username, email, first_name)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users

@router.get("/admin/fetch-all-users")
def fetch_all_users_endpoint(
    db: Session = Depends(get_db), 
    user: dict = Depends(admin_required)  ):
    """ Fetch all registered users (Admin Only). """
    users = get_all_users(db)
    return users
