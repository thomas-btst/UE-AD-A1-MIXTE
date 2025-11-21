from ..ScheduleDBConnector import ScheduleDBConnector, Schedule
import json

class ScheduleDBJsonConnector(ScheduleDBConnector):

    def __init__(self):
        self.db_path = '{}/data/times.json'.format(".")
        self.db_root_key = 'schedule'

        with open(self.db_path, "r") as jsf:
            self.schedules = json.load(jsf)[self.db_root_key]

    def write(self):
        with open(self.db_path, 'w') as f:
            full = {self.db_root_key: self.schedules}
            json.dump(full, f)

    def find_by_date_or_none(self, date: int) -> Schedule | None:
        return next(filter(lambda schedule: schedule["date"] == date, self.schedules), None)

    def find_all_by_movie_id(self, movie_id: str) -> list[Schedule]:
        return list(filter(lambda schedule: movie_id in schedule["movies"], self.schedules))

    def find_all(self) -> list[Schedule]:
        return self.schedules

    def create(self, schedule: Schedule):
        self.schedules.append(schedule)
        self.write()

    def update(self, schedule: Schedule):
        found_schedule = self.find_by_date_or_none(schedule["date"])
        found_schedule["date"] = schedule["date"]
        found_schedule["movies"] = schedule["movies"]
        self.write()

    def delete(self, date: int):
        schedule = self.find_by_date_or_none(date)
        self.schedules.remove(schedule)
        self.write()


