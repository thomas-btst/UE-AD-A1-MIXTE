import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json

class ScheduleServicer(schedule_pb2_grpc.ScheduleServiceServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.schedules = json.load(jsf)["schedule"]

    def write(self):
        with open('{}/data/times.json'.format("."), 'w') as file:
            json.dump({"schedule": self.schedules}, file)

    def find_by_date_or_none(self, date: int):
        return next(filter(lambda schedule: schedule["date"] == date, self.schedules), None)

    # RPC

    def GetListSchedules(self, request, context):
        return schedule_pb2.Schedules(schedules=self.schedules)

    def GetScheduleByDate(self, request, context):
        schedule = self.find_by_date_or_none(request.date)
        if schedule is None :
            return schedule_pb2.Movies(movies=[])
        return schedule_pb2.Movies(movies=schedule["movies"])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServiceServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
