from fastapi import FastAPI
from api.controllers import auth_controller, user_controller
from database.session import Base, engine

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

app.include_router(auth_controller.router, prefix="/auth")
app.include_router(user_controller.router, prefix="/auth/user")
@app.get("/")
def root():
    return {"message": "Welcome to the API"}
