from datetime import datetime
from email.policy import default
from os import abort
from flask import make_response, Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo
from bson.json_util import loads, dumps
import json


app = Flask(__name__)
api = Api(app)
mongodb_client = PyMongo(app, uri="mongodb://localhost:27017/user_db")
db = mongodb_client.db

# db.user_db.insert({_id: NumberInt('1'), name: "josh", dob: "28-10-1990", address: "choa chu kang", description: "software engineer", createdAt: "06-05-2022 12:22:00"})
# db.user_db.insert({_id: NumberInt('2'), name: "bosh", dob: "29-10-1990", address: "jurong east", description: "software engineer", createdAt: "07-05-2022 23:45:00"})
# db.user_db.deleteOne({_id : 1})
#  curl http://127.0.0.1:5000/ -d '{"name": "josh", "dob": "30/10/1990", "address": "jurong west", "description": "nothing"}' -X POST -v -H 'Content-Type: application/json' -H 'Accept: application/json'



# set the arguments to be taken in during request
main_parser = reqparse.RequestParser()
main_parser.add_argument('name', type=str, help='Name of the user cannot be blank!', required=True, trim=True)
main_parser.add_argument('dob', type=lambda x: datetime.strptime(x,"%d/%m/%Y").date().strftime("%d/%m/%Y"), help='Date of Birth of the User must be in DD/MM/YYYY format, e.g 30/01/2022', required=True, trim=True)
main_parser.add_argument('address', type=str, help='Address of the user cannot be blank!', required=True, trim=True)
main_parser.add_argument('description', type=str, help='Description of the User', store_missing=False, trim=True)

# function to define custom error message
def custom_error(message, status):
    return make_response(jsonify(title=message, status_code = status), status)
class UserAPI(Resource):

    def get(self, user_id):
        # find and return user record based on user's id
        users = None
        if user_id:
            users = loads(dumps(db.user_db.find_one({"_id":user_id})))
            return users
        else:
            return custom_error("User not found!", 404)

    def put(self, user_id):
        updated_user = loads(dumps(db.user_db.find_one({"_id": user_id})))
        # update the argument so that it is optional
        put_parser = main_parser.copy()
        put_parser.replace_argument('name', type=str, help='Name of the user cannot be blank!', store_missing=False)
        put_parser.replace_argument('dob', type=lambda x: datetime.strptime(x,"%d/%m/%Y").date().strftime("%d/%m/%Y"), help='Date of Birth of the User must be in DD/MM/YYYY format, e.g 30/01/2022', store_missing=False)
        put_parser.replace_argument('address', type=str, help='Address of the user cannot be blank!', store_missing=False)
        args = put_parser.parse_args(strict=True)
        # if record exist, perform the update, else return custom error
        if updated_user:
            db.user_db.update_one({"_id": user_id}, {"$set":args})
            updated_user = loads(dumps(db.user_db.find_one({"_id": user_id})))
            return updated_user
        else:
            return custom_error("User not found!", 404)

    def delete(self, user_id):
        deleted_user = loads(dumps(db.user_db.find_one({"_id": user_id})))
        # if record exist, perform the delete, else return custom error
        if deleted_user:
            db.user_db.delete_one({"_id": user_id})
            return deleted_user
        else:
            return custom_error("User not found!", 404)

class UserListAPI(Resource):

    def get(self):
        # return all users
        users = loads(dumps(db.user_db.find()))
        return users

    def post(self):
        # initialize the ID variable
        last_user_id = None
        args = main_parser.parse_args(strict=True)
        # retrieve the last record in the db
        last_user = loads(dumps(db.user_db.find().limit(1).sort([( '$natural', -1 )] )))
        # set the ID to 0 if no records or the ID of the last record if exist
        if len(last_user) == 0:
            last_user_id = 0
        else:
            last_user_id = last_user[0]['_id']
        # insert the record into mongo with all the required values and increment the last record ID by 1
        db.user_db.insert_one({"_id": int(last_user_id+1), "name": args["name"], "dob": args["dob"], "address": args["address"], "description": args["description"], "createdAt": datetime.now().strftime("%d/%m/%Y %H:%M:%S")})
        # retrive the lastest record and return as json
        last_user = loads(dumps(db.user_db.find().limit(1).sort([( '$natural', -1 )] )))
        return last_user

api.add_resource(UserAPI, '/users/<int:user_id>', endpoint= 'user')
api.add_resource(UserListAPI, '/users', endpoint= 'users')

if __name__ == '__main__':
    app.run(debug=True)
