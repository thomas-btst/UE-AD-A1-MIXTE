import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import requests

class ScheduleServicer(schedule_pb2_grpc.ScheduleServiceServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.schedules = json.load(jsf)["schedule"]

    def write(self):
        with open('{}/data/times.json'.format("."), 'w') as file:
            json.dump({"schedule": self.schedules}, file)

    def find_by_date_or_none(self, date: int):
        return next(filter(lambda schedule: schedule["date"] == date, self.schedules), None)

    @staticmethod
    def find_by_movie_id_in_schedule_or_none(schedule, movie_id: str):
        return next(filter(lambda _movie_id: movie_id == _movie_id, schedule["movies"]), None)

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

    # RPC

    def GetListSchedules(self, request, context):
        return schedule_pb2.Schedules(schedules=self.schedules)

    def GetScheduleByDate(self, request, context):
        schedule = self.find_by_date_or_none(request.date)
        if schedule is None :
            return schedule_pb2.Movies(movies=[])
        return schedule_pb2.Movies(movies=schedule["movies"])

    def AddSchedule(self, request, context):
        schedule = self.find_by_date_or_none(request.date)
        if schedule:
            for movie_id in list(request.movies):
                if self.find_by_movie_id_in_schedule_or_none(schedule, movie_id) or not self.check_movie_exists(movie_id):
                    return schedule_pb2.Schedule(date=0, movies=[])
                schedule["movies"].append(movie_id)
        else:
            schedule = {
                "date": request.date,
                "movies": list(request.movies) # TODO verify si les films existent
            }
            self.schedules.append(schedule)
        self.write()
        return schedule_pb2.Schedule(date=schedule["date"], movies=schedule["movies"])

    def DeleteSchedule(self, request, context):
        # TODO test the function
        # TODO check schedule is not used in booking
        schedule = self.find_by_date_or_none(request.date)
        if schedule is None:
            return schedule_pb2.Schedule(date=0, movies=[])

        for movie_id in request.movies:
            if movie_id in schedule["movies"]:
                schedule["movies"].remove(movie_id)
            else:
                return schedule_pb2.Schedule(date=0, movies=[]) # TODO use in function
        if not schedule["movies"]:
            self.schedules.remove(schedule)
        self.write()
        return schedule_pb2.Schedule(date=schedule["date"], movies=schedule["movies"]) # TODO use in function

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
