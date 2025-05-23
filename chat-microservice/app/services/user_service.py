import asyncio
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.user_model import User
from app.repositories.user_repository import UserRepository

class UserService:
    """
    Service layer for user-related operations.
    It orchestrates calls to the UserRepository and can include business logic
    before or after data access.
    """
    def __init__(self, db: Session):
        """
        Initializes the UserService.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db # Storing db session if other methods in service might need it directly
        self.user_repository = UserRepository(db)

    async def fetch_users_by_name_filter(
        self, 
        first_name_starts_with: Optional[str] = None, 
        last_name_ends_with: Optional[str] = None
    ) -> List[User]:
        """
        Fetches users based on specified name filtering criteria.

        This method calls the corresponding method in the UserRepository,
        handling the asynchronous execution of the synchronous repository call.

        Args:
            first_name_starts_with (Optional[str]): The prefix for the user's first name.
                                                      Filtering is case-insensitive.
            last_name_ends_with (Optional[str]): The suffix for the user's last name.
                                                   Filtering is case-insensitive.

        Returns:
            List[User]: A list of User objects matching the criteria.
        """
        users = await asyncio.to_thread(
            self.user_repository.get_users_by_name_criteria,
            first_name_starts_with=first_name_starts_with,
            last_name_ends_with=last_name_ends_with
        )
        return users

# Example of other methods that could be in UserService:
# async def create_user(self, user_data: dict) -> User:
#     # Add business logic, validation, hashing password, etc.
#     # new_user = await asyncio.to_thread(self.user_repository.create, **user_data)
#     # return new_user
#
# async def get_user_by_id(self, user_id: int) -> Optional[User]:
#     # user = await asyncio.to_thread(self.user_repository.get_by_id, user_id)
#     # return user
