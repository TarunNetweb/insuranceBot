from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from middleware.auth_middleware import admin_required
from models.user_model import UpdateUserRequest
from services.user_service import update_user , delete_user, search_user_all,fetch_all_users
from database.session import get_db
router = APIRouter()

@router.delete("/delete/{user_id}")
def delete_user_route(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database session is null")
    if admin is None:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    try:
        return delete_user(db, user_id) 
    except (AttributeError, Exception) as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.put("/update/{user_id}")
def update_user_route(user_id: int, request: UpdateUserRequest, db: Session = Depends(get_db),
                      admin=Depends(admin_required)):
    if db is None:
        raise HTTPException(status_code=500, detail="Database session is null")
    if request is None:
        raise HTTPException(status_code=400, detail="Request data is null")
    if admin is None:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    try:
        return update_user(db, user_id, request.username, request.email, request.first_name, 
                           request.last_name, request.phone_number, request.password)
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/search-user")
def search_user_endpoint(
    username: str = None, 
    email: str = None, 
    first_name: str = None, 
    db: Session = Depends(get_db),
    user: dict = Depends(admin_required)  # Restrict to admins only
):
    users = search_user_all(db, username, email, first_name)
    return users

@router.get("/admin/fetch-all-users")
def fetch_all_users_endpoint(
    db: Session = Depends(get_db), 
    user: dict = Depends(admin_required)  ):
    # """ Fetch all registered users (Admin Only). """
    users = fetch_all_users(db)
    return users
