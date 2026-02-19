from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select, or_, and_

from sqlalchemy.ext.asyncio import AsyncSession

import models

from auth import (
    CurrentUser,
    create_access_token,
    hash_password,
    verify_password,
)

from database import get_db
from schemas import Token, UserCreate, UserPublic



router = APIRouter()



# ---------------- registration ----------------

@router.post(
    "/registration",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.username == user.username),
    )

    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )

    new_user = models.User(
        username = user.username,
        password_hash = hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user



# ---------------- login ----------------

@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.username) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token = create_access_token(
        data={"sub": str(user.id)},
    )
    return Token(access_token=access_token, token_type="bearer")



# ---------------- get_current_user ----------------

@router.get("/me", response_model=UserPublic)
async def get_current_user(current_user: CurrentUser):
    return current_user



# ---------------- get_user ----------------

@router.get(
    "/{user_id}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def get_user(user_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id),
    )

    user = result.scalars().first()
    if user:
        return user

    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id doesn't exists"
        )



# ---------------- delete_user ----------------

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user",
        )

    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()



# ---------------- send_friend_request ----------------

@router.post("/friends/request/{friend_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    friend_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    if current_user.id == friend_id:
        raise HTTPException(status_code=400, detail="You cannot add yourself as a friend")

    # Перевіряємо, чи існує вже будь-який зв'язок між цими користувачами
    result = await db.execute(
        select(models.Friendship).where(
            or_(
                and_(models.Friendship.user_id == current_user.id, models.Friendship.friend_id == friend_id),
                and_(models.Friendship.user_id == friend_id, models.Friendship.friend_id == current_user.id)
            )
        )
    )
    existing = result.scalars().first()

    if existing:
        status_msg = "already friends" if existing.is_accepted else "request already pending"
        raise HTTPException(status_code=400, detail=f"Relationship exists: {status_msg}")

    # Створюємо новий запит (is_accepted за замовчуванням False)
    new_request = models.Friendship(
        user_id=current_user.id,
        friend_id=friend_id
    )
    db.add(new_request)
    await db.commit()
    return {"message": "Friend request sent"}



# ---------------- accept_friend_request ----------------

@router.post("/friends/accept/{sender_id}")
async def accept_friend_request(
    sender_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Шукаємо запит, де ми є отримувачем (friend_id)
    result = await db.execute(
        select(models.Friendship).where(
            and_(
                models.Friendship.user_id == sender_id,
                models.Friendship.friend_id == current_user.id,
                models.Friendship.is_accepted == False
            )
        )
    )
    request = result.scalars().first()

    if not request:
        raise HTTPException(status_code=404, detail="Pending request not found")

    request.is_accepted = True
    await db.commit()
    return {"message": "Friend request accepted"}



# ---------------- get_my_friends ----------------

@router.get("/friends/my", response_model=list[UserPublic])
async def get_my_friends(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Friendship).where(
            and_(
                models.Friendship.is_accepted == True,
                or_(
                    models.Friendship.user_id == current_user.id,
                    models.Friendship.friend_id == current_user.id
                )
            )
        )
    )
    friendships = result.scalars().all()

    friend_ids = [
        friendship.friend_id if friendship.user_id == current_user.id else friendship.user_id for friendship in friendships
    ]

    if not friend_ids:
        return []

    users_result = await db.execute(
        select(models.User).where(models.User.id.in_(friend_ids))
    )
    return users_result.scalars().all()



# ---------------- get_incoming_requests ----------------

@router.get("/friends/requests/incoming", response_model=list[UserPublic])
async def get_incoming_requests(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Вибираємо користувачів, які надіслали нам запит
    result = await db.execute(
        select(models.User)
        .join(models.Friendship, models.User.id == models.Friendship.user_id)
        .where(
            and_(
                models.Friendship.friend_id == current_user.id,
                models.Friendship.is_accepted == False
            )
        )
    )
    return result.scalars().all()



# ---------------- remove_friendship ----------------

# Відхилити запит або видалити з друзів
@router.delete("/friends/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friendship(
    user_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(models.Friendship).where(
            or_(
                and_(models.Friendship.user_id == current_user.id, models.Friendship.friend_id == user_id),
                and_(models.Friendship.user_id == user_id, models.Friendship.friend_id == current_user.id)
            )
        )
    )
    friendship = result.scalars().first()

    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship or request not found")

    await db.delete(friendship)
    await db.commit()
    return None
