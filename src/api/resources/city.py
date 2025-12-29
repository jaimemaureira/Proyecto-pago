import uuid
from flask import request
from flask_restful import Resource
from src.models import Ciudad  

class CityListResource(Resource):
    def get(self):
        id_pais = request.args.get("id_pais")
        if not id_pais:
            return {"error": "Falta id_pais"}, 400

        # Si tu columna es UUID(as_uuid=True) conviene convertir
        try:
            id_pais_uuid = uuid.UUID(id_pais)
        except ValueError:
            return {"error": "id_pais no es un UUID válido"}, 400

        ciudades = (
            Ciudad.query
            .filter(Ciudad.id_pais == id_pais_uuid)
            .order_by(Ciudad.nombre_ciudad.asc())
            .all()
        )

        return [
            {"id": str(c.id_ciudad), "nombre_ciudad": c.nombre_ciudad}
            for c in ciudades
        ], 200
