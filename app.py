from flask import Flask, jsonify
from pymongo import MongoClient


def connect():
    # Substitute the 5 pieces of information you got when creating
    # the Mongo DB Database (underlined in red in the screenshots)
    # REMEMBER to save username and password in an environment variable
        connection = MongoClient('ds143030.mlab.com', 43030)
        handle = connection['agency']
        handle.authenticate('agency_user', 'notsecret')
        return handle


app = Flask(__name__)
handle = connect()


@app.route('/')
def home_page():
    test_data = [x for x in handle.tests.find(
        {},
        {"name": True, "content": True, "_id": False, "requirements": True}
    )]
    return jsonify(results=test_data)


if __name__ == '__main__':
    app.run(debug=True)
