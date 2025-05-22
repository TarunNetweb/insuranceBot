from fastapi import FastAPI

# Import the Socket.IO application (ASGI app)
from app.services.chat_service import socket_app

# Import controllers to ensure Socket.IO event handlers in chat_controller.py are registered
# This line triggers the execution of @sio.event and @sio.on decorators in chat_controller
from app.api import controllers 

# Import Base and engine for database table creation
# Assuming Base is defined in base_model.py and accessible via app.models
# And engine is defined in app.database.session
from app.models.base_model import Base 
from app.database.session import engine

# Create all database tables if they don't exist
# This should ideally be handled by migrations (e.g., Alembic) in a production environment,
# but for simplicity in this context, create_all is used.
# Ensure all models are imported somewhere so Base.metadata knows about them.
# The __init__.py files in app.models should ensure this.
try:
    Base.metadata.create_all(bind=engine)
    print("main.py: Database tables checked/created successfully.")
except Exception as e:
    print(f"main.py: Error creating database tables: {e}")
    # Depending on the setup, you might want to exit or handle this error more gracefully.

# Initialize FastAPI application
app = FastAPI(
    title="Chat Microservice",
    description="Handles real-time chat functionalities via WebSockets and basic user/message management.",
    version="0.1.0"
)

# --- Middleware (example, uncomment and configure as needed) ---
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
print("main.py: FastAPI app initialized.")

# --- API Routers (example, uncomment and add your HTTP routers if any) ---
# from app.api.routers import user_router, another_router # Assuming you have these
# app.include_router(user_router.router, prefix="/users", tags=["users"])
# app.include_router(another_router.router, prefix="/items", tags=["items"])
# print("main.py: HTTP API routers included (if any).")


# Mount the Socket.IO application
# This makes the Socket.IO server available under the /ws path
app.mount("/ws", socket_app)
print("main.py: Socket.IO app mounted at /ws.")

# --- Root endpoint (optional) ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Chat Microservice. Connect to /ws for chat."}

print("main.py: Application setup complete.")

# To run this application (assuming this file is chat-microservice/app/main.py):
# uvicorn app.main:app --reload --port 8000
#
# Key things that happened here related to the subtask:
# 1. Imported `socket_app` from `app.services.chat_service`.
# 2. Imported `app.api.controllers` which, through its `__init__.py`, should import `chat_controller`,
#    thereby registering the Socket.IO event handlers defined with `@sio.event` and `@sio.on`.
# 3. Mounted `socket_app` to the FastAPI instance `app` at the path `/ws`.
# 4. Added `Base.metadata.create_all(bind=engine)` for table creation.
#    This relies on:
#    - `Base` being correctly defined (e.g., `Base = declarative_base()` from SQLAlchemy).
#    - All SQLAlchemy models inheriting from this `Base`.
#    - All models being imported into Python's memory space at the time this line is run
#      (e.g., via `app.models/__init__.py` importing all model files).
#
# The `Base` for models was defined in `app.models.base_model.py`.
# The `ChatMessage` model was defined in `app.models.chat_model.py`.
# The `User` model was defined in `app.models.user_model.py`.
# `app.models.__init__.py` was updated to import `BaseModel`, `User`, and `ChatMessage`.
# So, `Base.metadata` should contain these models.
# The `engine` is imported from `app.database.session`.
# This setup should correctly create the tables if they don't exist when the app starts.I have now completed all the steps for the subtask.

1.  **Review `main.py` Structure:**
    *   The file `chat-microservice/app/main.py` was initially empty.

2.  **Import Socket.IO Application and Controllers:**
    *   In `chat-microservice/app/main.py`:
        *   Imported `socket_app` from `app.services.chat_service`.
        *   Imported `app.api.controllers` to ensure event handlers in `chat_controller.py` are registered upon application startup.

3.  **Mount Socket.IO Application:**
    *   A FastAPI application instance was initialized: `app = FastAPI(...)`.
    *   The `socket_app` was mounted to the FastAPI application using `app.mount("/ws", socket_app)`.

4.  **Ensure Controller Event Handlers are Registered:**
    *   This is handled by importing `app.api.controllers`, which in turn should load `chat_controller.py` (due to its `__init__.py`) where the `@sio.event` and `@sio.on` decorators register the handlers with the `sio` instance (which is shared as it's imported from `app.services.chat_service`).

5.  **Database Initialization:**
    *   Imported `Base` from `app.models.base_model` and `engine` from `app.database.session`.
    *   Added `Base.metadata.create_all(bind=engine)` to create database tables based on SQLAlchemy models. This relies on all models (like `ChatMessage` and `User`) inheriting from this `Base` and being imported, which was handled in previous subtasks by updating `app.models.__init__.py`.
    *   Added basic print statements for confirmation and error handling around table creation.
    *   Included a root GET endpoint `/` for basic confirmation that the HTTP server is running.
    *   Added comments regarding CORS middleware and API routers as examples for future expansion.

The `main.py` file now initializes the FastAPI application, sets up database tables (if they don't exist), and correctly mounts the Socket.IO application, ensuring that its event handlers defined in the controller layer are registered.
