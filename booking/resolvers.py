import json
import requests
import grpc
import schedule_pb2
import schedule_pb2_grpc

db_path = '{}/data/bookings.json'.format(".")
db_root_key = 'bookings'

def load():
    with open(db_path, "r") as jsf:
        return json.load(jsf)[db_root_key]

def write(bookings):
    with open(db_path, 'w') as f:
        full = {}
        full[db_root_key]=bookings
        json.dump(full, f)

def find_booking_by_userid_or_none(bookings, userid: str):
    return next(filter(lambda _booking: _booking["userid"] == userid, bookings), None)

def find_date_in_booking_or_none(booking, date: str):
    return next(filter(lambda _date: _date["date"] == date, booking["dates"]), None)

def find_movie_in_date_or_none(date, movie: str):
    return next(filter(lambda _movie: _movie == movie, date["movies"]), None)

def requests_user_api_get(url: str):
    return requests.get(f"http://user:3004/{url}")

# Resolvers

def booking_with_userid(_, __, _userid: str):
    bookings = load()
    return find_booking_by_userid_or_none(bookings, _userid)

def bookings_with_admin_id(_, __, _admin_id: str):
    if requests_user_api_get(f"/users/{_admin_id}/admin").status_code != 200 :
        return None
    return load()

def date_with_userid_and_date(_, __, _userid: str, _date: str):
    bookings = load()
    booking = find_booking_by_userid_or_none(bookings, _userid)
    if booking:
        return find_date_in_booking_or_none(booking, _date)
    return None

def add_booking(_, __, _userid: str, _date: str, _movie_id: str):
    bookings = load()

    with grpc.insecure_channel('schedule:3002') as channel:
        stub = schedule_pb2_grpc.ScheduleServiceStub(channel)
        schedule = stub.GetScheduleByDate(schedule_pb2.Date(date=int(_date)))
        if _movie_id not in list(schedule.movies):
            raise Exception(f"Schedule with movie ID '{_movie_id}' and date '{_date}' does not exists")

    if requests_user_api_get(f"/users/{_userid}").status_code != 200:
        return None

    booking = find_booking_by_userid_or_none(bookings, _userid)
    if booking is None:
        booking = {"userid": _userid, "dates": []}
        bookings.append(booking)

    date = find_date_in_booking_or_none(booking, _date)
    if date is None:
        date = {"date": _date, "movies": []}
        booking["dates"].append(date)

    if find_movie_in_date_or_none(date, _movie_id):
        return None
    date["movies"].append(_movie_id)

    write(bookings)
    return booking

def delete_booking(_, __, _userid: str, _date: str, _movie_id: str):
    bookings = load()

    booking = find_booking_by_userid_or_none(bookings, _userid)
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

    if not booking["dates"]:
        bookings.remove(booking)

    write(bookings)
    return booking