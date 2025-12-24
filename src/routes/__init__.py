from flask import Blueprint

from ..extensions import db


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
	return {"message": "Bienvenido a Pago Auto"}


@main_bp.get("/db-ping")
def db_ping():
	try:
		# Executes a simple query to verify the DB connection
		result = db.session.execute(db.text("SELECT 1 AS ok"))
		row = result.first()
		return {"db": "connected", "ok": row.ok}
	except Exception as e:
		return {"db": "error", "message": str(e)}, 500

