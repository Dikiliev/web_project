import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class Notification(SqlAlchemyBase, UserMixin):
    tablename = 'notifications'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer)
    recipient_id = sqlalchemy.Column(sqlalchemy.Integer)
    publication_id = sqlalchemy.Column(sqlalchemy.Integer)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
