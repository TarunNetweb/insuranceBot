from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # Assuming settings.SQLALCHEMY_DATABASE_URL exists

# Use the database URL from settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} # Needed only for SQLite if using it
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Optional: A simple way to get a DB session, can be used by a dependency injector later
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

print("app.database.session.py created/updated with SessionLocal.")
