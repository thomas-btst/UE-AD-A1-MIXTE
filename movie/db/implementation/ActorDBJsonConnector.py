from ..ActorDBConnector import ActorDBConnector, Actor
import json

class ActorDBJsonConnector(ActorDBConnector):

    def __init__(self):
        self.db_path = '{}/data/actors.json'.format(".")
        self.db_root_key = 'actors'

        with open(self.db_path, "r") as jsf:
            self.actors = json.load(jsf)[self.db_root_key]

    def write(self):
        with open(self.db_path, 'w') as f:
            full = {self.db_root_key: self.actors}
            json.dump(full, f)

    def find_by_id_or_none(self, _id: str) -> Actor | None:
        return next(filter(lambda actor: actor["id"] == _id, self.actors), None)

    def find_all_by_movie_id(self, movie_id: str) -> list[Actor]:
        return [actor for actor in self.actors if movie_id in actor["movies"]]

    def create(self, actor: Actor):
        self.actors.append(actor)
        self.write()

    def update_firstname(self, _id: str, firstname: str) -> Actor | None:
        actor = self.find_by_id_or_none(_id)
        actor["firstname"] = firstname
        self.write()
        return actor

    def update_lastname(self, _id: str, lastname: str) -> Actor | None:
        actor = self.find_by_id_or_none(_id)
        actor["lastname"] = lastname
        self.write()
        return actor

    def update_birthyear(self, _id: str, birthyear: int) -> Actor | None:
        actor = self.find_by_id_or_none(_id)
        actor["birthyear"] = birthyear
        self.write()
        return actor

    def update_movies(self, _id: str, movies: list[str]) -> Actor | None:
        actor = self.find_by_id_or_none(_id)
        actor["movies"] = movies
        self.write()
        return actor

    def delete(self, _id: str):
        actor = self.find_by_id_or_none(_id)
        self.actors.remove(actor)
        self.write()