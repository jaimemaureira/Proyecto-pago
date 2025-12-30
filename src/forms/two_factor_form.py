from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class TwoFactorForm(FlaskForm):
    code = StringField(
        "Código de verificación",
        validators=[
            DataRequired(message="Ingresa el código"),
            Length(min=4, max=8, message="Código inválido"),
            Regexp(r"^\d{4,8}$", message="Debe ser numérico")
        ],
        render_kw={"inputmode": "numeric", "autocomplete": "one-time-code"}
    )
    submit = SubmitField("Verificar")
