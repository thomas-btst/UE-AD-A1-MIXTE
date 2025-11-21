from .BookingDBJsonConnector import BookingDBJsonConnector
from ..BookingDBConnector import BookingDBConnector, Booking
from pymongo import MongoClient

def booking_model_to_booking(booking_model: Booking | None) -> Booking | None:
    if booking_model is None:
        return None
    del booking_model["_id"]
    return booking_model

class BookingDBMongoConnector(BookingDBConnector):
    def __init__(self):
        client = MongoClient("mongodb://root:example@mongo:27017/")
        db = client["mixte"]
        self.collection = db["bookings"]

        self.collection.insert_many(BookingDBJsonConnector().bookings)

    def find_by_userid_or_none(self, userid: str) -> Booking | None:
        return booking_model_to_booking(self.collection.find_one({"userid": userid}))

    def find_all(self) -> list[Booking]:
        bookings = self.collection.find()
        return list(map(lambda booking: booking_model_to_booking(booking), bookings))

    def create(self, booking: Booking):
        self.collection.insert(booking)

    def update(self, booking: Booking):
        self.collection.update_one(
            {"userid": booking["userid"]},
            {"$set": booking}
        )

    def delete(self, userid: str):
        self.collection.delete_one({"userid": userid})
