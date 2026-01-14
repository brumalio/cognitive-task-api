from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status
from database import SessionFactory, get_db
from models import Users, Tasks
from schemas import CreateUserRequest, Token, TaskBase, TaskCreate, TaskRead, TaskUpdate
from routers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/tasks',
    tags=['tasks']
)

# --- Dependencies ---

user_dependency = Annotated[Users, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

# --- Tasks Routes ---


@router.post("", status_code=status.HTTP_201_CREATED)
def create_task(user: user_dependency, db: db_dependency, task_create: TaskCreate):

    task_model = Tasks(
        title=task_create.title,
        description=task_create.description,
        cognitive_load=task_create.cognitive_load,
        priority=task_create.priority,
        state=task_create.state,
        is_fragmentable=task_create.is_fragmentable,
        user_id=user.user_id
    )

    try:
        db.add(task_model)
        db.commit()
        db.refresh(task_model)
        return task_create
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError while creating task", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task with this title already exists."
        )


@router.get("", status_code=status.HTTP_200_OK, response_model=list[TaskRead])
def read_all_tasks(user: user_dependency, db: db_dependency):

    tasks = db.query(Tasks).filter(Tasks.user_id == user.user_id).order_by(
        Tasks.priority.desc()).all()

    return tasks


@router.get("/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskRead)
def read_task(user: user_dependency, db: db_dependency, task_id: int):

    task_model = db.query(Tasks).filter(Tasks.task_id == task_id)\
        .filter(Tasks.user_id == user.user_id).first()

    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    return task_model


@router.patch("/{task_id}", status_code=status.HTTP_200_OK, response_model=TaskUpdate,
              response_model_exclude_unset=True)
def update_task(user: user_dependency, db: db_dependency, task_id: int, task_update: TaskUpdate):
    task_model = db.query(Tasks).filter(
        Tasks.task_id == task_id, Tasks.user_id == user.id).first()

    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task_model, field, value)

    try:
        db.add()
        db.commit()
        db.refresh(task_model)
        return task_model
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError while updating task", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Incorrect data sent."
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(user: user_dependency, db: db_dependency, task_id: int):
    task_model = db.query(Tasks).filter(Tasks.task_id == task_id).first()

    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found.")

    try:
        db.delete(task_model)
        db.commit()
        return None
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError while deleting task", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The request is invalid."
        )
