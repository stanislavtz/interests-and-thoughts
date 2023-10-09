from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginUser(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=32)])
    submit = SubmitField("Log in")
