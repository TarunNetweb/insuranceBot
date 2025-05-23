from sqlalchemy import Column, String
from .base_model import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    class Config:
        orm_mode = True # Enables FastAPI to work with SQLAlchemy models directly

# NOTE: Added first_name and last_name. Schema changes may require a database migration 
# (e.g., using Alembic) in a production environment. 
# For development, Base.metadata.create_all() in main.py might handle this if the DB is new 
# or if it's configured to recreate tables, but this is not safe for existing data.
