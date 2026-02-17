from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

user_friends = Table(
    'user_friends',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True)
)

likes = Table(
    'likes',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True)
)

dislikes = Table(
    'dislikes',
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
    disliked_movies: Mapped[list[Movie]] = relationship(
        secondary=dislikes,
        back_populates='disliked_by'
    )

    friends_with: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_friends,
        primaryjoin=id == user_friends.columns.user_id,
        secondaryjoin=id == user_friends.columns.friend_id,
        backref="friend_of",
    )

class Movie(Base):
    __tablename__ = 'movies'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    liked_by: Mapped[list[User]] = relationship(
        secondary=likes,
        back_populates='liked_movies'
    )
    disliked_by: Mapped[list[User]] = relationship(
        secondary=dislikes,
        back_populates='disliked_movies'
    )
