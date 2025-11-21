from dotenv import load_dotenv
import os

from .MovieDBJsonConnector import MovieDBJsonConnector
from ..MovieDBConnector import MovieDBConnector, Movie
from pymongo import MongoClient


load_dotenv()

def movie_model_to_movie(movie_model: Movie | None) -> Movie | None:
    if movie_model is None:
        return None
    del movie_model["_id"]
    return movie_model

class MovieDBMongoConnector(MovieDBConnector):
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["mixte"]
        self.collection = db["movies"]

        self.collection.insert_many(MovieDBJsonConnector().movies)

    def find_by_id_or_none(self, _id: str) -> Movie | None:
        return movie_model_to_movie(self.collection.find_one({"id": _id}))

    def find_all(self) -> list[Movie]:
        movies = self.collection.find()
        return list(map(lambda movie: movie_model_to_movie(movie), movies))

    def find_all_by_id(self, _ids: list[str]) -> list[Movie]:
        movies = self.collection.find({"id": {"$in": _ids}})
        return list(map(lambda movie: movie_model_to_movie(movie), movies))

    def create(self, movie: Movie):
        self.collection.insert_one(movie)

    def update_title(self, _id: str, title: str) -> Movie | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"title": title}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_rating(self, _id: str, rating: float) -> Movie | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"rating": rating}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_director(self, _id, director: str) -> Movie | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"director": director}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def delete(self, _id):
        self.collection.delete_one({"id": _id})
