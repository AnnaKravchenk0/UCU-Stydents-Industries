from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException, status

from typing import Optional, Dict, Any
from requests.exceptions import RequestException
from sqlalchemy.ext.asyncio import AsyncSession


from get_movie_info import client
from database import get_db
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import models

from schemas import MoviePublic

from auth import CurrentUser

router = APIRouter()

@router.get("/")
def get_movies(
    name: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1, le=500)
):
    return client.get_movies(name=name, year=year, page=page)

@router.get("/like-movie")
async def like_movie(
    movie_data: MoviePublic,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser
):
    result = await db.execute(select(models.Movie).where(models.Movie.id == movie_data.id))
    movie = result.scalars().first()

    if not movie:
        movie = models.Movie(id=movie_data.id, poster_path=movie_data.poster_path, movie_name=movie_data.movie_name)
        db.add(movie)
        await db.flush()

    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.liked_movies))
        .where(models.User.id == current_user.id)
    )
    user = result.scalars().first()

    if movie not in user.liked_movies:
        user.liked_movies.append(movie)
        await db.commit()
        return {"message": "Movie added to favorites"}
    return {"message": "Movie already in favorites"}

@router.get("/{user_id}/liked", response_model=list[MoviePublic])
async def get_liked_movies(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.refresh(user, ["liked_movies"])

    return user.liked_movies

@router.get("/common/{friend_id}", response_model=list[MoviePublic])
async def get_common_movies(
    friend_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # Завантажуємо фільми поточного користувача
    await db.refresh(current_user, ["liked_movies"])
    my_movies_ids = {movie.id for movie in current_user.liked_movies}

    # Шукаємо друга
    result = await db.execute(select(models.User).where(models.User.id == friend_id))
    friend = result.scalars().first()

    if not friend:
        raise HTTPException(status_code=404, detail="Friend not found")

    # Завантажуємо фільми друга
    await db.refresh(friend, ["liked_movies"])
    friend_movies = friend.liked_movies

    # Знаходимо спільні фільми
    common = [movie for movie in friend_movies if movie.id in my_movies_ids]

    return common
