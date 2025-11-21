import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import requests
import sys

from db.ScheduleDBConnector import ScheduleDBConnector
from db.implementations.ScheduleDBJsonConnector import ScheduleDBJsonConnector
from db.implementations.ScheduleDBMongoConnector import ScheduleDBMongoConnector

db: ScheduleDBConnector

class ScheduleServicer(schedule_pb2_grpc.ScheduleServiceServicer):

    @staticmethod
    def find_dates_by_movie(movie: str):
        filtered_schedules = db.find_all_by_movie_id(movie)
        return list(map(lambda schedule: schedule["date"], filtered_schedules))

    @staticmethod
    def check_movie_exists(movie_id: str):
        response = requests.post(
            "http://movie:3001/graphql",
            json ={
                "query": f"""
                    query{{
                      movie_with_id(_id:"{movie_id}") {{
                            id
                      }}
                    }}
                """
            },
        )
        if response.status_code == 200:
            return response.json()["data"]["movie_with_id"] is not None
        return False

    @staticmethod
    def movies_to_dto(movies):
        return schedule_pb2.Movies(movies = movies)

    @staticmethod
    def schedule_to_dto(schedule):
        return schedule_pb2.Schedule(date=schedule["date"], movies=schedule["movies"])

    @staticmethod
    def empty_schedule_dto():
        return ScheduleServicer.schedule_to_dto({
            "date": 0,
            "movies": []
        })

    @staticmethod
    def is_userid_admin(userid: str):
        response = requests.get(f"http://user:3004/users/{userid}/admin")
        return response.status_code == 200

    @staticmethod
    def check_schedule_not_used_in_booking(admin_id: str, date: int, movie_id: str):
        response = requests.post(
            "http://booking:3003/graphql",
            json={
                "query": f"""
                    query{{
                        bookings_with_admin_id(_admin_id:"{admin_id}") {{
                            dates {{
                                date
                                movies
                            }}
                        }}
                    }}
                """
            },
        )
        if response.status_code == 200:
            data = response.json()["data"]["bookings_with_admin_id"]
            if data is None:
                return True
            else:
                if any(any(bookingDate["date"] == str(date) and movie_id in bookingDate["movies"] for bookingDate in booking["dates"]) for booking in data):
                    return False
                return True
        raise Exception("Unknown error")

    # RPC

    def GetListSchedules(self, request, context):
        return schedule_pb2.Schedules(schedules=db.find_all())

    def GetScheduleByDate(self, request, context):
        schedule = db.find_by_date_or_none(request.date)
        if schedule is None :
            return self.movies_to_dto([])
        return self.movies_to_dto(schedule["movies"])

    def GetScheduleByMovie(self, request, context):
        dates = self.find_dates_by_movie(request.movie_id)
        return schedule_pb2.Dates(dates=dates)

    def AddSchedule(self, request, context):
        if not self.is_userid_admin(request.user_id):
            return self.empty_schedule_dto()
        schedule = db.find_by_date_or_none(request.schedule.date)
        movies = list(request.schedule.movies)
        for movie_id in movies:
            if not self.check_movie_exists(movie_id):
                return self.empty_schedule_dto()
        if schedule:
            for movie_id in movies:
                if next(filter(lambda _movie_id: movie_id == _movie_id, schedule["movies"]), None):
                    return self.empty_schedule_dto()
                schedule["movies"].append(movie_id)
            db.update(schedule)
        else:
            schedule = {
                "date": request.schedule.date,
                "movies": movies
            }
            db.create(schedule)
        return self.schedule_to_dto(schedule)

    def DeleteSchedule(self, request, context):
        if not self.is_userid_admin(request.user_id):
            return self.empty_schedule_dto()

        for movie in request.schedule.movies:
            if not self.check_schedule_not_used_in_booking(request.user_id, request.schedule.date, movie):
                return self.empty_schedule_dto()

        schedule = db.find_by_date_or_none(request.schedule.date)
        if schedule is None:
            return self.empty_schedule_dto()

        for movie_id in request.schedule.movies:
            if movie_id in schedule["movies"]:
                schedule["movies"].remove(movie_id)
            else:
                return self.empty_schedule_dto()
        if schedule["movies"]:
            db.update(schedule)
        else:
            db.delete(request.schedule.date)
        return self.schedule_to_dto(schedule)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script.py <json|mongo>")
        sys.exit(1)  # Exit if wrong number of arguments

    mode = sys.argv[1].lower()
    if mode not in ("json", "mongo"):
        print("Argument must be 'json' or 'mongo'")
        sys.exit(1)
    if mode == "json":
        db = ScheduleDBJsonConnector()
    else:
        db = ScheduleDBMongoConnector()

    serve()
