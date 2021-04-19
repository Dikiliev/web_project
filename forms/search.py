from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    name = StringField('Введите имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Найти', validators=[DataRequired()])
