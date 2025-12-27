from src.services.psw_generator import generate_password
from src.models import *
from src.extensions import db
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

def _norm_role(name: str) -> str:
    # "Master Admin" -> "MASTER_ADMIN"
    return name.strip().upper().replace(" ", "_")

ROLE_TABLE = {
    "PROPIETARIO": Propietario,
    "CONDUCTOR": Conductor,
    "ADMINISTRADOR": Administrador,
    "MASTER_ADMIN": MasterAdmin,
}

def create_persona_role(persona_data: dict, role_names: list[str]):
    required_fields = [
        "nombre","apellido_pat","apellido_mat","rut","email",
        "num_tele","fecha_nac","direccion","foto"
    ]
    for f in required_fields:
        if persona_data.get(f) in (None, ""):
            raise ValueError(f"Falta el campo requerido de persona: {f}")

    if not role_names:
        raise ValueError("Debe proporcionar al menos un rol para la persona.")

    # normaliza roles
    role_keys = [_norm_role(r) for r in role_names]

    try:
        # ✅ password automático
        plain_password = generate_password(16)        
        pwd_hash = generate_password_hash(plain_password)

        # 1) crear persona
        persona = Persona(
            nombre=persona_data["nombre"],
            apellido_pat=persona_data["apellido_pat"],
            apellido_mat=persona_data["apellido_mat"],
            rut=persona_data["rut"],
            email=persona_data["email"],
            num_tele=persona_data["num_tele"],
            fecha_nac=persona_data["fecha_nac"],
            direccion=persona_data["direccion"],
            foto=persona_data["foto"],
            password_hash=pwd_hash,
            must_change_password=True,
        )
        db.session.add(persona)
        db.session.flush()  # para obtener persona.id_persona    
        

        # 2) buscar roles (NO crearlos acá)
        roles = Rol.query.filter(Rol.nombre_rol.in_(role_keys)).all()
        encontrados = { _norm_role(r.nombre_rol) for r in roles }
        faltan = [rk for rk in set(role_keys) if rk not in encontrados]
        if faltan:
            raise ValueError(f"Estos roles no existen en tabla rol: {faltan}")

        # 3) asignar roles + crear tablas específicas (1:1)
        for rol_obj in roles:
            persona.roles.append(rol_obj)

            key = _norm_role(rol_obj.nombre_rol)
            Model = ROLE_TABLE.get(key)
            if not Model:
                continue

            # si ya existe fila especializada, no duplicar
            if Model.query.get(persona.id_persona) is not None:
                continue

            if Model is Conductor:
                # conductor necesita campos extra
                missing = [k for k in ["licencia", "hoja_vida_conduct"] if persona_data.get(k) in (None, "")]
                if missing:
                    raise ValueError(f"Faltan campos requeridos para Conductor: {', '.join(missing)}")

                db.session.add(Conductor(
                    id_persona=persona.id_persona,
                    licencia=persona_data["licencia"],                    
                    hoja_vida_conduct=persona_data["hoja_vida_conduct"],
                    
                ))
            else:
                # Propietario / Administrador / MasterAdmin
                db.session.add(Model(
                    id_persona=persona.id_persona,
                    
                ))

        db.session.commit()

        # ✅ devolvemos password en texto SOLO una vez
        return persona, plain_password

    except IntegrityError as e:
        db.session.rollback()
        raise ValueError(f"Error de integridad (rut/email/num_tele duplicado): {str(e)}")
    except Exception:
        db.session.rollback()
        raise