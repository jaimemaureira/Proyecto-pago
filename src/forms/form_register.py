from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from src.utils.rut import RutValidator

class PersonaRegisterForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=30)])
    apellido_pat = StringField("Apellido paterno", validators=[DataRequired(), Length(max=50)])
    apellido_mat = StringField("Apellido materno", validators=[DataRequired(), Length(max=50)])
    rut = StringField("RUT", validators=[DataRequired(), Length(max=12), RutValidator(normalize=True)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    num_tele = StringField("Teléfono", validators=[DataRequired(), Length(max=20)])
    fecha_nac = DateField("Fecha nacimiento", validators=[DataRequired()], format="%Y-%m-%d")
    direccion = StringField("Dirección", validators=[DataRequired(), Length(max=300)])
    pais = SelectField("País", validators=[DataRequired(), Length(max=100)])
    ciudad = SelectField("Ciudad", validators=[DataRequired(), Length(max=100)])
    roles = SelectField("Rol", coerce=str, validators=[DataRequired()])

    foto = FileField("Foto", validators=[FileAllowed(["jpg","jpeg","png","pdf"]), FileRequired()])
    licencia = FileField("Licencia de conducir", validators=[FileAllowed(["jpg","jpeg","png","pdf"])])
    hoja_vida_conduct = FileField("Hoja de vida del conductor", validators=[FileAllowed(["jpg","jpeg","png","pdf"])])

    submit = SubmitField("Registrar")