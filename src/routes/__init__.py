from functools import wraps
from flask import Blueprint, flash, redirect, render_template, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import random
from datetime import datetime, timedelta
from forms.form_register_vehicle import VehicleRegisterForm
from src.forms.form_change_psw import recoveryPassword
from src.forms.logout_form import LogoutForm
from src.forms.login_form import LoginForm
from src.forms.two_factor_form import TwoFactorForm
from src.extensions import db
from src.forms.form_register import PersonaRegisterForm
from src.forms.form_set_password import SetPasswordForm
from src.models import Persona
from src.models.modeles import MasterAdmin, Rol, Pais, Ciudad
from src.services.propietarios_services import ROLE_TABLE, _norm_role, create_persona_role
from src.services.storage import upload_to_bucket
from src.services.email_service import send_set_password_email
from src.services.password_reset_tokens import make_reset_token, verify_reset_token
from src.services.sms_service import send_sms
from src.models.modeles import Persona, Rol, Conductor



main_bp = Blueprint("main", __name__)

@main_bp.after_request
def add_no_cache(resp):
    if request.endpoint in {"main.verify_2fa", "main.index"}:
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp

ROLE_TARGETS = {
    "propietario": "main.owner",
    "conductor": "main.driver",
    "administrador": "main.super_adm_panel",
    "master_admin": "main.super_adm_panel",
}
norm_role = _norm_role  # alias para usar en este archivo

