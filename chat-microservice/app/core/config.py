class Settings:
    # Default to an in-memory SQLite database for simplicity if not overridden by environment variables
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./test_chat.db"
    # Example for PostgreSQL (if you set this in your environment)
    # SQLALCHEMY_DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/appdb")

    # Secret key for JWT (example, replace with a real secret in production)
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

print("app.core.config.py created/updated with default settings.")
