from fastapi import FastAPI, status, HTTPException, Depends
from database import engine, SessionLocal, Base, get_db
from sqlalchemy.orm import Session
from typing import Annotated
import models
from routers import auth, tasks
from routers.auth import get_current_user
import schemas

app = FastAPI()
app.include_router(auth.router)
app.include_router(tasks.router)

models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# TODO:
# - Implement filtering and sorting
