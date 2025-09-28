from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response

import resolvers as r

PORT = 3003
HOST = '0.0.0.0'
app = Flask(__name__)

type_defs = load_schema_from_path('booking.graphql')

booking = ObjectType('Booking')

date = ObjectType('Date')

query = QueryType()
query.set_field('booking_with_userid', r.booking_with_userid)
query.set_field('bookings_with_admin_id', r.bookings_with_admin_id)
query.set_field('date_with_userid_and_date', r.date_with_userid_and_date)

mutation = MutationType()
mutation.set_field("add_booking", r.add_booking)
mutation.set_field("delete_booking", r.delete_booking)

schema = make_executable_schema(type_defs, booking, date, query, mutation)

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)