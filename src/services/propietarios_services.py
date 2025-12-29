import uuid
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.extensions import db
from src.models import Persona, Rol, Propietario, Conductor, Administrador, MasterAdmin


def _norm_role(name: str) -> str:
    # "Master Admin" -> "master_admin"
    return (name or "").strip().lower().replace(" ", "_")


ROLE_TABLE = {
    "propietario": Propietario,
    "conductor": Conductor,
    "administrador": Administrador,
    "master_admin": MasterAdmin,
}


def create_persona_role(persona_data: dict, role_names: list[str]) -> Persona:
    required_fields = [
        "nombre", "apellido_pat", "apellido_mat", "rut", "email",
        "num_tele", "fecha_nac", "direccion", "foto", "id_pais", "id_ciudad"
    ]
    for f in required_fields:
        if persona_data.get(f) in (None, ""):
            raise ValueError(f"Falta el campo requerido de persona: {f}")

    if not role_names:
        raise ValueError("Debe proporcionar al menos un rol para la persona.")

    try:
        # 1) Crear persona
        persona = Persona(
            nombre=persona_data["nombre"],
            apellido_pat=persona_data["apellido_pat"],
            apellido_mat=persona_data["apellido_mat"],
            rut=persona_data["rut"],
            email=persona_data["email"],
            num_tele=persona_data["num_tele"],
            fecha_nac=persona_data["fecha_nac"],
            direccion=persona_data["direccion"],
            id_pais=persona_data["id_pais"],
            id_ciudad=persona_data["id_ciudad"],
            foto=persona_data["foto"],
            password_hash=generate_password_hash(str(uuid.uuid4())),  # hash random temporal
            must_change_password=True,
        )
        db.session.add(persona)
        db.session.flush()  # ya tienes persona.id_persona

        # 2) Buscar roles por NOMBRE REAL (tal como viene del select)
        roles = Rol.query.filter(Rol.nombre_rol.in_(role_names)).all()

        encontrados = {_norm_role(r.nombre_rol) for r in roles}
        esperados = {_norm_role(rn) for rn in role_names}
        faltan = sorted(list(esperados - encontrados))
        if faltan:
            raise ValueError(f"Estos roles no existen en tabla rol: {faltan}")

        # 3) Asignar roles + crear fila en tabla específica (si aplica)
        for rol_obj in roles:
            persona.roles.append(rol_obj)

            key = _norm_role(rol_obj.nombre_rol)
            Model = ROLE_TABLE.get(key)
            if not Model:
                continue

            # Evitar duplicados
            if Model.query.get(persona.id_persona) is not None:
                continue

            if Model is Conductor:
                missing = [k for k in ["licencia", "hoja_vida_conduct"] if persona_data.get(k) in (None, "")]
                if missing:
                    raise ValueError(f"Faltan campos requeridos para Conductor: {', '.join(missing)}")

                db.session.add(Conductor(
                    id_persona=persona.id_persona,
                    licencia=persona_data["licencia"],
                    hoja_vida_conduct=persona_data["hoja_vida_conduct"],
                    # si tu tabla Conductor exige foto, usa la misma:
                    foto=persona_data["foto"],
                ))
            else:
                db.session.add(Model(id_persona=persona.id_persona))

        db.session.commit()
        return persona

    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad (rut/email/num_tele duplicado): {str(e)}")

    except Exception:
        db.session.rollback()
        raise