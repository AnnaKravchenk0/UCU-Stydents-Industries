import requests
import json
import uvicorn
from fastapi import FastAPI, Query
from typing import Optional, Dict, Any
from requests.exceptions import RequestException
from geners import convert_gener_id_to_gener_name


class TMDBClient:

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str = None):

        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API Key is missing! Set TMDB_API_KEY environment variable.")

        self.session = requests.Session()
        self.session.params = {'api_key': self.api_key}

    def get_movies(self, name: Optional[str] = None, year: Optional[int] = None, page: int = 1) -> Dict[str, Any]:
        if name:
            endpoint = f"{self.BASE_URL}/search/movie"
            params = {'query': name, 'year': year}

        elif year:
            endpoint = f"{self.BASE_URL}/discover/movie"
            params = {
                'primary_release_year': year,
                'sort_by': 'popularity.desc'
            }

        else:
            endpoint = f"{self.BASE_URL}/movie/popular"
            params = {}

        params['page'] = page
        try:
            clean_params = {k: v for k, v in params.items() if v is not None}
            response = self.session.get(endpoint, params=clean_params)
            response.raise_for_status()

            data = response.json()

            for movie in data.get("results", []):

                poster = movie.get("poster_path")
                movie["poster_url"] = (
                    f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                )

                movie_genres= movie['genre_ids']
                movie['genres_str'] = convert_gener_id_to_gener_name(movie_genres)
            return data

        except RequestException as e:
            print(f"Помилка при запиті до TMDB: {e}")
            return {"error": str(e), "results": []}



app = FastAPI()

client = TMDBClient(api_key="acfd6dae20beb64c13392327c3a64a13")

@app.get("/movies")
def get_movies(
     name: Optional[str] = Query(None),
     year: Optional[int] = Query(None),
     page: int = Query(1, ge=1, le=500)
):
     return client.get_movies(name=name, year=year, page=page)
