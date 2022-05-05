from flask import Flask, jsonify
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from bson.json_util import loads, dumps, LEGACY_JSON_OPTIONS


app = Flask(__name__)
api = Api(app)
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/user_db")
db = mongodb_client.db

{
"id": "xxx", # user ID
"name": "test", # user name
"dob": "", # date of birth
"address": "", # user address
"description": "", # user description
"createdAt": "" # user created date
}

# db.user_db.insert({_id: NumberInt('1'), name: "josh", dob: "28-10-1990", address: "choa chu kang", description: "software engineer", createdAt: "06-05-2022 12:22:00"})
# db.user_db.deleteOne({_id : 1})

class UserAPI(Resource):
    def get(self):
        userlist = []
        users = db.user_db.find()
        # for user in users:
        #     print(type(user))
        #     userlist.append(user)
        return loads(dumps(users))

    def post(self):
        return {'hello': 'world'}

    def put(self):
        return {'hello': 'world'}

    def delete(self):
        return {'hello': 'world'}

api.add_resource(UserAPI, '/')

if __name__ == '__main__':
    app.run(debug=True)
