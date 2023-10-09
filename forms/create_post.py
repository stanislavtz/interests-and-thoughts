from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Length


class CreatePost(FlaskForm):
    title = StringField("Blog Post Title", validators=[Length(min=4), DataRequired(message="This field is required")])
    subtitle = StringField("Subtitle", validators=[Length(min=8), DataRequired()])
    author_name = StringField("Your Name", validators=[Length(min=3), DataRequired()])
    img_url = StringField("Blog Image Url", validators=[URL(), DataRequired()])
    body_text = CKEditorField("Blog Comment:", validators=[DataRequired()])
    submit = SubmitField("Submit Post")
