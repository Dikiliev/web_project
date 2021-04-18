from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class AddPublicationForm(FlaskForm):
    file = FileField('Выберите фотографию', validators=[DataRequired()])
    submit_view = SubmitField('Посмотреть', validators=[DataRequired()])
    about = TextAreaField('Описание:', validators=[DataRequired()])

    submit = SubmitField('Опубликовать', validators=[DataRequired()])
