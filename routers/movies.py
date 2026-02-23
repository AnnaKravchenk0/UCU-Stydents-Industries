from typing import Annotated, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth import CurrentUser
from database import get_db
from services.movie_service import MovieService
from schemas import MoviePublic

router = APIRouter()

DB = Annotated[AsyncSession, Depends(get_db)]


# GET /movies/
# choose.html завантажує список фільмів з TMDB. Токен не потрібен.
# Параметри опціональні: ?name=Matrix&year=1999&page=2
@router.get("/")
async def get_movies(
    name: Optional[str] = None,
    year: Optional[int] = None,
    page: int = 1,
    db: DB = None,
):
    service = MovieService(db)
    return await service.get_all_movies(name=name, year=year, page=page)


# POST /movies/like-movie
# choose.html — кнопка ❤️. Потрібен токен.
# Тіло запиту: { "id": 603, "poster_path": "/abc.jpg", "movie_name": "The Matrix" }
@router.post("/like-movie")
async def like_movie(movie_data: MoviePublic, db: DB, current_user: CurrentUser):
    service = MovieService(db)
    return await service.like_movie(movie_data, current_user)


# GET /movies/common/{friend_id}
# Спільні фільми з другом. Потрібен токен.
# СТОЇТЬ ВИЩЕ /{user_id}/liked — інакше "common" трактується як user_id
@router.get("/common/{friend_id}")
async def get_common_movies(friend_id: int, db: DB, current_user: CurrentUser):
    service = MovieService(db)
    return await service.get_common_movies(current_user, friend_id)


# GET /movies/{user_id}/liked
# my_films.html і profile.html — вподобані фільми юзера. Токен не потрібен.
@router.get("/{user_id}/liked")
async def get_liked_movies(user_id: int, db: DB):
    service = MovieService(db)
    return await service.get_user_liked_movies(user_id)
