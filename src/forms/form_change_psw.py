from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class recoveryPassword(FlaskForm):
    email=StringField('Email', validators=[DataRequired(), Email()])
    submit=SubmitField('Request Password Reset')