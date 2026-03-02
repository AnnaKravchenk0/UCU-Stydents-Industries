from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser
from database import get_db
from services.movie_service import MovieService
from schemas import MoviePublic, MovieInDB

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/")
async def get_movies(
    name: Optional[str] = None,
    year: Optional[int] = None,
    genre: Optional[str] = Query(None, description="Comma-separated genre IDs, e.g. '28,12'"),
    page: int = 1,
    db: DB = None,
):
    genre_ids = [int(g) for g in genre.split(',')] if genre else None
    service = MovieService(db)
    return await service.get_all_movies(name=name, year=year, genre_ids=genre_ids, page=page)


@router.post("/like-movie")
async def like_movie(movie_data: MoviePublic, db: DB, current_user: CurrentUser):
    service = MovieService(db)
    return await service.like_movie(movie_data, current_user)


@router.get("/common/{friend_id}", response_model=list[MovieInDB])
async def get_common_movies(friend_id: int, db: DB, current_user: CurrentUser):
    service = MovieService(db)
    return await service.get_common_movies(current_user, friend_id)


@router.get("/{user_id}/liked", response_model=list[MovieInDB])
async def get_liked_movies(user_id: int, db: DB):
    service = MovieService(db)
    return await service.get_user_liked_movies(user_id)
