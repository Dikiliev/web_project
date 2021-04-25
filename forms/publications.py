from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField


class ShowPublicationForm(FlaskForm):
    like_submit = SubmitField(' ', validators=[DataRequired()])


class AddPublicationForm(FlaskForm):
    submit_cancel = SubmitField('Отмена', validators=[DataRequired()])
    file = FileField('Выберите фотографию', validators=[FileAllowed(['jpg', 'png'], 'Images only!'), DataRequired()])
    submit_view = SubmitField('Посмотреть', validators=[DataRequired()])

    about = TextAreaField('Описание:', validators=[DataRequired()])

    submit = SubmitField('Опубликовать', validators=[DataRequired()])


class EditPublicationForm(FlaskForm):
    about = TextAreaField('Описание:', validators=[DataRequired()])
    submit = SubmitField('Сохранить', validators=[DataRequired()])
    submit_delete = SubmitField('Удалить публикацию', validators=[DataRequired()])
