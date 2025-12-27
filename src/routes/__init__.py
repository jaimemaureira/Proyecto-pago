from flask import Blueprint, flash, redirect, render_template, url_for
from src.forms.form_register import PersonaRegisterForm
from src.models.modeles import Rol
from src.services.propietarios_services import create_persona_role

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

@main_bp.route("/form_registro_usuarios.html", methods=["GET", "POST"])
def form_registro_usuarios():
    form = PersonaRegisterForm()

    # 1) Cargar roles desde DB
    roles_db = Rol.query.order_by(Rol.nombre_rol.asc()).all()
    form.roles.choices = [(r.nombre_rol, r.nombre_rol) for r in roles_db]

    # 2) Si envían formulario
    if form.validate_on_submit():
        persona_data = {
            "nombre": form.nombre.data,
            "apellido_pat": form.apellido_pat.data,
            "apellido_mat": form.apellido_mat.data,
            "rut": form.rut.data,
            "email": form.email.data,
            "num_tele": form.num_tele.data,
            "fecha_nac": form.fecha_nac.data,
            "direccion": form.direccion.data,
            "foto": form.foto.data,

            # extras conductor si aplican
            "licencia": form.licencia.data,
            "hoja_vida_conduct": form.hoja_vida_conduct.data,
        }

        role_names = form.roles.data  # lista de roles seleccionados

        persona, temp_password = create_persona_role(persona_data, role_names)

        flash(f"Usuario creado. Password temporal: {temp_password}", "success")
        return redirect(url_for("main.index"))

    return render_template("form_registro_usuarios.html", form=form)


@main_bp.get("/db-ping")
def db_ping():
	try:
		# Executes a simple query to verify the DB connection
		result = db.session.execute(db.text("SELECT 1 AS ok"))
		row = result.first()
		return {"db": "connected", "ok": row.ok}
	except Exception as e:
		return {"db": "error", "message": str(e)}, 500

