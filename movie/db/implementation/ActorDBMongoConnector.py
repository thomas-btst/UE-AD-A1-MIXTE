import os

from dotenv import load_dotenv

from .ActorDBJsonConnector import ActorDBJsonConnector
from ..ActorDBConnector import ActorDBConnector, Actor
from pymongo import MongoClient

load_dotenv()

def actor_model_to_actor(actor_model: Actor | None) -> Actor | None:
    if actor_model is None:
        return None
    del actor_model["_id"]
    return actor_model

class ActorDBMongoConnector(ActorDBConnector):
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["mixte"]
        self.collection = db["actors"]

        self.collection.insert_many(ActorDBJsonConnector().actors)

    def find_by_id_or_none(self, _id: str) -> Actor | None:
        return actor_model_to_actor(self.collection.find_one({"id": _id}))

    def find_all_by_movie_id(self, movie_id: str) -> list[Actor]:
        actors = self.collection.find({"movies": movie_id})
        return list(map(lambda actor: actor_model_to_actor(actor), actors))

    def create(self, actor: Actor):
        self.collection.insert_one(actor)

    def update_firstname(self, _id: str, firstname: str) -> Actor | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"firstname": firstname}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_lastname(self, _id: str, lastname: str) -> Actor | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"lastname": lastname}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_birthyear(self, _id: str, birthyear: int) -> Actor | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"birthyear": birthyear}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_movies(self, _id: str, movies: list[str]) -> Actor | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"movies": movies}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def delete(self, _id: str):
        self.collection.delete_one({"id": _id})

