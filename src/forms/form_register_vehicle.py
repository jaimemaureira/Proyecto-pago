from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class VehicleRegisterForm(FlaskForm):
    patente = StringField("Patente", validators=[DataRequired(), Length(max=30)])
    id_interna = StringField("ID Interna", validators=[DataRequired(), Length(max=6)])
    marca = SelectField("Marca", coerce=str, validators=[DataRequired()])
    modelo = SelectField("Modelo", coerce=str, validators=[DataRequired()])
    anio = DateField("Año", format="%Y", validators=[DataRequired()])
    vin = StringField("VIN", validators=[DataRequired(), Length(max=30)])
    tipo_vehiculo = SelectField("Tipo de vehículo", coerce=str, validators=[DataRequired()])
    color = StringField("Color", validators=[DataRequired(), Length(max=30)])
    nombre_propietario = StringField("Nombre del propietario", validators=[DataRequired(), Length(max=100)])
    foto_vehiculo = FileField("Foto", validators=[FileAllowed(["jpg","jpeg","png","pdf"])])
    conductor_asignado = SelectField("Conductor asignado", coerce=str, validators=[DataRequired()])