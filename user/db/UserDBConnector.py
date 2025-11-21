from abc import ABC, abstractmethod
from typing import Union

User = dict[str, Union[str, int]]

class UserDBConnector(ABC):
    @abstractmethod
    def find_by_id_or_none(self, _id: str) -> User | None:
        pass

    @abstractmethod
    def find_all(self) -> list[User]:
        pass

    @abstractmethod
    def create(self, user: User):
        pass

    @abstractmethod
    def update_last_active(self, _id: str, last_active: int) -> User | None:
        pass

    @abstractmethod
    def update_name(self, _id: str, name: str) -> User | None:
        pass

    @abstractmethod
    def delete(self, _id):
        pass
