# from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# endpoint get info

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)

class UserCreate(UserBase):
    password: str = Field(min_length=8)


# endpoint give info

class Token(BaseModel):
    access_token: str
    token_type: str

class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
