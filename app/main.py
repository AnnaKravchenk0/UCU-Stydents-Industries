from contextlib import asynccontextmanager
from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends, FastAPI, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import Base, engine, get_db

from fastapi.middleware.cors import CORSMiddleware

# Command to start backend
# >>> uvicorn main:app --reload

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на час розробки можна все
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    username: str
    password: str

@app.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.username == user.username),
    )

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    new_user = models.User(
        username=user.username,
        password_hash=user.password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.get(
    "/get_user/{username}",
    status_code=status.HTTP_200_OK,
)
async def get_user(username: str, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.username == username),
    )

    user = result.scalars().first()
    if user:
        return user

    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username doesn't exists"
        )
