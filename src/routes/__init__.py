from flask import Blueprint, render_template

from ..extensions import db


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
	return render_template("index.html")

@main_bp.get("/owner.html")
def owner():
    return render_template("owner.html")

@main_bp.get("/driver.html")
def driver():
    return render_template("driver.html")

@main_bp.get("/guias.html")
def guias():
    return render_template("guias_despacho.html")

@main_bp.get("/super_adm_panel.html")
def super_adm_panel():
    return render_template("super_adm_panel.html")

@main_bp.get("/form_registro_usuarios.html")
def form_registro_usuarios():
    return render_template("form_registro_usuarios.html")


@main_bp.get("/db-ping")
def db_ping():
	try:
		# Executes a simple query to verify the DB connection
		result = db.session.execute(db.text("SELECT 1 AS ok"))
		row = result.first()
		return {"db": "connected", "ok": row.ok}
	except Exception as e:
		return {"db": "error", "message": str(e)}, 500

