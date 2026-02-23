from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from services.user_service import UserService, FriendshipService
from auth import CurrentUser, auth_service

from database import get_db
from schemas import Token, UserCreate, UserPublic

router = APIRouter()

# service dependency
async def get_user_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return UserService(db)

async def get_friend_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return FriendshipService(db)



# ---------------- registration ----------------

@router.post("/registration", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    return await service.register(user)



# ---------------- login ----------------

@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: UserService = Depends(get_user_service)):
    user = await service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return Token(access_token=auth_service.create_access_token(data={"sub": str(user.id)}), token_type="bearer")



# ---------------- get_current_user ----------------

@router.get("/me", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def get_current_user(current_user: CurrentUser):
    return current_user



# ---------------- get_user ----------------

@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    return await service.get_by_id(user_id)



# ---------------- delete_user ----------------

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, current_user: CurrentUser, service: UserService = Depends(get_user_service)):
    await service.delete_user(user_id, current_user.id)



# ---------------- send_friend_request ----------------

@router.post("/friends/request/{friend_id}", status_code=status.HTTP_201_CREATED)
async def send_friend_request(friend_id: int, current_user: CurrentUser, service: FriendshipService = Depends(get_friend_service)):
    return await service.send_request(current_user.id, friend_id)



# ---------------- accept_friend_request ----------------

@router.post("/friends/accept/{sender_id}")
async def accept_friend_request(sender_id: int, current_user: CurrentUser, service: FriendshipService = Depends(get_friend_service)):
    return await service.accept_request(current_user.id, sender_id)



# ---------------- get_my_friends ----------------

@router.get("/friends/my", response_model=list[UserPublic])
async def get_my_friends(current_user: CurrentUser, service: FriendshipService = Depends(get_friend_service)):
    return await service.get_friends(current_user.id)



# ---------------- get_incoming_requests ----------------

@router.get("/friends/requests/incoming", response_model=list[UserPublic])
async def get_incoming_requests(current_user: CurrentUser, service: FriendshipService = Depends(get_friend_service)):
    return await service.get_incoming(current_user.id)



# ---------------- remove_friendship ----------------

@router.delete("/friends/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friendship(user_id: int, current_user: CurrentUser, service: FriendshipService = Depends(get_friend_service)):
    await service.remove_friendship(current_user.id, user_id)
