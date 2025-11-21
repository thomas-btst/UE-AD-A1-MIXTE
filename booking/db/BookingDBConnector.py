from abc import ABC, abstractmethod
from typing import Union, Any

Booking = dict[str, Union[str, int, list[Any]]]

class BookingDBConnector(ABC):
    @abstractmethod
    def find_by_userid_or_none(self, userid: str) -> Booking | None:
        pass

    @abstractmethod
    def find_all(self) -> list[Booking]:
        pass

    @abstractmethod
    def create(self, booking: Booking):
        pass

    @abstractmethod
    def update(self, booking: Booking):
        pass

    @abstractmethod
    def delete(self, userid: str):
        pass