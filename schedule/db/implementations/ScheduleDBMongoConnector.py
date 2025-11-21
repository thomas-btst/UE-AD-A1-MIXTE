import os

from dotenv import load_dotenv
from pymongo import MongoClient
from .ScheduleDBJsonConnector import ScheduleDBJsonConnector
from ..ScheduleDBConnector import ScheduleDBConnector, Schedule

load_dotenv()

def schedule_model_to_schedule(schedule_model: Schedule | None) -> Schedule | None:
    if schedule_model is None:
        return None
    del schedule_model["_id"]
    return schedule_model

class ScheduleDBMongoConnector(ScheduleDBConnector):
    def __init__(self):
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client["mixte"]
        self.collection = db["schedules"]

        if self.collection.count_documents({}) == 0:
            self.collection.insert_many(ScheduleDBJsonConnector().schedules)

    def find_by_date_or_none(self, date: int) -> Schedule | None:
        return schedule_model_to_schedule(self.collection.find_one({"date": date}))

    def find_all_by_movie_id(self, movie_id: str) -> list[Schedule]:
        schedules = self.collection.find({"movies": movie_id})
        return list(map(lambda schedule: schedule_model_to_schedule(schedule), schedules))

    def find_all(self) -> list[Schedule]:
        schedules = self.collection.find()
        return list(map(lambda schedule: schedule_model_to_schedule(schedule), schedules))

    def create(self, schedule: Schedule):
        self.collection.insert_one(schedule)

    def update(self, schedule: Schedule):
        self.collection.update_one(
            {"date": schedule["date"]},
            {"$set": schedule}
        )

    def delete(self, date: int):
        self.collection.delete_one({"date": date})