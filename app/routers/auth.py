from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from starlette import status
from database import SessionFactory, get_db
from models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import bcrypt
import os
from schemas import CreateUserRequest, Token
import logging

load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# --- Configuration ---

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is not set")
ALGORITHM = "HS256"

# --- Security Helpers ---


BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    ).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# --- Dependencies ---

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/login')
db_dependency = Annotated[Session, Depends(get_db)]

# --- Auth Routes ---


@router.post("/register", status_code=status.HTTP_201_CREATED)
def create_user(db: db_dependency,
                create_user_request: CreateUserRequest):
    create_user_model = Users(
        username=create_user_request.username,
        email=create_user_request.email,
        hashed_password=hash_password(create_user_request.password),
    )

    try:
        db.add(create_user_model)
        db.commit()
        return {"status": "User created successfully."}
    except IntegrityError as e:
        db.rollback()
        logger.warning("IntegrityError during user creation", exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed."
        )


@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db,)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.")

    token = create_access_token(
        user=user,
        expires_delta=timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}

# --- Auth Functions ---


def authenticate_user(username: str, password: str, db: Session) -> Users | None:
    user = (
        db.query(Users)
        .filter(Users.username == username)
        .first()
    )

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_access_token(user: Users, expires_delta: timedelta):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.username,
        "uid": user.user_id,
        "iat": now,
        "nbf": now,
        "exp": now + expires_delta
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_bearer),
                     db: Session = Depends(get_db)) -> Users:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.',
                            headers={"WWW-Authenticate": "Bearer"})

    user_id = payload.get("uid")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(Users).filter(Users.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")

    return user
