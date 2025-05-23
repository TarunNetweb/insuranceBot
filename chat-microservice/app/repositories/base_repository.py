from sqlalchemy.orm import Session
from sqlalchemy import select # `update` and `delete` are not directly used from sqlalchemy here
from app.models.base_model import Base # Assuming Base is the declarative_base from models
from typing import TypeVar, Generic, Type, Any, List, Optional

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """
    A generic base repository providing common CRUD operations for SQLAlchemy models.

    This class is designed to be inherited by specific model repositories.
    It uses SQLAlchemy session for database interactions.
    """
    def __init__(self, db: Session, model: Type[ModelType]):
        """
        Initializes the BaseRepository.

        Args:
            db: The SQLAlchemy database session.
            model: The SQLAlchemy model class that this repository will manage.
        """
        self.db = db
        self.model = model

    def get_by_id(self, item_id: Any) -> Optional[ModelType]:
        """
        Retrieves an item by its primary key.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The model instance if found, otherwise None.
        """
        return self.db.get(self.model, item_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieves all items of the model type, with optional pagination.

        Args:
            skip: The number of items to skip (for pagination). Defaults to 0.
            limit: The maximum number of items to return (for pagination). Defaults to 100.

        Returns:
            A list of model instances.
        """
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(statement).scalars().all())

    def create(self, **kwargs: Any) -> ModelType:
        """
        Creates a new item in the database.

        Args:
            **kwargs: Arbitrary keyword arguments representing the attributes of the item to create.
                      These should match the model's attributes.

        Returns:
            The newly created and persisted model instance.
        """
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, item_id: Any, **kwargs: Any) -> Optional[ModelType]:
        """
        Updates an existing item in the database.

        The item is first fetched by its ID. If found, its attributes are updated
        with the provided keyword arguments, and changes are committed.

        Note:
            This method uses a fetch-then-update pattern. For scenarios with many
            concurrent updates, alternative patterns or optimistic locking might be
            considered. `self.db.get()` is used for fetching by primary key.

        Args:
            item_id: The ID of the item to update.
            **kwargs: Arbitrary keyword arguments representing the attributes to update
                      and their new values.

        Returns:
            The updated model instance if found and updated, otherwise None.
        """
        db_obj = self.db.get(self.model, item_id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            self.db.add(db_obj) # Using add for session tracking, can also be self.db.merge(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
        
    def delete(self, item_id: Any) -> Optional[ModelType]:
        """
        Deletes an item from the database by its ID.

        The item is first fetched by its ID. If found, it is deleted from the database.

        Args:
            item_id: The ID of the item to delete.

        Returns:
            The model instance that was deleted if found, otherwise None.
        """
        db_obj = self.db.get(self.model, item_id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj
