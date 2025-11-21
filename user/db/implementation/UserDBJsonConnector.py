from ..UserDBConnector import UserDBConnector, User
import json

class UserDBJsonConnector(UserDBConnector):
    def __init__(self):
        self.db_path = '{}/data/users.json'.format(".")
        self.db_root_key = 'users'

        with open(self.db_path, "r") as jsf:
            self.users = json.load(jsf)[self.db_root_key]

    def write(self):
        with open(self.db_path, 'w') as f:
            full = {self.db_root_key: self.users}
            json.dump(full, f)

    def find_by_id_or_none(self, _id: str) -> User | None:
        return next(filter(lambda user: user["id"] == _id, self.users), None)

    def find_all(self) -> list[User]:
        return self.users

    def create(self, user: User):
        self.users.append(user)
        self.write()

    def update_last_active(self, _id: str, last_active: int) -> User | None:
        user = self.find_by_id_or_none(_id)
        user["last_active"] = last_active
        self.write()
        return user

    def update_name(self, _id: str, name: str) -> User | None:
        user = self.find_by_id_or_none(_id)
        user["name"] = name
        self.write()
        return user

    def delete(self, _id):
        user = self.find_by_id_or_none(_id)
        self.users.remove(user)
        self.write()