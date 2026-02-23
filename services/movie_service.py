from fastapi import HTTPException, status

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from get_movie_info import client
import models

from schemas import MoviePublic

class MovieService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_movies(self, name: Optional[str], year: Optional[int], page: int):
        # Викликаємо метод нашого клієнта
        return client.get_movies(name=name, year=year, page=page)

    async def like_movie(self, movie_data: MoviePublic, current_user: models.User):
        # 1. Шукаємо фільм у нашій базі або створюємо, якщо його немає
        result = await self.db.execute(select(models.Movie).where(models.Movie.id == movie_data.id))
        movie = result.scalars().first()

        if not movie:
            movie = models.Movie(
                id=movie_data.id,
                poster_path=movie_data.poster_path,
                movie_name=movie_data.movie_name
            )
            self.db.add(movie)
            await self.db.flush()

        # 2. Завантажуємо список вподобань користувача
        result = await self.db.execute(
            select(models.User)
            .options(selectinload(models.User.liked_movies))
            .where(models.User.id == current_user.id)
        )
        user = result.scalars().first()

        # 3. Додаємо фільм, якщо його ще немає в списку
        if movie not in user.liked_movies:
            user.liked_movies.append(movie)
            await self.db.commit()
            return {"message": "Movie added to favorites"}

        return {"message": "Movie already in favorites"}

    async def get_user_liked_movies(self, user_id: int):
        result = await self.db.execute(select(models.User).where(models.User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await self.db.refresh(user, ["liked_movies"])
        return user.liked_movies

    async def get_common_movies(self, current_user: models.User, friend_id: int):
        # Завантажуємо фільми поточного користувача
        await self.db.refresh(current_user, ["liked_movies"])
        my_movies_ids = {movie.id for movie in current_user.liked_movies}

        # Шукаємо друга
        result = await self.db.execute(select(models.User).where(models.User.id == friend_id))
        friend = result.scalars().first()

        if not friend:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friend not found")

        # Завантажуємо фільми друга
        await self.db.refresh(friend, ["liked_movies"])
        friend_movies = friend.liked_movies

        # Знаходимо спільні
        common_movies = [movie for movie in friend_movies if movie.id in my_movies_ids]
        return common_movies
