from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired


class Button(FlaskForm):
    submit = SubmitField('', validators=[DataRequired()])
