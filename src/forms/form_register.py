from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class PersonaRegisterForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired(), Length(max=30)])
    apellido_pat = StringField("Apellido paterno", validators=[DataRequired(), Length(max=50)])
    apellido_mat = StringField("Apellido materno", validators=[DataRequired(), Length(max=50)])
    rut = StringField("RUT", validators=[DataRequired(), Length(max=12)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    num_tele = StringField("Teléfono", validators=[DataRequired(), Length(max=20)])
    fecha_nac = DateField("Fecha nacimiento", validators=[DataRequired()], format="%Y-%m-%d")
    direccion = StringField("Dirección", validators=[DataRequired(), Length(max=300)])
    foto = StringField("Foto (URL)", validators=[DataRequired(), Length(max=500)])

    # choices se cargan desde DB en la ruta
    roles = SelectMultipleField("Roles", coerce=str, validators=[DataRequired()])

    # campos extra (solo si eliges CONDUCTOR)
    licencia = StringField("Licencia (URL)", validators=[Length(max=500)])
    hoja_vida_conduct = StringField("Hoja de vida (URL)", validators=[Length(max=500)])

    submit = SubmitField("Registrar")