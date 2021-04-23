import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Notification(SqlAlchemyBase, UserMixin):
    __tablename__ = 'notifications'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    recipient_id = sqlalchemy.Column(sqlalchemy.Integer)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer)
    publication_id = sqlalchemy.Column(sqlalchemy.Integer)

    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