@main_bp.route("/", methods=["GET", "POST"])
def index():
    form = LoginForm()
    if session.get("persona_id"):
        roles = session.get("roles", [])
        for key in ["master_admin", "administrador", "conductor", "propietario"]:
            if key in roles:
                return redirect(url_for(ROLE_TARGETS[key]))
        return redirect(url_for("main.index"))

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        pwd = form.password.data
        p = Persona.query.filter_by(email=email).first()
        if not p or not check_password_hash(p.password_hash, pwd):
            flash("Credenciales inválidas.", "danger")
            return render_template("index.html", form=form)

        # Paso 1: preparar 2FA por SMS
        if not p.num_tele:
            flash("Tu cuenta no tiene teléfono registrado.", "warning")
            return render_template("index.html", form=form)

        # Guardar datos en sesión pendientes de verificación
        session["pending_persona_id"] = str(p.id_persona)
        session["pending_roles"] = [_norm_role(r.nombre_rol) for r in p.roles]

        # Generar código 2FA
        code = f"{random.randint(100000, 999999)}"  # 6 dígitos
        session["two_factor_hash"] = generate_password_hash(code)
        session["two_factor_exp"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        session["two_factor_phone"] = p.num_tele

        # Enviar SMS (si Twilio configurado; si no, fallback a consola)
        sent = send_sms(p.num_tele, f"Tu código de verificación es: {code}")
        if not sent:
            flash("No se pudo enviar el SMS. Intenta más tarde.", "danger")
            return render_template("index.html", form=form)

        flash("Te enviamos un código al teléfono registrado.", "info")
        return redirect(url_for("main.verify_2fa"))

    return render_template("index.html", form=form)


@main_bp.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    if session.get("persona_id"):
        roles = session.get("roles", [])
        for key in ["master_admin", "administrador", "conductor", "propietario"]:
            if key in roles:
                return redirect(url_for(ROLE_TARGETS[key]))
        return redirect(url_for("main.index"))
    # Debe existir un login pendiente
    if not session.get("pending_persona_id"):
        flash("Inicia sesión para validar tu código.", "warning")
        return redirect(url_for("main.index"))

    form = TwoFactorForm()
    phone = session.get("two_factor_phone", "")
    # Enmascarar teléfono visualmente
    masked = phone
    if isinstance(phone, str) and len(phone) >= 4:
        masked = f"***{phone[-4:]}"

    if form.validate_on_submit():
        code_entered = (form.code.data or "").strip()
        code_hash = session.get("two_factor_hash")
        exp_str = session.get("two_factor_exp")
        # Validación de expiración
        try:
            if exp_str and datetime.utcnow() > datetime.fromisoformat(exp_str):
                flash("El código expiró. Solicita reenvío.", "warning")
                return render_template("verify_2fa.html", form=form, masked_phone=masked)
        except Exception:
            pass

        if not code_hash or not check_password_hash(code_hash, code_entered):
            flash("Código incorrecto.", "danger")
            return render_template("verify_2fa.html", form=form, masked_phone=masked)

        # Éxito: completar sesión
        persona_id = session.pop("pending_persona_id", None)
        roles = session.pop("pending_roles", [])
        session.pop("two_factor_hash", None)
        session.pop("two_factor_exp", None)
        session.pop("two_factor_phone", None)

        session["persona_id"] = persona_id
        session["roles"] = roles

        # Redirección por rol
        if session.get("persona_id"):
            roles = session.get("roles", [])
            for key in ["master_admin", "administrador", "conductor", "propietario"]:
                if key in roles:
                    return redirect(url_for(ROLE_TARGETS[key]))
        return redirect(url_for("main.index"))

    return render_template("verify_2fa.html", form=form, masked_phone=masked)


@main_bp.route("/resend-2fa", methods=["POST"])
def resend_2fa():
    if not session.get("pending_persona_id"):
        flash("Inicia sesión para validar tu código.", "warning")
        return redirect(url_for("main.index"))

    # Generar y enviar nuevo código
    code = f"{random.randint(100000, 999999)}"
    session["two_factor_hash"] = generate_password_hash(code)
    session["two_factor_exp"] = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    phone = session.get("two_factor_phone")
    sent = send_sms(phone, f"Tu nuevo código es: {code}")
    if sent:
        flash("Enviamos un nuevo código.", "info")
    else:
        flash("No se pudo enviar el SMS de reenvío.", "danger")

    return redirect(url_for("main.verify_2fa"))

#elimina cache una vez autenticado el usuario, evita volver a la pagina de login con el boton atras
@main_bp.after_request
def add_no_cache(resp):
    if request.endpoint in {"main.verify_2fa", "main.index"}:
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
    return resp

# Recuperación de contraseña
@main_bp.route("/recover-password", methods=["GET", "POST"], endpoint="recover_password")
def recovery_password():
    form = recoveryPassword()
    if form.validate_on_submit():
        email = (form.email.data or "").strip().lower()
        persona = Persona.query.filter_by(email=email).first()
        if persona:
            try:
                token = make_reset_token(persona.id_persona, persona.reset_nonce)
                link = request.url_root.rstrip("/") + url_for("main.set_password", token=token)
                print("Password reset link:", link)
                send_set_password_email(persona.email, persona.nombre, link)
            except Exception:
                pass
        flash("Si el correo existe, te enviamos un enlace para restablecer tu contraseña.", "info")
        return redirect(url_for("main.index"))
    return render_template("recovery_password.html", form=form)


#inyectar nombre de persona en el navbar
@main_bp.context_processor
def inject_current_persona():
    try:
        pid = session.get("persona_id")
        persona = Persona.query.get(uuid.UUID(pid)) if pid else None

        # 1) Preferir los roles ya normalizados en sesión (puestos en login)
        roles = session.get("roles", [])
        role_key = roles[0] if roles else None

        # 2) Si no hay en sesión, tomar el primero desde DB y normalizar
        if not role_key and persona and getattr(persona, "roles", None):
            role_key = _norm_role(persona.roles[0].nombre_rol)

        role_label = ROLE_TABLE.get(role_key, role_key) if role_key else None
        return {"current_persona": persona, "current_role": role_label}
    except Exception:
        return {"current_persona": None, "current_role": None}


# Rutas de páginas estáticas
@main_bp.get("/owner.html")
def owner():
    return render_template("owner.html")

@main_bp.get("/find_gps.html")
def find_gps():
    return render_template("find_gps.html")


@main_bp.get("/driver.html")
def driver():
    return render_template("driver.html")

# Ruta de guías de despacho
@main_bp.get("/guias.html")
def guias():
    return render_template("guias_despacho.html")

# Decoradores de roles y login
def require_roles(*allowed):
    def wrap(fn):
        @wraps(fn)
        def inner(*args, **kwargs):
            roles = session.get("roles", [])
            if not any(r in roles for r in allowed):
                flash("No autorizado.", "danger")
                return redirect(url_for("main.index"))
            return fn(*args, **kwargs)
        return inner
    return wrap

# Decorador para requerir login
def login_required(fn):
    @wraps(fn)
    def inner(*args, **kwargs):
        if not session.get("persona_id"):
            flash("Debes iniciar sesión.", "warning")
            return redirect(url_for("main.index"))
        return fn(*args, **kwargs)
    return inner

# Ruta del panel de super administrador
@main_bp.get("/super_adm_panel.html")
@require_roles("master_admin", "administrador")
#login_required
def super_adm_panel():
    form = LogoutForm()
    return render_template("super_adm_panel.html", form=form)

# Ruta de logout
@main_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("main.index"))

