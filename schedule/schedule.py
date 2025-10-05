import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import requests

db_path = '{}/data/times.json'.format(".")
db_root_key = 'schedule'

class ScheduleServicer(schedule_pb2_grpc.ScheduleServiceServicer):

    def __init__(self):
        with open(db_path, "r") as jsf:
            self.schedules = json.load(jsf)[db_root_key]

    def write(self):
        with open(db_path, 'w') as file:
            json.dump({db_root_key: self.schedules}, file)

    def find_by_date_or_none(self, date: int):
        return next(filter(lambda schedule: schedule["date"] == date, self.schedules), None)

    @staticmethod
    def find_by_movie_id_in_schedule_or_none(schedule, movie_id: str):
        return next(filter(lambda _movie_id: movie_id == _movie_id, schedule["movies"]), None)

    def find_dates_by_movie(self, movie: str):
        filtered_schedules = filter(lambda schedule: movie in schedule["movies"], self.schedules)
        return list(map(lambda schedule: schedule["date"], filtered_schedules))

    @staticmethod
    def check_movie_exists(movie_id: str):
        response = requests.post(
            "http://localhost:3001/graphql",
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
        response = requests.get(f"http://localhost:3004/users/{userid}/admin")
        return response.status_code == 200

    # RPC

    def GetListSchedules(self, request, context):
        return schedule_pb2.Schedules(schedules=self.schedules)

    def GetScheduleByDate(self, request, context):
        schedule = self.find_by_date_or_none(request.date)
        if schedule is None :
            return self.movies_to_dto([])
        return self.movies_to_dto(schedule["movies"])

    def GetScheduleByMovie(self, request, context):
        dates = self.find_dates_by_movie(request.movie_id)
        return schedule_pb2.Dates(dates=dates)

    def AddSchedule(self, request, context):
        if not self.is_userid_admin(request.user_id):
            return self.empty_schedule_dto()
        schedule = self.find_by_date_or_none(request.schedule.date)
        movies = list(request.schedule.movies)
        for movie_id in movies:
            if not self.check_movie_exists(movie_id):
                return self.empty_schedule_dto()
        if schedule:
            for movie_id in movies:
                if self.find_by_movie_id_in_schedule_or_none(schedule, movie_id):
                    return self.empty_schedule_dto()
                schedule["movies"].append(movie_id)
        else:
            schedule = {
                "date": request.schedule.date,
                "movies": movies
            }
            self.schedules.append(schedule)
        self.write()
        return self.schedule_to_dto(schedule)

    def DeleteSchedule(self, request, context):
        if not self.is_userid_admin(request.user_id):
            return self.empty_schedule_dto()
        # TODO check schedule is not used in booking
        schedule = self.find_by_date_or_none(request.schedule.date)
        if schedule is None:
            return self.empty_schedule_dto()

        for movie_id in request.schedule.movies:
            if movie_id in schedule["movies"]:
                schedule["movies"].remove(movie_id)
            else:
                return self.empty_schedule_dto()
        if not schedule["movies"]:
            self.schedules.remove(schedule)
        self.write()
        return self.schedule_to_dto(schedule)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
