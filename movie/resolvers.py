import requests
import grpc
import schedule_pb2
import schedule_pb2_grpc
import sys

from dotenv import load_dotenv

from db.implementation.ActorDBJsonConnector import ActorDBJsonConnector
from db.implementation.MovieDBJsonConnector import MovieDBJsonConnector
from db.implementation.ActorDBMongoConnector import ActorDBMongoConnector
from db.implementation.MovieDBMongoConnector import MovieDBMongoConnector
from db.MovieDBConnector import MovieDBConnector
from db.ActorDBConnector import ActorDBConnector
import os

load_dotenv()

SCHEDULE_API = os.getenv("SCHEDULE_API") or "localhost:3002"

# Database Connector
movie_db: MovieDBConnector
actor_db: ActorDBConnector

USER_API = os.getenv("USER_API") or "localhost:3004"

match (os.getenv("DB_TYPE")):
    case "json":
        movie_db = MovieDBJsonConnector()
        actor_db = ActorDBJsonConnector()
    case "mongo":
        movie_db = MovieDBMongoConnector()
        actor_db = ActorDBMongoConnector()
    case _:
        print("DB_TYPE env variable must be 'json' or 'mongo'")
        sys.exit(1)

# Helpers

def find_movie_by_id_or_raise(movie_id: str):
    movie = movie_db.find_by_id_or_none(movie_id)
    if movie is None:
        raise Exception(f"Movie with ID '{movie_id}' not found")
    return movie

def find_actor_by_id_or_raise(actor_id: str):
    actor = actor_db.find_by_id_or_none(actor_id)
    if actor is None:
        raise Exception(f"Actor with ID '{actor_id}' not found")
    return actor

def is_userid_admin_or_raise(userid: str):
    response = requests.get(f"http://{USER_API}/users/{userid}/admin")
    if response.status_code != 200:
        raise Exception("Access forbidden")

# Resolvers

def list_movies(_,__):
    return movie_db.find_all()

def movie_with_id(_,__,_id: str):
    return find_movie_by_id_or_raise(_id)

def add_movie(_, __, _id: str, _userid: str, _title: str, _director: str, _rating: float):
    is_userid_admin_or_raise(_userid)
    if movie_db.find_by_id_or_none(_id):
        raise Exception(f"Movie with ID '{_id}' already exists")
    new_movie = {
        "id": _id,
        "title": _title,
        "director": _director,
        "rating": _rating,
    }
    movie_db.create(new_movie)
    return new_movie

def update_movie(_, __, _id: str, _userid: str, _title: str = None, _rating: float = None, _director: str = None):
    is_userid_admin_or_raise(_userid)
    movie = find_movie_by_id_or_raise(_id)
    if _title is not None:
        movie = movie_db.update_title(_id, _title)
    if _rating is not None:
        movie = movie_db.update_rating(_id, _rating)
    if _director is not None:
        movie = updated_movie = movie_db.update_director(_id, _director)
    return movie

def delete_movie(_, __, _id: str, _userid: str):
    is_userid_admin_or_raise(_userid)
    with grpc.insecure_channel(SCHEDULE_API) as channel:
        stub = schedule_pb2_grpc.ScheduleServiceStub(channel)
        dates = stub.GetScheduleByMovie(schedule_pb2.MovieId(movie_id=_id)).dates
        if list(dates):
            raise Exception(f"Movie '{_id}' is used in a schedule")
    movie = find_movie_by_id_or_raise(_id)
    for actor in actor_db.find_all_by_movie_id(movie["id"]):
        movies = actor["movies"]
        movies.remove(_id)
        actor_db.update_movies(actor["id"], movies)
    movie_db.delete(_id)
    return movie

def resolve_actors_in_movie(movie, _):
    return actor_db.find_all_by_movie_id(movie["id"])

def actor_with_id(_, __, _id: str):
    return find_actor_by_id_or_raise(_id)

def add_actor(_, __, _id: str, _userid: str, _firstname: str, _lastname: str, _birthyear: int, _movies):
    is_userid_admin_or_raise(_userid)
    if actor_db.find_by_id_or_none(_id):
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
    actor_db.create(new_actor)
    return new_actor

def update_actor(_, __, _id: str, _userid: str, _firstname: str = None, _lastname: str = None, _birthyear: int = None, _movies=None):
    is_userid_admin_or_raise(_userid)
    actor = find_actor_by_id_or_raise(_id)
    if _movies:
        for movie in _movies:
            find_movie_by_id_or_raise(movie)
    if _firstname is not None:
        actor_db.update_firstname(_id, _firstname)
    if _lastname is not None:
        actor_db.update_lastname(_id, _lastname)
    if _birthyear is not None:
        actor_db.update_birthyear(_id, _birthyear)
    if _movies is not None:
        actor_db.update_movies(_id, _movies)
    return actor

def delete_actor(_, __, _id: str, _userid: str):
    is_userid_admin_or_raise(_userid)
    actor = find_actor_by_id_or_raise(_id)
    actor_db.delete(_id)
    return actor

def resolve_movies_in_actor(actor, _):
    return movie_db.find_all_by_id(actor["movies"])
