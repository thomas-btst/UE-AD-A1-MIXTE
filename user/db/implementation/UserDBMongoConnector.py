from dotenv import load_dotenv

from .UserDBJsonConnector import UserDBJsonConnector
from ..UserDBConnector import UserDBConnector, User
from pymongo import MongoClient
import os

load_dotenv()

def user_model_to_user(user_model: User | None) -> User | None:
    if user_model is None:
        return None
    del user_model["_id"]
    return user_model

class UserDBMongoConnector(UserDBConnector):
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["mixte"]
        self.collection = db["users"]

        if self.collection.count_documents({}) == 0:
            self.collection.insert_many(UserDBJsonConnector().users)

    def find_by_id_or_none(self, _id: str) -> User | None:
        return user_model_to_user(self.collection.find_one({"id": _id}))

    def find_all(self) -> list[User]:
        users = self.collection.find()
        return list(map(lambda user: user_model_to_user(user), users))

    def create(self, user: User):
        self.collection.insert_one(user)
        user_model_to_user(user)

    def update_last_active(self, _id: str, last_active: int) -> User | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"last_active": last_active}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def update_name(self, _id: str, name: str) -> User | None:
        result = self.collection.update_one(
            {"id": _id},
            {"$set": {"name": name}}
        )
        if result.modified_count > 0:
            return self.find_by_id_or_none(_id)
        return None

    def delete(self, _id):
        self.collection.delete_one({"id": _id})
