from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.models.base_model import Base # Assuming Base is the declarative_base from models
from typing import TypeVar, Generic, Type, Any

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, item_id: Any) -> ModelType | None:
        return self.db.get(self.model, item_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(statement).scalars().all())

    def create(self, **kwargs: Any) -> ModelType:
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, item_id: Any, **kwargs: Any) -> ModelType | None:
        # It's often better to fetch, then update attributes, then commit,
        # but for a generic repo, this is a common pattern.
        # However, self.db.get() is preferred for fetching by PK.
        db_obj = self.db.get(self.model, item_id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            self.db.add(db_obj) # or self.db.merge(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
        
    def delete(self, item_id: Any) -> ModelType | None:
        db_obj = self.db.get(self.model, item_id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
        return db_obj
