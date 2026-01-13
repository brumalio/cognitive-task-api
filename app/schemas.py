from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from enum import IntEnum

# --- Enums ---


class CognitiveLoad(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class State(IntEnum):
    PENDING = 1
    ACTIVE = 2
    COMPLETED = 3
    PAUSED = 4

# --- User Schemas ---


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20,
                          description="Unique username", pattern="^[a-zA-Z0-9_]+$",)
    email: EmailStr = Field(..., example="johndoe@example.com")
    password: str = Field(..., min_length=8, max_length=72,
                          description="The password is encrypted with Bcrypt (max 72 chars)", example="MySecurePassword123"
                          )

    @field_validator('email')
    @classmethod
    def email_to_lowercase(cls, v: str) -> str:
        return v.lower()

    class Config:
        from_attributes = True  # Esto permite leer modelos de SQLAlchemy
        json_schema_extra = {
            "example": {
                "username": "brumalio_dev",
                "email": "johndoe@example.com",
                "password": "my_secret_password",
            }
        }


class Token(BaseModel):
    access_token: str = Field(
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")
    token_type: str = Field(example="bearer")

# --- Task Schemas ---


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = Field(None, min_length=3, max_length=512)
    cognitive_load: CognitiveLoad = Field(default=CognitiveLoad.LOW,
                                          description="The cognitive load of the task")
    priority: Priority = Field(default=Priority.LOW,
                               description="The priority of the task")
    state: State = Field(default=State.PENDING,
                         description="The state of the task")
    is_fragmentable: bool = Field(default=False,
                                  description="Indicates whether the task can be broken down")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = Field(None, min_length=3, max_length=512)
    cognitive_load: Optional[CognitiveLoad] = Field(
        None, description="The cognitive load of the task")
    priority: Optional[Priority] = Field(
        None, description="The priority of the task")
    state: Optional[State] = Field(None, description="The state of the task")
    is_fragmentable: Optional[bool] = Field(
        None, description="Indicates whether the task can be broken down")


class TaskRead(TaskBase):
    task_id: int = Field(..., description="Unique identifier of the task")
    user_id: int = Field(..., description="Unique identifier of the user")
    created_at: datetime = Field(..., description="Date the task was created")
    updated_at: datetime = Field(..., description="Date of last task update")

    class Config:
        from_attributes = True
