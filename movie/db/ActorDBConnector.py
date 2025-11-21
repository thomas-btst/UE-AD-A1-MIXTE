from abc import ABC, abstractmethod
from typing import Union

Actor = dict[str, Union[str, int, list[str]]]

class ActorDBConnector(ABC):
    @abstractmethod
    def find_by_id_or_none(self, _id: str) -> Actor | None:
        pass

    @abstractmethod
    def find_all_by_movie_id(self, movie_id: str) -> list[Actor]:
        pass

    @abstractmethod
    def create(self, actor: Actor):
        pass

    @abstractmethod
    def update_firstname(self, _id: str, firstname: str) -> Actor | None:
        pass

    @abstractmethod
    def update_lastname(self, _id: str, lastname: str) -> Actor | None:
        pass

    @abstractmethod
    def update_birthyear(self, _id: str, birthyear: int) -> Actor | None:
        pass

    @abstractmethod
    def update_movies(self, _id: str, movies: list[str]) -> Actor | None:
        pass

    @abstractmethod
    def delete(self, _id: str):
        pass