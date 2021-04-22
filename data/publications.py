import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os
import json


class Publication(SqlAlchemyBase, UserMixin):
    __tablename__ = 'publications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)

    filename_photo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    other_data = None

    def __init__(self):
        if self.id is not None:
            self.load_data()

    def save_data(self):
        with open(f'static/user_data/additional_data/publication_{self.id}.json', 'w') as file:
            if self.other_data is None:
                self.other_data = {
                    'likes': [],
                    'comments': []
                }

            json.dump(self.other_data, file)

    def load_data(self):
        if os.path.isfile(f'static/user_data/additional_data/publication_{self.id}.json'):
            file = open(f'static/user_data/additional_data/publication_{self.id}.json', 'r')
            self.other_data = json.load(file)
        else:
            self.save_data()
