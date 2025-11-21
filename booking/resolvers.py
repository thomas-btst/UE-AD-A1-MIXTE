import json
import requests
import grpc
import schedule_pb2
import schedule_pb2_grpc
import sys
import os

from dotenv import load_dotenv

from db.implementations.BookingDBMongoConnector import BookingDBMongoConnector
from db.implementations.BookingDBJsonConnector import BookingDBJsonConnector
from db.BookingDBConnector import BookingDBConnector

load_dotenv()

USER_API = os.getenv("USER_API") or "localhost:3004"
SCHEDULE_API = os.getenv("SCHEDULE_API") or "localhost:3002"

# Database Connector
db: BookingDBConnector

match (os.getenv("DB_TYPE")):
    case "json":
        db = BookingDBJsonConnector()
    case "mongo":
        db = BookingDBMongoConnector()
    case _:
        print("DB_TYPE env variable must be 'json' or 'mongo'")
        sys.exit(1)

# Helpers

def find_date_in_booking_or_none(booking, date: str):
    return next(filter(lambda _date: _date["date"] == date, booking["dates"]), None)

def find_movie_in_date_or_none(date, movie: str):
    return next(filter(lambda _movie: _movie == movie, date["movies"]), None)

def requests_user_api_get(url: str):
    return requests.get(f"http://{USER_API}/{url}")

# Resolvers

def booking_with_userid(_, __, _userid: str):
    return db.find_by_userid_or_none(_userid)

def bookings_with_admin_id(_, __, _admin_id: str):
    if requests_user_api_get(f"/users/{_admin_id}/admin").status_code != 200 :
        return None
    return db.find_all()

def date_with_userid_and_date(_, __, _userid: str, _date: str):
    booking = db.find_by_userid_or_none(_userid)
    if booking:
        return find_date_in_booking_or_none(booking, _date)
    return None

def add_booking(_, __, _userid: str, _date: str, _movie_id: str):
    with grpc.insecure_channel(SCHEDULE_API) as channel:
        stub = schedule_pb2_grpc.ScheduleServiceStub(channel)
        schedule = stub.GetScheduleByDate(schedule_pb2.Date(date=int(_date)))
        if _movie_id not in list(schedule.movies):
            raise Exception(f"Schedule with movie ID '{_movie_id}' and date '{_date}' does not exists")

    if requests_user_api_get(f"/users/{_userid}").status_code != 200:
        return None

    booking = db.find_by_userid_or_none(_userid)
    if booking is None:
        booking = {"userid": _userid, "dates": []}
        db.create(booking)

    date = find_date_in_booking_or_none(booking, _date)
    if date is None:
        date = {"date": _date, "movies": []}
        booking["dates"].append(date)

    if find_movie_in_date_or_none(date, _movie_id):
        return None
    date["movies"].append(_movie_id)

    db.update(booking)
    return booking

def delete_booking(_, __, _userid: str, _date: str, _movie_id: str):
    booking = db.find_by_userid_or_none(_userid)
    if booking is None:
        return None

    date = find_date_in_booking_or_none(booking, _date)
    if date is None:
        return None

    if find_movie_in_date_or_none(date, _movie_id) is None:
        return None

    date["movies"].remove(_movie_id)

    if not date["movies"]:
        booking["dates"].remove(date)

    if booking["dates"]:
        db.update(booking)
    else:
        db.delete(booking["userid"])

    return booking