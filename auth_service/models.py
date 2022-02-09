from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy_utils.types.password import PasswordType


DB = SQLAlchemy()


class User(DB.Model):
    __tablename__ = 'users'

    id = DB.Column(DB.Integer, primary_key=True)
    jmbg = DB.Column(DB.String(256), nullable=False)
    email = DB.Column(DB.String(256), nullable=False, unique=True)
    # password = DB.Column(PasswordType(schemes=['pbkdf2_sha512']), nullable=False)
    password = DB.Column(DB.String(256), nullable=False)  # TODO: Properly store passwords
    forename = DB.Column(DB.String(256), nullable=False)
    surname = DB.Column(DB.String(256), nullable=False)
    role = DB.Column(DB.String(16), nullable=False, default='user')
