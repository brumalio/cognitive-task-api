from fastapi import FastAPI, status, HTTPException, Depends
from database import engine, SessionLocal, Base, get_db
from sqlalchemy.orm import Session
from typing import Annotated
import models
from routers import auth
import schemas

app = FastAPI()
app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]

# TODO:
# - Implement CRUD endpoints
# - Implement filtering and sorting
