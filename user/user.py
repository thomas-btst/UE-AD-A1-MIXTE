# REST API
import sys

from flask import Flask, render_template, request, jsonify, make_response
import time

from werkzeug.exceptions import Forbidden, NotFound, Conflict
from flask_swagger_ui import get_swaggerui_blueprint

from db.UserDBConnector import UserDBConnector
from db.implementation.UserDBJsonConnector import UserDBJsonConnector
from db.implementation.UserDBMongoConnector import UserDBMongoConnector

app = Flask(__name__)

PORT = 3004
HOST = '0.0.0.0'

SWAGGER_URL = "/docs"
API_URL = "/static/openapi.en.yml"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "User Management API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

db: UserDBConnector

def timestamp():
    return int(time.time())

def find_user_by_id_or_raise(_id: str):
    user = db.find_by_id_or_none(_id)
    if user is None:
        raise NotFound(f"User with id '{_id}' not found")
    return user

def is_admin_id_or_raise(admin_id: str):
    user = db.find_by_id_or_none(admin_id)
    if user is None or not user["is_admin"]:
        raise Forbidden("Access forbidden")
    return user

@app.route("/users/admin/<admin_id>", methods=['GET'])
def list_users(admin_id: str):
    is_admin_id_or_raise(admin_id)
    return make_response(jsonify(db.find_all()), 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user(userid: str):
    return make_response(jsonify(find_user_by_id_or_raise(userid)), 200)

@app.route("/users/<admin_id>/admin", methods=['GET'])
def is_admin(admin_id: str):
    return make_response(jsonify(is_admin_id_or_raise(admin_id)), 200)

@app.route("/users", methods=['POST'])
def create_user():
    req = request.get_json()

    userid = str(req["id"])

    if db.find_by_id_or_none(userid):
        raise Conflict(f"User with ID '{userid}' already exists")

    user = {
      "id": userid,
      "name": str(req["name"]),
      "last_active": timestamp(),
      "is_admin": False,
    }
    db.create(user)
    return make_response(jsonify(user),200)

@app.route("/users/<userid>/last-active", methods=['PATCH'])
def update_last_active(userid: str):
    find_user_by_id_or_raise(userid)
    db.update_last_active(userid, timestamp())
    updated_user = db.find_by_id_or_none(userid)
    return make_response(jsonify(updated_user),200)

@app.route("/users/<userid>/name", methods=['PATCH'])
def update_name(userid: str):
    req = request.get_json()
    find_user_by_id_or_raise(userid)
    db.update_name(userid, str(req["name"]))
    updated_user = db.update_last_active(userid, timestamp())
    return make_response(jsonify(updated_user),200)

@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid: str):
    user = find_user_by_id_or_raise(userid)
    db.delete(userid)
    return make_response(jsonify(user), 200)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <json|mongo>")
        sys.exit(1)  # Exit if wrong number of arguments

    mode = sys.argv[1].lower()
    if mode not in ("json", "mongo"):
        print("Argument must be 'json' or 'mongo'")
        sys.exit(1)
    if mode == "json":
        db = UserDBJsonConnector()
    else:
        db = UserDBMongoConnector()

    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)
