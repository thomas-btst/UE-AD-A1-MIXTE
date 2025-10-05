import json
import requests
import grpc
import schedule_pb2
import schedule_pb2_grpc

db_path = './data'
db_movies_file = "movies.json"
db_actors_file = "actors.json"
db_movies_key = "movies"
db_actors_key = "actors"

def compute_path(file: str):
    return f'{db_path}/{file}'

def load(file: str, key: str):
    with open(compute_path(file), 'r') as file:
        return json.load(file)[key]

def write(file: str, key: str, value):
    with open(compute_path(file), 'w') as file:
        json.dump({key: value}, file)

movies = load(db_movies_file, db_movies_key)

actors = load(db_actors_file, db_actors_key)

def write_movies():
    write(db_movies_file, db_movies_key, movies)

def write_actors():
    write(db_actors_file, db_actors_key, actors)

def find_by_id_or_none(array, _id: str):
    return next(filter(lambda item: item["id"] == _id, array), None)

def find_movie_by_id_or_none(movie_id: str):
    return find_by_id_or_none(movies, movie_id)

def find_movie_by_id_or_raise(movie_id: str):
    movie = find_movie_by_id_or_none(movie_id)
    if movie is None:
        raise Exception(f"Movie with ID '{movie_id}' not found")
    return movie

def find_actor_by_id_or_none(actor_id: str):
    return find_by_id_or_none(actors, actor_id)

def find_actor_by_id_or_raise(actor_id: str):
    actor = find_actor_by_id_or_none(actor_id)
    if actor is None:
        raise Exception(f"Actor with ID '{actor_id}' not found")
    return actor

def find_actors_by_movie_id(movie_id: str):
    return [actor for actor in actors if movie_id in actor["movies"]]

def is_userid_admin_or_raise(userid: str):
    response = requests.get(f"http://localhost:3004/users/{userid}/admin")
    if response.status_code != 200:
        raise Exception("Access forbidden")

def assign_value_if_not_none(obj, key: str, value):
    if value is not None:
        obj[key] = value

# Resolvers

def list_movies(_,__):
    return movies

def movie_with_id(_,__,_id: str):
    return find_movie_by_id_or_raise(_id)

def add_movie(_, __, _id: str, _userid: str, _title: str, _director: str, _rating: float):
    is_userid_admin_or_raise(_userid)
    if find_movie_by_id_or_none(_id):
        raise Exception(f"Movie with ID '{_id}' already exists")
    new_movie = {
        "id": _id,
        "title": _title,
        "director": _director,
        "rating": _rating,
    }
    movies.append(new_movie)
    write_movies()
    return new_movie

def update_movie(_, __, _id: str, _userid: str, _title: str = None, _rating: float = None, _director: str = None):
    is_userid_admin_or_raise(_userid)
    movie = find_movie_by_id_or_raise(_id)
    assign_value_if_not_none(movie, "title", _title)
    assign_value_if_not_none(movie, "rating", _rating)
    assign_value_if_not_none(movie, "director", _director)
    write_movies()
    return movie

def delete_movie(_, __, _id: str, _userid: str):
    is_userid_admin_or_raise(_userid)
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = schedule_pb2_grpc.ScheduleServiceStub(channel)
        dates = stub.GetScheduleByMovie(schedule_pb2.MovieId(movie_id=_id)).dates
        if list(dates):
            raise Exception(f"Movie '{_id}' is used in a schedule")
    movie = find_movie_by_id_or_raise(_id)
    for actor in find_actors_by_movie_id(movie["id"]):
        actor["movies"].remove(_id)
    movies.remove(movie)
    write_actors()
    write_movies()
    return movie

def resolve_actors_in_movie(movie, _):
    return find_actors_by_movie_id(movie["id"])

def actor_with_id(_, __, _id: str):
    return find_actor_by_id_or_raise(_id)

def add_actor(_, __, _id: str, _userid: str, _firstname: str, _lastname: str, _birthyear: int, _movies):
    is_userid_admin_or_raise(_userid)
    if find_actor_by_id_or_none(_id):
        raise Exception(f"Actor with ID '{_id}' already exists")
    for movie in _movies:
        find_movie_by_id_or_raise(movie)
    new_actor = {
        "id": _id,
        "firstname": _firstname,
        "lastname": _lastname,
        "birthyear": _birthyear,
        "movies": _movies,
    }
    actors.append(new_actor)
    write_actors()
    return new_actor

def update_actor(_, __, _id: str, _userid: str, _firstname: str = None, _lastname: str = None, _birthyear: int = None, _movies=None):
    is_userid_admin_or_raise(_userid)
    actor = find_actor_by_id_or_raise(_id)
    if _movies:
        for movie in _movies:
            find_movie_by_id_or_raise(movie)
    assign_value_if_not_none(actor, "firstname", _firstname)
    assign_value_if_not_none(actor, "lastname", _lastname)
    assign_value_if_not_none(actor, "birthyear", _birthyear)
    assign_value_if_not_none(actor, "movies", _movies)
    write_actors()
    return actor

def delete_actor(_, __, _id: str, _userid: str):
    is_userid_admin_or_raise(_userid)
    actor = find_actor_by_id_or_raise(_id)
    actors.remove(actor)
    write_actors()
    return actor

def resolve_movies_in_actor(actor, _):
    return map(lambda movie_id: find_movie_by_id_or_none(movie_id) , actor["movies"])
