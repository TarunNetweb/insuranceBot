from fastapi import FastAPI

# Import the Socket.IO ASGI application
from app.services.chat_service import socket_app

# Import controllers to ensure Socket.IO event handlers are registered.
# This import triggers the execution of @sio.event and @sio.on decorators
# in the files imported by app.api.controllers (i.e., chat_controller.py).
from app.api import controllers 

# Import Base and engine for database table creation
from app.models.base_model import Base 
from app.database.session import engine

# Import the user router
from app.api.controllers.user_controller import router as user_router

# Initialize database: Create all tables if they don't exist.
# Note: In a production environment, database migrations (e.g., using Alembic)
# are a more robust approach than `create_all`.
# This requires that all SQLAlchemy models are imported and known to `Base.metadata`.
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    # In a production app, use proper logging.
    # Depending on the severity, you might want to prevent app startup.
    print(f"CRITICAL: Error creating database tables: {e}") 
    # Consider raising the exception or sys.exit(1) if DB is essential for startup.

# Initialize FastAPI application
app = FastAPI(
    title="Chat Microservice",
    description="Handles real-time chat functionalities via WebSockets and basic user/message management.",
    version="0.1.0"
)

# Mount the Socket.IO application at the "/ws" path.
# All WebSocket traffic to "/ws" will be handled by `socket_app`.
app.mount("/ws", socket_app)

# Include HTTP API routers
app.include_router(user_router) # For user-related endpoints like /users/filter_by_name

# Basic HTTP root endpoint for health check or welcome message.
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chat Microservice. Connect to /ws for chat."}

# To run this application (example):
# uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
#
# This setup ensures that:
# 1. FastAPI application is initialized.
# 2. Database tables are created/verified based on SQLAlchemy models.
# 3. Socket.IO event handlers defined in controllers are registered with the `sio` instance.
# 4. The Socket.IO ASGI app is mounted under FastAPI, making it accessible via the specified path.
# 5. HTTP routers (like user_router) are included for regular API endpoints.
