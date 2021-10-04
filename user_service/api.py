from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt, get_jwt_identity,
    jwt_required,
)
from sqlalchemy import and_

from common.api import *
from . import schemas
from .models import DB, User


service_bp = Blueprint('users', __name__)


@service_bp.post('/register')
@consumes(schemas.UserRegistration.ONE)
@produces(schemas.EmptyResponse.ONE)
def register_user(data):
    if DB.session.query(User).filter(User.email == data['email']).first():
        raise BadRequest("Email already exists.")

    user = User(**data)
    DB.session.add(user)
    DB.session.commit()


@service_bp.post('/login')
@consumes(schemas.UserLogin.ONE)
@produces(schemas.TokenPair.ONE)
def login_user(data):
    user = DB.session.query(User).filter(
        and_(User.email == data['email'], User.password == data['password'])
    ).first()
    if not user:
        raise BadRequest("Invalid credentials.")

    ac = {
        'jmbg':     user.jmbg,
        'forename': user.forename,
        'surname':  user.surname,
        'roles':    'admin' if user.is_admin else None,
    }
    return {
        'access_token': create_access_token(identity=user.email, additional_claims=ac),
        'refresh_token': create_refresh_token(identity=user.email, additional_claims=ac),
    }


@service_bp.post('/refresh')
@jwt_required(refresh=True)
@produces(schemas.AccessToken.ONE)
def refresh_token():
    identity = get_jwt_identity()
    claims = get_jwt()

    ac = {
        'jmbg':     claims['jmbg'],
        'forename': claims['forename'],
        'surname':  claims['surname'],
        'roles':    claims['roles'],
    }
    return {
        'access_token': create_access_token(identity=identity, additional_claims=ac),
    }


@service_bp.post('/delete')
@jwt_required()
@consumes(schemas.UserDeletion.ONE)
@produces(schemas.EmptyResponse.ONE)
def delete_user(data):
    user = DB.session.query(User).filter(User.email == data['email']).first()
    if not user:
        raise BadRequest("Unknown user.")

    DB.session.delete(user)
    DB.session.commit()
