from flask import Flask, jsonify, request
from flask_restful import abort, Api, Resource

from pymongo import MongoClient
from bson.objectid import ObjectId
# from bson.json_util import dumps, RELAXED_JSON_OPTIONS


app = Flask(__name__)
api = Api(app)

class KublaiDB():

    def __init__(self, dbhost='localhost', dbport=27017, dbname = 'kublai'):
        self.dbhost = dbhost
        self.dbport = dbport
        self.dbname = dbname

    def connect(self):
        client = MongoClient(self.dbhost, self.dbport)
        db = client[self.dbname]
        self.notes = db['notes']
        self.templates = db['templates']

    def get_note(self, id):
        return self.notes.find_one({"_id" : ObjectId(id)})

    def delete_note(self, id):
        return self.notes.find_one_and_delete({"_id" : ObjectId(id)})

    def update_note(self, id, json):
        return self.notes.find_one_and_replace({"_id" : ObjectId(id)}, json)
    
    def add_note(self, json):
        result = self.notes.insert_one(json)
        return None if not result.acknowledged else result.inserted_id

    def find_notes(self, filter):
        # results = []
        # for d in self.notes.find(filter):
        #     results.append(dumps(d))
        # return results
        return list(self.notes.find(filter))

    # see https://pymongo.programmingpedia.net/en/tutorial/9348/converting-between-bson-and-json
    def convert(self, bson):
        return dumps(bson) if bson else None

# class DB():
#     def __init__(self):
#         self.NOTES = {
#             "n1" : {'title':'A Note'},
#             "n2" : {'title':'Another Note'},
#             "n3" : {'title':'Yet another Note'},
#         }

#     def connect():
#         pass

#     def get(self, id):
#         return self.NOTES.get(id, None)

#     def delete(self, id):
#         return self.NOTES.pop(id, None)

#     def update(self, id, json):
#         if id not in self.NOTES:
#             return None
#         else:
#             self.NOTES[id] = json
#             return json
    
#     def add(self, json):
#         note_id = 'n%i' % (int(max(self.NOTES.keys()).lstrip('n')) + 1)
#         self.NOTES[note_id] = json
#         return {note_id : json}

#     def query(self, criteria):
#         return self.NOTES


class Note(Resource):
    def __init__(self, db):
        self.db = db

    def get(self, note_id):
        note = self.db.get_note(note_id)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return note
    
    def delete(self, note_id):
        note = self.db.delete_note(note_id)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return '', 204

    def put(self, note_id):
        json = request.get_json()
        note = self.db.update_note(note_id, json)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return note


class NoteList(Resource):
    def __init__(self, db):
        self.db = db

    def get(self):
        return self.db.find_notes({})

    def post(self):
        json = request.get_json()
        note_id = self.db.add_note(json)
        if not note_id:
            abort(404, message="Cannot create new note")
        return note_id, 201
        
        
db = KublaiDB()
db.connect()

api.add_resource(Note, "/v1/resources/notes/<note_id>", resource_class_kwargs={'db':db})
api.add_resource(NoteList, "/v1/resources/notes", resource_class_kwargs={'db':db})

if __name__ == "main":
    app.run(host="127.0.0.1", port=5000)