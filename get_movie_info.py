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

    @classmethod
    def convert_gener_id_to_gener_name(cls, genre_ids: list[int]) -> list | None:
        result = []
        for genre in cls.GENERS_DICT["genres"]:
            if genre['id'] in genre_ids:
                result.append(genre['name'])
        if result:
            return result
        return None

    @classmethod
    def get_genre_id_by_name(cls, genres):
        "converts genere to genere id"
        result = []
        for genre in cls.GENERS_DICT["genres"]:
            if genre["name"] in genres:
                result.append(genre['id'])
        if result:
            return result
        return None

    def get_movies(self, name=None, year=None, genre_ids=None, page=1,):
        SAFE_LANGUAGES = {
            'en', 'uk', 'fr', 'de', 'it', 'es', 'pt', 'nl',
            'ja', 'ko', 'pl', 'cs', 'sv', 'no', 'da', 'fi',
            'hu', 'ro', 'el', 'bg', 'he', 'th'
        }

        if name:
            endpoint = f"{self.BASE_URL}/search/movie"
            params = {'query': name, 'year': year, 'include_adult': False}
        elif year or genre_ids:
            endpoint = f"{self.BASE_URL}/discover/movie"
            params = {'sort_by': 'popularity.desc', 'include_adult': False}
            if year:
                params['primary_release_year'] = year
            if genre_ids:
                params['with_genres'] = "|".join([str(g) for g in genre_ids])
        else:
            endpoint = f"{self.BASE_URL}/movie/popular"
            params = {'include_adult': False}

        params['page'] = page

        try:
            clean_params = {k: v for k, v in params.items() if v is not None}
            response = self.session.get(endpoint, params=clean_params)
            response.raise_for_status()
            data = response.json()

            data["results"] = [
                movie for movie in data.get("results", [])
                if movie.get("original_language") in SAFE_LANGUAGES
                and not movie.get("adult", False)
            ]

            for movie in data["results"]:
                poster = movie.get("poster_path")
                movie["poster_url"] = (
                    f"https://image.tmdb.org/t/p/w500{poster}" if poster else None
                )
                movie['genres_str'] = self.convert_gener_id_to_gener_name(movie['genre_ids'])

            return data

        except RequestException as e:
            print(f"Помилка при запиті до TMDB: {e}")
            return {"error": str(e), "results": []}
client = TMDBClient(api_key = settings.tmdb_api_key.get_secret_value())
