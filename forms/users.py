from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField, FileField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Optional


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    full_name = StringField('Имя и Фамилия', validators=[DataRequired()])
    about = TextAreaField('О себе', validators=[DataRequired()])

    email = EmailField('Почта', validators=[DataRequired()])

    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    name_or_email = StringField('Имя пользователя или почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditProfileForm(FlaskForm):
    file = FileField('Загрузить фотографию')

    name = StringField('Имя пользователя', validators=[DataRequired()])
    full_name = StringField('Имя и Фамилия', validators=[DataRequired()])
    about = TextAreaField('О себе', validators=[DataRequired()])

    email = EmailField('Почта', validators=[DataRequired()])
    phone = StringField('Номер телефона', default='+7 ')

    submit = SubmitField('Сохранить')


class ProfileForm(FlaskForm):
    submit_sub = SubmitField('Подписатся')
