from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status
from database import SessionLocal, get_db
from models import Users, Tasks
from schemas import CreateUserRequest, Token, TaskBase, TaskCreate, TaskRead, TaskUpdate
from routers.auth import get_current_user

router = APIRouter(
    prefix='',
    tags=['tasks']
)

# --- Dependencies ---

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

# --- Tasks Routes ---


@router.post("/task", status_code=status.HTTP_201_CREATED)
async def create_task(user: user_dependency, db: db_dependency, task_create: TaskCreate):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    task_model = Tasks(
        title=task_create.title,
        description=task_create.description,
        cognitive_load=task_create.cognitive_load,
        priority=task_create.priority,
        state=task_create.state,
        is_fragmentable=task_create.is_fragmentable,
        user_id=user.get('id')
    )

    try:
        db.add(task_model)
        db.commit()
        return {"status": "Task created successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task already exists. Please change the title."
        )


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def read_all_tasks(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    tasks = db.query(Tasks).filter(Tasks.user_id == user.get(
        'id')).order_by(Tasks.priority.desc()).all()

    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user has no tasks."
        )

    return tasks


@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def read_task(user: user_dependency, db: db_dependency, task_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    task_model = db.query(Tasks).filter(Tasks.task_id == task_id)\
        .filter(Tasks.user_id == user.get('id')).first()

    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task_model
