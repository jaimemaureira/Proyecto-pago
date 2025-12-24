from flask import Flask

from .config import Config
from .extensions import db
from .routes import main_bp


def create_app() -> Flask:
	app = Flask(__name__, template_folder="templates", static_folder="static")
	app.config.from_object(Config)

	# Init extensions
	db.init_app(app)

	# Blueprints
	app.register_blueprint(main_bp)

	@app.get("/health")
	def health():
		return {"status": "ok"}

	return app

