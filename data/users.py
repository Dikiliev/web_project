import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import json
import os


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_name = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')

    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    phone = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    other_data = None

    def __init__(self):
        if self.id is not None:
            self.load_data()

    def save_data(self):
        with open(f'static/user_data/additional_data/user_{self.id}.json', 'w') as file:
            if self.other_data is None:
                self.other_data = {
                    'followers': [],
                    'subscriptions': [],
                    'publications': [],
                    'likes': [],
                }

            json.dump(self.other_data, file)

    def load_data(self):
        if os.path.isfile(f'static/user_data/additional_data/user_{self.id}.json'):
            file = open(f'static/user_data/additional_data/user_{self.id}.json', 'r')
            self.other_data = json.load(file)
        else:
            self.save_data()

    def create_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
