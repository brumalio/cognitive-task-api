from fastapi import FastAPI
from database import engine
from models import Base
from routers import auth, tasks
import os

app = FastAPI()

app.include_router(auth.router)
app.include_router(tasks.router)

ENV = os.getenv("ENV", "development")

if os.getenv("ENV") == "development":
    Base.metadata.create_all(bind=engine)
