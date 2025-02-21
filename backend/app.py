from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)


def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.

    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})

@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)

@app.route("/shows", methods=['GET'])
def get_all_shows():
    return create_response({"shows": db.get('shows')})

@app.route("/shows/<id>", methods=['DELETE'])
def delete_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    db.deleteById('shows', int(id))
    return create_response(message="Show deleted")

#my code starts here!
@app.route("/shows/<id>", methods=['GET'])
def get_one_show(id):
    show = db.getById("shows", int(id))
    if show is None:
        return create_response(status=404, message="No show with this id exists")
    return create_response({"show": show})

@app.route("/shows", methods=['POST'])
def create_show():
    request_data = request.get_json()
    show_entry = {"id": None}
    try:
        show_entry["name"] = request_data["name"]
    except (ValueError, KeyError, TypeError):
        return create_response(status=404, message="Need 'name' and 'episodes_seen' parameters.")
    try:
        show_entry["episodes_seen"] = request_data["episodes_seen"]
    except (ValueError, KeyError, TypeError):
        return create_response(status=404, message="Need an 'episodes_seen' parameter.")
    created_id = db.create("shows", show_entry) #changed 'create' function to return new id
    show = db.getById("shows", int(created_id))
    return create_response(data={"show": show}, status=201)

@app.route("/shows/<id>", methods=['PUT'])
def update_show(id):
    request_data = request.get_json()
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    update_entry = {}
    try:
        update_entry["name"] = request_data["name"]
    except (ValueError, KeyError, TypeError):
        pass
    try:
        update_entry["episodes_seen"] = request_data["episodes_seen"]
    except (ValueError, KeyError, TypeError):
        pass
    db.updateById("shows", int(id), update_entry)
    show = db.getById("shows", int(id))
    return create_response(data={"show": show}, status=201)


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(port=8080, debug=True)
