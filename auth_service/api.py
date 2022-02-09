from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity,
)
from sqlalchemy import and_

from common.api import *
from . import schemas
from .models import DB, User


service_bp = Blueprint('auth', __name__)


@service_bp.post('/register')
@consumes(schemas.UserRegistration.ONE)
@produces(schemas.EmptyResponse.ONE)
def register_user(data):
    if User.query.filter(User.email == data['email']).first():
        raise BadRequest("Email already exists.")

    user = User(**data)
    DB.session.add(user)
    DB.session.commit()


@service_bp.post('/login')
@consumes(schemas.UserLogin.ONE)
@produces(schemas.TokenPair.ONE)
def login_user(data):
    user = (
        User.query
        .filter(and_(User.email == data['email'],
                     User.password == data['password']))
        .first()
    )
    if not user:
        raise BadRequest("Invalid credentials.")

    claims = {
        'jmbg':     user.jmbg,
        'forename': user.forename,
        'surname':  user.surname,
        'role':     user.role,
    }
    return {
        'access_token': create_access_token(identity=user.email,
                                            additional_claims=claims),
        'refresh_token': create_refresh_token(identity=user.email,
                                              additional_claims=claims),
    }


@service_bp.post('/refresh')
@auth_jwt(require_claims=True, refresh=True)
@produces(schemas.AccessToken.ONE)
def refresh_token():
    identity = get_jwt_identity()
    jwt = get_jwt()
    claims = {
        'jmbg':     jwt['jmbg'],
        'forename': jwt['forename'],
        'surname':  jwt['surname'],
        'role':     jwt['role'],
    }
    return {
        'access_token': create_access_token(identity=identity,
                                            additional_claims=claims),
    }


@service_bp.post('/delete')
@auth_jwt(admin=True)
@consumes(schemas.UserDeletion.ONE)
@produces(schemas.EmptyResponse.ONE)
def delete_user(data):
    user = User.query.filter(User.email == data['email']).first()
    if not user:
        raise BadRequest("Unknown user.")

    DB.session.delete(user)
    DB.session.commit()
