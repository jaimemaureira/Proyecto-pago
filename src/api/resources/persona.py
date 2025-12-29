from flask_restful import Resource

class PersonaListResource(Resource):
    def get(self):
        return {"status": "ok", "data": []}, 200