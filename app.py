from flask import Flask, jsonify, request
from flask_restful import abort, Api, Resource

app = Flask(__name__)
api = Api(app)

class DB():
    def __init__(self):
        self.NOTES = {
            "n1" : {'title':'A Note'},
            "n2" : {'title':'Another Note'},
            "n3" : {'title':'Yet another Note'},
        }

    def get(self, id):
        return self.NOTES.get(id, None)

    def delete(self, id):
        return self.NOTES.pop(id, None)

    def update(self, id, json):
        if id not in self.NOTES:
            return None
        else:
            self.NOTES[id] = json
            return json
    
    def add(self, json):
        note_id = 'n%i' % (int(max(self.NOTES.keys()).lstrip('n')) + 1)
        self.NOTES[note_id] = json
        return {note_id : json}

    def query(self, criteria):
        return self.NOTES


class Note(Resource):
    def __init__(self, db):
        self.db = db

    def get(self, note_id):
        note = self.db.get(note_id)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return note
    
    def delete(self, note_id):
        note = self.db.delete(note_id)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return '', 204

    def put(self, note_id):
        json = request.get_json()
        note = self.db.update(note_id, json)
        if not note:
            abort(404, message="Note {} doesn't exist".format(note_id))
        return note


class NoteList(Resource):
    def __init__(self, db):
        self.db = db

    def get(self):
        return self.db.query('ALL')

    def post(self):
        json = request.get_json()
        note = self.db.add(json)
        if not note:
            abort(404, message="Cannot create new note")
        return note, 201
        
        
db = DB()
api.add_resource(Note, "/v1/resources/notes/<note_id>", resource_class_kwargs={'db':db})
api.add_resource(NoteList, "/v1/resources/notes", resource_class_kwargs={'db':db})


if __name__ == "main":
    app.run(host="127.0.0.1", port=5000)