# REST API
from flask import Flask, render_template, request, jsonify, make_response
import json
import time

from werkzeug.exceptions import Forbidden, NotFound, Conflict

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

db_path = '{}/data/users.json'.format(".")
db_root_key = 'users'

with open(db_path, "r") as jsf:
   users = json.load(jsf)[db_root_key]

def write(_users):
    with open(db_path, 'w') as f:
        full = {db_root_key: _users}
        json.dump(full, f)

def timestamp():
    return int(time.time())

def find_user_by_id_or_none(_id: str):
    return next(filter(lambda user: user["id"] == _id, users), None)

def find_user_by_id_or_raise(_id: str):
    user = find_user_by_id_or_none(_id)
    if user is None:
        raise NotFound(f"User with id '{_id}' not found")
    return user

def is_admin_id_or_raise(admin_id: str):
    user = find_user_by_id_or_none(admin_id)
    if user is None or not user["is_admin"]:
        raise Forbidden("Access forbidden")
    return user

@app.route("/users/admin/<admin_id>", methods=['GET'])
def list_users(admin_id: str):
    is_admin_id_or_raise(admin_id)
    return make_response(jsonify(users))

@app.route("/users/<userid>", methods=['GET'])
def get_user(userid: str):
    return make_response(jsonify(find_user_by_id_or_raise(userid)))

@app.route("/users/<admin_id>/admin", methods=['GET'])
def is_admin(admin_id: str):
    return make_response(jsonify(is_admin_id_or_raise(admin_id)))

@app.route("/users", methods=['POST'])
def create_user():
    req = request.get_json()

    userid = str(req["id"])

    if find_user_by_id_or_none(userid):
        raise Conflict(f"User with ID '{userid}' already exists")

    user = {
      "id": userid,
      "name": str(req["name"]),
      "last_active": timestamp(),
      "is_admin": False,
    }
    users.append(user)
    write(users)
    return make_response(jsonify(user),200)

@app.route("/users/<userid>/last-active", methods=['PATCH'])
def update_last_active(userid: str):
    user = find_user_by_id_or_raise(userid)
    user["last_active"] = timestamp()
    write(users)
    return make_response(jsonify(user),200)

@app.route("/users/<userid>/name", methods=['PATCH'])
def update_name(userid: str):
    req = request.get_json()
    user = find_user_by_id_or_raise(userid)
    user["name"] = str(req["name"])
    user["last_active"] = timestamp()
    write(users)
    return make_response(jsonify(user),200)

@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid: str):
    user = find_user_by_id_or_raise(userid)
    users.remove(user)
    write(users)
    return make_response(jsonify(user), 500)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
