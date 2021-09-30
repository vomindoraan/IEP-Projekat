from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt, get_jwt_identity,
    jwt_required,
)
from sqlalchemy import and_
from werkzeug.exceptions import Conflict, NotFound, Unauthorized

from common.api import *
from . import schemas
from .models import DB, User


service_bp = Blueprint('users', __name__)


@service_bp.post('/register')
@consumes(schemas.UserRegistration.ONE)
@produces(schemas.EmptyResponse.ONE)
def register_user(data):
    if User.query.filter(User.email == data['email']).first():
        raise Conflict("Email already exists.")

    user = User(**data)
    DB.session.add(user)
    DB.session.commit()


@service_bp.post('/login')
@consumes(schemas.UserLogin.ONE)
@produces(schemas.TokenPair.ONE)
def login_user(data):
    user = User.query.filter(
        and_(User.email == data['email'], User.password == data['password'])
    ).first()
    if not user:
        raise Unauthorized("Invalid credentials.")

    ac = {
        'forename': user.forename,
        'surname':  user.surname,
        'is_admin': user.is_admin,
    }
    return {
        'access_token': create_access_token(identity=user.email, additional_claims=ac),
        'refresh_token': create_refresh_token(identity=user.email, additional_claims=ac),
    }


@service_bp.post('/refresh')
@produces(schemas.AccessToken.ONE)
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    claims = get_jwt()
    return {
        'access_token': create_access_token(identity=identity, additional_claims=claims),
    }


@service_bp.post('/delete')
@consumes(schemas.UserDeletion.ONE)
@produces(schemas.EmptyResponse.ONE)
@jwt_required()
def delete_user(data):
    user = User.query.filter(User.email == data['email']).first()
    if not user:
        raise NotFound("Unknown user.")

    DB.session.delete(user)
    DB.session.commit()
