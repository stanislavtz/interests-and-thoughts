from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, URL, Length, Email



class RegisterUser(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3)])
    email = EmailField(label="Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=32)])
    repeat_password = PasswordField("Repeat Password", validators=[DataRequired(), Length(min=6, max=32)])
    submit = SubmitField("Register")

