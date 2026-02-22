from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Table, Column, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# user_friends = Table(
#     'user_friends',
#     Base.metadata,
#     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
#     Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True)
# )

likes = Table(
    'likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # nickname: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)

    liked_movies: Mapped[list[Movie]] = relationship(
        secondary=likes,
        back_populates='liked_by'
    )

class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    poster_path = mapped_column(String(200), unique=False, nullable=False)
    movie_name = mapped_column(String(50), unique=False, nullable=False)
    liked_by: Mapped[list[User]] = relationship(
        secondary=likes,
        back_populates='liked_movies'
    )

class Friendship(Base):
    __tablename__ = 'user_friends'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)

    is_accepted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    friend: Mapped["User"] = relationship("User", foreign_keys=[friend_id])
