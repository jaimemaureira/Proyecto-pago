from flask import Blueprint
from flask_restful import Api
from .resources.persona import PersonaListResource
from .resources.city import CityListResource

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

api.add_resource(PersonaListResource, "/personas")
api.add_resource(CityListResource, "/cities")