#REGISTRO DE VEHICULOS
@main_bp.route("/form_new_vehicle.html", methods=["GET", "POST"])
@login_required
@require_roles("master_admin", "administrador")
def form_new_vehicle():
    form = VehicleRegisterForm()
    try:
        from src.models.modeles import Persona, Rol, Conductor
        conductores_por_rol = (
            db.session.query(Persona)
            .join(Persona.roles)
            .filter(db.func.lower(Rol.nombre_rol) == "conductor")
            .all()
        )
        conductores_por_tabla = (
            db.session.query(Persona)
            .join(Conductor, Conductor.id_persona == Persona.id_persona)
            .all()
        )
        by_id = {str(p.id_persona): p for p in conductores_por_rol}
        for p in conductores_por_tabla:
            by_id.setdefault(str(p.id_persona), p)
        conductores = list(by_id.values())

        form.conductor_asignado.choices = [("__new__", "➕ Crear nuevo conductor…")] + [
            (str(p.id_persona), f"{p.nombre} {p.apellido_pat} {p.apellido_mat} • {p.rut}")
            for p in conductores
        ]
    except Exception:
        form.conductor_asignado.choices = [("__new__", "➕ Crear nuevo conductor…")]

    # Fallback simple para selects requeridos
    if not getattr(form.marca, "choices", None):
        form.marca.choices = [("otro", "Otro")]
    if not getattr(form.modelo, "choices", None):
        form.modelo.choices = [("generico", "Genérico")]
    if not getattr(form.tipo_vehiculo, "choices", None):
        form.tipo_vehiculo.choices = [("auto", "Automóvil")]

    if form.validate_on_submit():
        patente = (form.patente.data or "").strip().upper()
        id_interna = (form.id_interna.data or "").strip()
        marca = form.marca.data
        modelo = form.modelo.data
        anio = form.anio.data
        vin = (form.vin.data or "").strip().upper()
        tipo_vehiculo = form.tipo_vehiculo.data
        color = (form.color.data or "").strip()
        nombre_propietario = (form.nombre_propietario.data or "").strip()
        foto_vehiculo = form.foto_vehiculo.data
        conductor_sel = form.conductor_asignado.data

        # Si no existe o se elige crear nuevo, redirigir al registro de usuarios (conductor)
        if not conductor_sel or conductor_sel == "__new__":
            flash("Debes registrar primero al CONDUCTOR para asignarlo al vehículo.", "warning")
            return redirect(url_for("main.form_registro_usuarios") + "?prefill_role=conductor")

        # Buscar el conductor seleccionado por UUID
        try:
            from src.models.modeles import Persona, Conductor
            import uuid as _uuid
            conductor = db.session.query(Persona).get(_uuid.UUID(conductor_sel))
            if not conductor:
                flash("Conductor no encontrado. Regístralo e inténtalo nuevamente.", "danger")
                return render_template("form_new_vehicle.html", form=form)

            has_role = any(_norm_role(r.nombre_rol) == "conductor" for r in getattr(conductor, "roles", []))
            has_conductor_tabla = db.session.query(Conductor).get(conductor.id_persona) is not None
            if not (has_role or has_conductor_tabla):
                flash("La persona seleccionada no es un CONDUCTOR registrado.", "warning")
                return render_template("form_new_vehicle.html", form=form)
        except Exception as e:
            flash(f"Error validando conductor: {e}", "danger")
            return render_template("form_new_vehicle.html", form=form)

        # TODO: Guardar Automovil y enlazar propietario/conductor según tu modelo
        flash("Conductor validado. Continúa con el registro del vehículo.", "success")
        return render_template("form_new_vehicle.html", form=form)

    return render_template("form_new_vehicle.html", form=form)
    
    
    
    

