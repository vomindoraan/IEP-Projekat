from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import EmailType, PasswordType


DB = SQLAlchemy()


class User(DB.Model):
    __tablename__ = 'users'

    id = DB.Column(DB.Integer, primary_key=True)
    jmbg = DB.Column(DB.String(256), nullable=False)
    email = DB.Column(EmailType(length=256), nullable=False, unique=True)
    password = DB.Column(PasswordType(max_length=256, schemes=['pbkdf2_sha512']),
                         nullable=False)
    forename = DB.Column(DB.String(256), nullable=False)
    surname = DB.Column(DB.String(256), nullable=False)
    role = DB.Column(DB.String(16), nullable=False, default='user')
