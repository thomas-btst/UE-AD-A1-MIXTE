from abc import ABC, abstractmethod
from typing import Union

Schedule = dict[str, Union[str, int, list[str]]]

class ScheduleDBConnector(ABC):
    @abstractmethod
    def find_by_date_or_none(self, date: int) -> Schedule | None:
        pass

    @abstractmethod
    def find_all_by_movie_id(self, movie_id: str) -> list[Schedule]:
        pass

    @abstractmethod
    def find_all(self) -> list[Schedule]:
        pass

    @abstractmethod
    def create(self, schedule: Schedule):
        pass

    @abstractmethod
    def update(self, schedule: Schedule):
        pass

    @abstractmethod
    def delete(self, date: int):
        pass