# Ruta de registro de usuarios (solo admin)
@main_bp.route("/form_registro_usuarios.html", methods=["GET", "POST"])
@login_required
@require_roles("master_admin", "administrador")
def form_registro_usuarios():
    form = PersonaRegisterForm()

    # ---------------------------
    # Choices (Roles / País / Ciudad)
    # ---------------------------

    all_roles = Rol.query.order_by(Rol.nombre_rol.asc()).all()

    current_roles = set(session.get("roles", []))  # p.ej. {'master_admin'} o {'administrador'}
    # Normalización helper
    def norm(n: str) -> str:
        return _norm_role(n)  # normaliza 'Administrador' -> 'administrador', etc.

    if "master_admin" in current_roles:
        # Master Admin: acceso a todos los roles
        allowed_roles = all_roles
    elif "administrador" in current_roles:
        # Administrador: solo puede crear 'propietario' y 'conductor'
        allowed_keys = {"propietario", "conductor"}
        allowed_roles = [r for r in all_roles if norm(r.nombre_rol) in allowed_keys]
    else:
        # No debería entrar aquí por @require_roles, pero por seguridad:
        allowed_roles = []

    form.roles.choices = [("", "Seleccione un rol...")] + [(r.nombre_rol, r.nombre_rol) for r in allowed_roles]

    paises = Pais.query.order_by(Pais.nombre_pais.asc()).all()
    form.pais.choices = [("", "Seleccione un país...")] + [(str(p.id_pais), p.nombre_pais) for p in paises]

    id_pais_sel = request.form.get("pais") or form.pais.data
    if id_pais_sel:
        ciudades = (
            Ciudad.query
            .filter_by(id_pais=id_pais_sel)
            .order_by(Ciudad.nombre_ciudad.asc())
            .all()
        )
    else:
        ciudades = []
    form.ciudad.choices = [("", "Seleccione una ciudad...")] + [(str(c.id_ciudad), c.nombre_ciudad) for c in ciudades]

    # ---------------------------
    # Debug (sin llamar validate 2 veces)
    # ---------------------------
    is_valid = form.validate_on_submit()

    print("METHOD:", request.method)
    print("FILES:", list(request.files.keys()))
    if "foto" in request.files:
        print("FOTO filename:", request.files["foto"].filename)
    print("VALIDATE:", is_valid)
    print("FORM ERRORS:", form.errors)

    # ---------------------------
    # Submit
    # ---------------------------
    if is_valid:
        selected_roles = [form.roles.data]  # SelectField => string
        print("Roles seleccionados:", selected_roles)

        # Foto obligatoria
        if not form.foto.data or not getattr(form.foto.data, "filename", ""):
            flash("Debes adjuntar la foto.", "warning")
            return render_template("form_registro_usuarios.html", form=form)

        try:
            # 1) Subir FOTO (bucket: "foto")
            print("1) Subiendo foto...")
            foto_url = upload_to_bucket(form.foto.data, bucket="fotos")
            print("1.1) Foto subida:", foto_url)

            # 2) Subir archivos de conductor si corresponde
            lic_url, hoja_url = None, None
            is_conductor = any(r and r.strip().lower() == "conductor" for r in selected_roles)

            if is_conductor:
                if not form.licencia.data or not getattr(form.licencia.data, "filename", ""):
                    flash("Para CONDUCTOR adjunta licencia.", "warning")
                    return render_template("form_registro_usuarios.html", form=form)

                if not form.hoja_vida_conduct.data or not getattr(form.hoja_vida_conduct.data, "filename", ""):
                    flash("Para CONDUCTOR adjunta hoja de vida.", "warning")
                    return render_template("form_registro_usuarios.html", form=form)

                print("2) Subiendo licencia...")
                lic_url = upload_to_bucket(form.licencia.data, bucket="licencia")
                print("2.1) Licencia subida:", lic_url)

                print("3) Subiendo hoja de vida...")
                hoja_url = upload_to_bucket(form.hoja_vida_conduct.data, bucket="hoja_vida")
                print("3.1) Hoja de vida subida:", hoja_url)

            # 4) Datos para crear persona
            persona_data = {
                "nombre": form.nombre.data,
                "apellido_pat": form.apellido_pat.data,
                "apellido_mat": form.apellido_mat.data,
                "rut": form.rut.data,
                "email": form.email.data,
                "num_tele": form.num_tele.data,
                "fecha_nac": form.fecha_nac.data,
                "direccion": form.direccion.data,
                "id_pais": form.pais.data,
                "id_ciudad": form.ciudad.data,
                "foto": foto_url,
                "licencia": lic_url,
                "hoja_vida_conduct": hoja_url,
            }

            # 5) Crear persona + roles + tabla específica (esto lo hace tu service)
            print("4) Creando persona en DB...")
            persona = create_persona_role(persona_data, selected_roles)
            print("4.1) Persona creada:", persona.id_persona)

            # 6) Token set-password + email
            print("5) Creando token...")
            token = make_reset_token(persona.id_persona, persona.reset_nonce)

            link = request.url_root.rstrip("/") + url_for("main.set_password", token=token)
            print("5.1) Link completo:", link)

            print("6) Enviando correo...")
            send_set_password_email(persona.email, persona.nombre, link)
            print("6.1) Correo enviado.")

            flash("Usuario creado. Revisa tu correo para crear tu contraseña.", "success")
            return redirect(url_for("main.index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear usuario: {e}", "danger")

    return render_template("form_registro_usuarios.html", form=form)

# Ruta para establecer nueva contraseña desde email
@main_bp.route("/set-password/<token>", methods=["GET", "POST"])
def set_password(token):
    data = verify_reset_token(token, max_age_seconds=1800)  # 30 min
    if not data:
        flash("El enlace es inválido o expiró. Solicita uno nuevo.", "danger")
        return redirect(url_for("main.index"))

    persona = Persona.query.get(data["pid"])
    if not persona:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for("main.index"))

    # 1 uso: validar nonce
    if str(persona.reset_nonce) != data["nonce"]:
        flash("Este enlace ya fue usado o fue reemplazado por uno nuevo.", "warning")
        return redirect(url_for("main.index"))

    form = SetPasswordForm()

    is_valid = form.validate_on_submit()
    print("METHOD:", request.method)
    print("FORM ERRORS:", form.errors)
    print("VALIDATE:", is_valid)

    if is_valid:
        persona.password_hash = generate_password_hash(form.password.data)
        persona.must_change_password = False

        # invalidar token usado
        persona.reset_nonce = uuid.uuid4()

        db.session.commit()
        flash("Contraseña creada correctamente. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("main.index"))

    # ✅ siempre retornar template si no valida o es GET
    return render_template("set_password.html", form=form)

def roll_back(any):
    pass



@main_bp.get("/db-ping")
def db_ping():
    try:
        result = db.session.execute(db.text("SELECT 1 AS ok"))
        row = result.first()
        return {"db": "connected", "ok": row.ok}
    except Exception as e:
        return {"db": "error", "message": str(e)}, 500