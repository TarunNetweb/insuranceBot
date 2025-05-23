from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional # Optional might be used for other methods, List is for return type
from app.models.user_model import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    Repository for user-related database operations.
    This class provides an abstraction layer for accessing user data
    and inherits common CRUD operations from BaseRepository.
    """
    def __init__(self, db: Session):
        """
        Initializes the UserRepository.

        Args:
            db (Session): The SQLAlchemy database session to be used for operations.
        """
        super().__init__(db, User)

    def get_users_by_name_criteria(
        self, 
        first_name_starts_with: Optional[str] = None, 
        last_name_ends_with: Optional[str] = None
    ) -> List[User]:
        """
        Retrieves users based on specified name criteria.

        Filters users where the first name starts with `first_name_starts_with` (case-insensitive)
        and/or the last name ends with `last_name_ends_with` (case-insensitive).
        If a criterion is None or an empty string, it is not applied.

        Args:
            first_name_starts_with (Optional[str]): The prefix for the user's first name.
                                                      Filtering is case-insensitive.
            last_name_ends_with (Optional[str]): The suffix for the user's last name.
                                                   Filtering is case-insensitive.

        Returns:
            List[User]: A list of User objects matching the criteria.
                        Returns all users if no criteria are provided or if provided criteria are empty.
        """
        stmt = select(self.model)
        filters = []

        if first_name_starts_with: # Checks for non-empty string
            filters.append(self.model.first_name.ilike(f"{first_name_starts_with}%"))
        
        if last_name_ends_with: # Checks for non-empty string
            filters.append(self.model.last_name.ilike(f"%{last_name_ends_with}"))
        
        if filters:
            stmt = stmt.where(*filters)
        
        users = list(self.db.execute(stmt).scalars().all())
        return users

# Further methods specific to User model, like get_by_username, get_by_email,
# would be added here.
