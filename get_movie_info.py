from typing import Optional, Dict, Any, List

import requests
from requests.exceptions import RequestException

from config import settings

class TMDBClient:
    GENERS_DICT = {
        "genres": [
            {"id": 28, "name": "Action"},
            {"id": 12, "name": "Abenteuer"},
            {"id": 16, "name": "Animation"},
            {"id": 35, "name": "Komödie"},
            {"id": 80, "name": "Krimi"},
            {"id": 99, "name": "Dokumentarfilm"},
            {"id": 18, "name": "Drama"},
            {"id": 10751, "name": "Familie"},
            {"id": 14, "name": "Fantasy"},
            {"id": 36, "name": "Historie"},
            {"id": 27, "name": "Horror"},
            {"id": 10402, "name": "Musik"},
            {"id": 9648, "name": "Mystery"},
            {"id": 10749, "name": "Liebesfilm"},
            {"id": 878, "name": "Science Fiction"},
            {"id": 10770, "name": "TV-Film"},
            {"id": 53, "name": "Thriller"},
            {"id": 10752, "name": "Kriegsfilm"},
            {"id": 37, "name": "Western"}
        ]
    }

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self, api_key: str = None):
        self.__api_key = api_key
        if not self.__api_key:
            raise ValueError("API Key is missing! Set TMDB_API_KEY environment variable.")
        self.session = requests.Session()
        self.session.params = {'api_key': self.__api_key}

    def get_movies(
        self,
        name: Optional[str] = None,
        year: Optional[int] = None,
        genre_ids: Optional[List[int]] = None,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        Отримує фільми з TMDB.
        - Якщо вказано name – виконує пошук за назвою.
        - Інакше – використовує discover з фільтрами year та/або genre_ids.
        """
        if name:
            endpoint = f"{self.BASE_URL}/search/movie"
            params = {'query': name, 'year': year}
        else:
            endpoint = f"{self.BASE_URL}/discover/movie"
            params = {
                'sort_by': 'popularity.desc',
                'primary_release_year': year,
                'with_genres': ','.join(str(g) for g in genre_ids) if genre_ids else None
            }

        params['page'] = page
        params = {k: v for k, v in params.items() if v is not None}

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            for movie in data.get("results", []):
                poster = movie.get("poster_path")
                movie["poster_url"] = (
                    f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                )
                movie_genres = movie.get('genre_ids', [])
                movie['genres_str'] = self.convert_gener_id_to_gener_name(movie_genres)
            return data

        except RequestException as e:
            print(f"Помилка при запиті до TMDB: {e}")
            return {"error": str(e), "results": []}

    @classmethod
    def convert_gener_id_to_gener_name(cls, genre_ids: list[int]) -> str | None:
        result = []
        for genre in cls.GENERS_DICT["genres"]:
            if genre['id'] in genre_ids:
                result.append(genre['name'])
        if result:
            return result
        return None

client = TMDBClient(api_key=settings.tmdb_api_key.get_secret_value())
