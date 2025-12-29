from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class SetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contraseña", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField("Confirmar", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Guardar contraseña")