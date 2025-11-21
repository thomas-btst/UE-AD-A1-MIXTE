from abc import ABC, abstractmethod
from typing import Union

Movie = dict[str, Union[str, int]]

class MovieDBConnector(ABC):
    @abstractmethod
    def find_by_id_or_none(self, _id: str) -> Movie | None:
        pass

    @abstractmethod
    def find_all(self) -> list[Movie]:
        pass

    @abstractmethod
    def find_all_by_id(self, _ids: list[str]) -> list[Movie]:
        pass

    @abstractmethod
    def create(self, movie: Movie):
        pass

    @abstractmethod
    def update_title(self, _id: str, title: str) -> Movie | None:
        pass

    @abstractmethod
    def update_rating(self, _id: str, rating: float) -> Movie | None:
        pass

    @abstractmethod
    def update_director(self, _id, director: str) -> Movie | None:
        pass

    @abstractmethod
    def delete(self, _id):
        pass