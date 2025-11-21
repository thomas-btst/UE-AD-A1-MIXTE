from ..MovieDBConnector import MovieDBConnector, Movie
import json

class MovieDBJsonConnector(MovieDBConnector):
    def __init__(self):
        self.db_path = '{}/data/movies.json'.format(".")
        self.db_root_key = 'movies'

        with open(self.db_path, "r") as jsf:
            self.movies = json.load(jsf)[self.db_root_key]

    def write(self):
        with open(self.db_path, 'w') as f:
            full = {self.db_root_key: self.movies}
            json.dump(full, f)

    def find_by_id_or_none(self, _id: str) -> Movie | None:
        return next(filter(lambda item: item["id"] == _id, self.movies), None)

    def find_all(self) -> list[Movie]:
        return self.movies

    def find_all_by_id(self, _ids: list[str]) -> list[Movie]:
        return list(filter(lambda movie: movie["id"] in _ids, self.movies))

    def create(self, movie: Movie):
        self.movies.append(movie)
        self.write()

    def update_title(self, _id: str, title: str) -> Movie | None:
        movie = self.find_by_id_or_none(_id)
        movie["title"] = title
        self.write()
        return movie

    def update_rating(self, _id: str, rating: float) -> Movie | None:
        movie = self.find_by_id_or_none(_id)
        movie["rating"] = rating
        self.write()
        return movie

    def update_director(self, _id, director: str) -> Movie | None:
        movie = self.find_by_id_or_none(_id)
        movie["director"] = director
        self.write()
        return movie

    def delete(self, _id):
        movie = self.find_by_id_or_none(_id)
        self.movies.remove(movie)
        self.write()