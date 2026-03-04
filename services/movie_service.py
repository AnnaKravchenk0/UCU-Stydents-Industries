from fastapi import HTTPException, status
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from get_movie_info import client
import models
from schemas import MoviePublic


class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_movies(
        self,
        name: Optional[str],
        year: Optional[int],
        genre_ids: Optional[List[int]],
        page: int
    ):
        return client.get_movies(name=name, year=year, genre_ids=genre_ids, page=page)

    async def like_movie(self, movie_data: MoviePublic, current_user: models.User):
        # (без змін)
        result = await self.db.execute(
            select(models.Movie).where(models.Movie.id == movie_data.id)
        )
        movie = result.scalars().first()
        if not movie:
            movie = models.Movie(
                id=movie_data.id,
                movie_name=movie_data.movie_name,
                poster_path=movie_data.poster_path,
                poster_url=movie_data.poster_url,
                overview=movie_data.overview,
                release_date=movie_data.release_date,
                vote_average=movie_data.vote_average,
            )
            self.db.add(movie)
            await self.db.flush()
        else:
            if not movie.poster_url and movie_data.poster_url:
                movie.poster_url = movie_data.poster_url
            if not movie.overview and movie_data.overview:
                movie.overview = movie_data.overview
            if not movie.release_date and movie_data.release_date:
                movie.release_date = movie_data.release_date
            if not movie.vote_average and movie_data.vote_average:
                movie.vote_average = movie_data.vote_average

        result = await self.db.execute(
            select(models.User)
            .options(selectinload(models.User.liked_movies))
            .where(models.User.id == current_user.id)
        )
        user = result.scalars().first()

        if movie not in user.liked_movies:
            user.liked_movies.append(movie)
            await self.db.commit()
            return {"message": "Movie added to favorites"}
        return {"message": "Movie already in favorites"}

    async def get_user_liked_movies(self, user_id: int):
        result = await self.db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        await self.db.refresh(user, ["liked_movies"])
        return user.liked_movies

    async def get_common_movies(self, current_user: models.User, friend_id: int):
        await self.db.refresh(current_user, ["liked_movies"])
        my_ids = {movie.id for movie in current_user.liked_movies}

        result = await self.db.execute(
            select(models.User).where(models.User.id == friend_id)
        )
        friend = result.scalars().first()
        if not friend:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Friend not found"
            )
        await self.db.refresh(friend, ["liked_movies"])

        return [m for m in friend.liked_movies if m.id in my_ids]
