from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True,
                       isolation_level="READ COMMITTED", echo=False,)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()

# NOTE: This project uses synchronous SQLAlchemy sessions.
# Async endpoints must NOT use this session factory.
