from typing import Annotated

from fastapi import APIRouter, Query, Depends

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from services.movie_service import MovieService

from schemas import MoviePublic
from auth import CurrentUser


router = APIRouter()

# Хелпер для отримання сервісу фільмів
async def get_movie_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return MovieService(db)

@router.get("/")
async def get_movies(
    name: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1, le=500),
    movie_service: MovieService = Depends(get_movie_service)
):
    return await movie_service.get_all_movies(name=name, year=year, page=page)

@router.post("/like-movie")
async def like_movie(
    movie_data: MoviePublic,
    current_user: CurrentUser,
    movie_service: MovieService = Depends(get_movie_service)
):
    return await movie_service.like_movie(movie_data=movie_data, current_user=current_user)

@router.get("/{user_id}/liked", response_model=list[MoviePublic])
async def get_liked_movies(
    user_id: int,
    movie_service: MovieService = Depends(get_movie_service)
):
    return await movie_service.get_user_liked_movies(user_id=user_id)

@router.get("/common/{friend_id}", response_model=list[MoviePublic])
async def get_common_movies(
    friend_id: int,
    current_user: CurrentUser,
    movie_service: MovieService = Depends(get_movie_service)
):
    return await movie_service.get_common_movies(current_user=current_user, friend_id=friend_id)
