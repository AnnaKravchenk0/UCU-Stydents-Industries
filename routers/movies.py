import requests
from fastapi import APIRouter, Query

from typing import Optional, Dict, Any
from requests.exceptions import RequestException

from get_movie_info import client

router = APIRouter()

@router.get("/")
def get_movies(
     name: Optional[str] = Query(None),
     year: Optional[int] = Query(None),
     page: int = Query(1, ge=1, le=500)
):
     return client.get_movies(name=name, year=year, page=page)
