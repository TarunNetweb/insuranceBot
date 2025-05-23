from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.services.user_service import UserService
from app.models.user_model import User # SQLAlchemy model with orm_mode = True
from app.database.session import get_db # Dependency to get DB session

router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)

# Utility function to get UserService instance with a DB session
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """
    Dependency function to get an instance of UserService.
    Injects a database session into the UserService.
    """
    return UserService(db)

@router.get("/filter_by_name", response_model=List[User])
async def filter_users_by_name(
    first_name_starts_with: Optional[str] = None,
    last_name_ends_with: Optional[str] = None,
    user_service: UserService = Depends(get_user_service)
):
    """
    Filters users based on name criteria.

    Allows filtering by:
    - `first_name_starts_with`: Users whose first name starts with the provided string (case-insensitive).
    - `last_name_ends_with`: Users whose last name ends with the provided string (case-insensitive).

    Both parameters are optional. If a parameter is provided as an empty string or only whitespace,
    it will be treated as if it were not provided.

    Returns:
        A list of User objects matching the criteria.
    """
    # Treat empty strings or whitespace-only strings as None (no filter)
    if first_name_starts_with is not None and not first_name_starts_with.strip():
        first_name_starts_with = None 
    if last_name_ends_with is not None and not last_name_ends_with.strip():
        last_name_ends_with = None

    # If both criteria are effectively None after stripping, it might be desirable to return
    # all users, or a specific response (e.g., an error or an empty list).
    # The current repository implementation returns all users if no criteria are passed.
    # If specific behavior for "no valid criteria" is needed, add it here.
    # For example, to prevent fetching all users without any filter:
    # if first_name_starts_with is None and last_name_ends_with is None:
    #     raise HTTPException(status_code=400, detail="At least one name filter must be substantially provided.")


    users = await user_service.fetch_users_by_name_filter(
        first_name_starts_with=first_name_starts_with,
        last_name_ends_with=last_name_ends_with
    )
    return users

# Note: The response_model=List[User] relies on User model having Config.orm_mode = True,
# which was addressed in a previous step.
# This controller provides an HTTP interface to the user filtering functionality.
