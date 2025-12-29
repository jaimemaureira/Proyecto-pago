from ..extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Pais(db.Model):
    __tablename__ = "pais"

    id_pais = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_pais = db.Column(db.String(100), unique=True, nullable=False)

class Ciudad(db.Model):
    __tablename__ = "ciudad"

    id_ciudad = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_ciudad = db.Column(db.String(100), unique=True, nullable=False)
    id_pais = db.Column(UUID(as_uuid=True), db.ForeignKey("pais.id_pais", ondelete="CASCADE"), nullable=False)

class Persona(db.Model):
    __tablename__ = "persona"

    id_persona = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = db.Column(db.String(30), nullable=False)
    apellido_pat = db.Column(db.String(50), nullable=False)
    apellido_mat = db.Column(db.String(50), nullable=False)
    rut = db.Column(db.String(12), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    num_tele = db.Column(db.String(20), unique=True, nullable=False)
    fecha_nac = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(300), nullable=False)
    id_pais = db.Column(UUID(as_uuid=True), db.ForeignKey("pais.id_pais", ondelete="CASCADE"), nullable=False)
    id_ciudad = db.Column(UUID(as_uuid=True), db.ForeignKey("ciudad.id_ciudad", ondelete="CASCADE"), nullable=False)
    roles = db.relationship("Rol", secondary="persona_rol", back_populates="personas")   
    foto = db.Column(db.String(500), nullable=False)    
    password_hash = db.Column(db.String(255), nullable=False)
    must_change_password = db.Column(db.Boolean, nullable=False, default=True)
    reset_nonce = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4) 

    conductor = db.relationship("Conductor", back_populates="persona", uselist=False, cascade="all, delete-orphan")
    propietario = db.relationship("Propietario", back_populates="persona", uselist=False, cascade="all, delete-orphan")
    administrador = db.relationship("Administrador", back_populates="persona", uselist=False, cascade="all, delete-orphan")
    master_admin = db.relationship("MasterAdmin", back_populates="persona", uselist=False, cascade="all, delete-orphan")

class Rol(db.Model):
    __tablename__ = "rol"

    id_rol = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_rol = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(250), nullable=True)

    personas = db.relationship("Persona", secondary="persona_rol", back_populates="roles")


class PersonaRol(db.Model):
    __tablename__ = "persona_rol"
    id_perosnarol = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona", ondelete="CASCADE"), primary_key=True)
    id_rol = db.Column(UUID(as_uuid=True), db.ForeignKey("rol.id_rol", ondelete="CASCADE"), primary_key=True)


class Conductor(db.Model):
    __tablename__ = "conductor"

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona", ondelete="CASCADE"), primary_key=True)
    licencia = db.Column(db.String(500), unique=True, nullable=False)    
    hoja_vida_conduct = db.Column(db.String(500), nullable=False)
    anotaciones_internas = db.Column(db.String(2500), nullable=True)

    persona = db.relationship("Persona", back_populates="conductor")


class Propietario(db.Model):
    __tablename__ = "propietario"

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona", ondelete="CASCADE"), primary_key=True)
    
    persona = db.relationship("Persona", back_populates="propietario")


class Administrador(db.Model):
    __tablename__ = "administrador"

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona", ondelete="CASCADE"), primary_key=True)
    
    persona = db.relationship("Persona", back_populates="administrador")


class MasterAdmin(db.Model):
    __tablename__ = "master_admin"

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona", ondelete="CASCADE"), primary_key=True)
    
    persona = db.relationship("Persona", back_populates="master_admin")


class Automovil(db.Model):
    __tablename__ = "automovil"

    id_automovil = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_interna = db.Column(db.String(8), unique=True, nullable=False)
    patente = db.Column(db.String(8), unique=True, nullable=False)

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("propietario.id_persona"), nullable=False)

    vin = db.Column(db.String(25), unique=True, nullable=False)
    marca = db.Column(db.String(30), nullable=False)
    modelo = db.Column(db.String(30), nullable=False)
    tipo_vehiculo = db.Column(db.String(30), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(20), nullable=False)
    foto_automovil = db.Column(db.String(500), nullable=True)


class Turno(db.Model):
    __tablename__ = "turno"

    id_turno = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_automovil = db.Column(UUID(as_uuid=True), db.ForeignKey("automovil.id_automovil"), nullable=False)
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("conductor.id_persona"), nullable=False)

    fecha_ini = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(20), nullable=False)


class Documento(db.Model):
    __tablename__ = "documento"

    id_documento = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_automovil = db.Column(UUID(as_uuid=True), db.ForeignKey("automovil.id_automovil"), nullable=False)

    padron = db.Column(db.String(500), nullable=False)
    seguro_obligatorio = db.Column(db.String(500), nullable=False)
    revision_tec = db.Column(db.String(500), nullable=False)
    seguro_complementario = db.Column(db.String(500), nullable=True)
    permiso_circulacion = db.Column(db.String(500), nullable=False)
    cav = db.Column(db.String(500), nullable=False)
    cartola_recorrido = db.Column(db.String(500), nullable=False)

    fecha_vencimiento = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)


class Venta_guia(db.Model):
    __tablename__ = "venta_guia"

    id_guia = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_interna_desde = db.Column(db.Integer, nullable=False)
    id_interna_hasta = db.Column(db.Integer, nullable=False)
    valor_guia = db.Column(db.Integer, nullable=False)
    cantidad_guias = db.Column(db.Integer, nullable=False)
    total_venta = db.Column(db.Integer, nullable=False)

    fecha_venta = db.Column(db.DateTime, nullable=False)
    monto = db.Column(db.Float, nullable=False)

    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("propietario.id_persona"), nullable=False)
    guia_venta = db.Column(db.String(500), nullable=False)