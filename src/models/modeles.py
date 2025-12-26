from ..extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Persona(db.Model):
    id_persona = db.Column(UUID(as_uuid=True), primary_key=True)
    nombre = db.Column(db.VARCHAR(30), nullable=False)
    apellido_pat = db.Column(db.VARCHAR(50), nullable=False)
    apellido_mat = db.Column(db.VARCHAR(50), nullable=False)
    rut = db.Column(db.VARCHAR(12), unique=True, nullable=False)
    email = db.Column(db.VARCHAR(150), unique=True, nullable=False)
    num_tele = db.Column(db.VARCHAR(20), unique=True, nullable=False)
    fecha_nac = db.Column(db.DATE, nullable=False)
    direccion = db.Column(db.VARCHAR(300), nullable=False)
    
class Conductor(db.Model):
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona"), primary_key=True)
    licencia = db.Column(db.VARCHAR(500), unique=True, nullable=False)  # Almacenar la licencia como una URL o ruta al archivo
    foto = db.Column(db.VARCHAR(500), nullable=False) # Almacenar la foto como una URL o ruta al archivo
    hoja_vida_conduct = db.Column(db.VARCHAR(500), nullable=False) # Almacenar la hoja de vida como una URL o ruta al archivo
    anotaciones_internas = db.Column(db.VARCHAR(2500), nullable=True) # Campo para anotaciones internas
    

class Propietario(db.Model):
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("persona.id_persona"), primary_key=True)
    foto = db.Column(db.VARCHAR(500), nullable=True)

class Automovil(db.Model):
    id_automovil = db.Column(UUID(as_uuid=True), primary_key=True)
    id_interna = db.Column(db.VARCHAR(8), unique=True, nullable=False)
    patente = db.Column(db.VARCHAR(8), unique=True, nullable=False)
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("propietario.id_persona"), nullable=False)
    vin = db.Column(db.VARCHAR(25), unique=True, nullable=False)
    marca = db.Column(db.VARCHAR(30), nullable=False)
    modelo = db.Column(db.VARCHAR(30), nullable=False)
    tipo_vehiculo = db.Column(db.VARCHAR(30), nullable=False)
    anio = db.Column(db.INTEGER, nullable=False)
    color = db.Column(db.VARCHAR(20), nullable=False)
    foto = db.Column(db.VARCHAR(500), nullable=True) # Almacenar la foto como una URL o ruta al archivo
    
class Turno(db.Model):
    id_turno = db.Column(UUID(as_uuid=True), primary_key=True)
    id_automovil = db.Column(UUID(as_uuid=True), db.ForeignKey("automovil.id_automovil"), nullable=False)
    id_persona= db.Column(UUID(as_uuid=True), db.ForeignKey("conductor.id_persona"), nullable=False)
    fecha_ini = db.Column(db.TIMESTAMP, nullable=False)
    fecha_fin = db.Column(db.TIMESTAMP, nullable=False)    
    estado = db.Column(db.VARCHAR(20), nullable=False)  # e.g., "activo", "no activo"
    
class Documento(db.Model):
    id_documento = db.Column(UUID(as_uuid=True), primary_key=True)
    id_automovil = db.Column(UUID(as_uuid=True), db.ForeignKey("automovil.id_automovil"), nullable=False)
    padron = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar el padrón como una URL o ruta al archivo
    seguro_obligatorio = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar
    revision_tec = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar
    seguro_complementario = db.Column(db.VARCHAR(500), nullable=True)  # Almacenar
    permiso_circulacion = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar
    cav = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar
    cartola_recorrido = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar
    fecha_vencimiento = db.Column(db.DATE, nullable=False)
    estado = db.Column(db.VARCHAR(20), nullable=False)  # e.g., "al día", "vencido"
    
class Venta_guia(db.Model):
    id_guia = db.Column(UUID(as_uuid=True), primary_key=True)
    id_interna_desde = db.Column(db.INTEGER, nullable=False) #es el correlativo de las guias, en el caso que se compren muchas
    id_interna_hasta = db.Column(db.INTEGER, nullable=False)#guias se utiliza el hasta que es el final correlativo de la ulyima guia
    valor_guia = db.Column(db.INTEGER, nullable=False)
    cantidad_guias = db.Column(db.INTEGER, nullable=False)
    total_venta = db.Column(db.INTEGER, nullable=False)
    fecha_venta = db.Column(db.TIMESTAMP, nullable=False)
    id_persona = db.Column(UUID(as_uuid=True), db.ForeignKey("propietario.id_persona"), nullable=False)
    fecha_venta = db.Column(db.TIMESTAMP, nullable=False)
    monto = db.Column(db.FLOAT, nullable=False)
    guia_venta = db.Column(db.VARCHAR(500), nullable=False)  # Almacenar la guía de venta como una URL o ruta al archivo
    