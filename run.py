from src import create_app
from flask_migrate import Migrate
from src.models import db
from src.models import Persona, Propietario, Automovil, Conductor, Turno, Documento, Venta_guia


app = create_app()

migrate = Migrate(app, db)



if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5000, debug=True)

