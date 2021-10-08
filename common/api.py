from functools import wraps

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required
from flask_jwt_extended.exceptions import NoAuthorizationError
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException

from common.schemas import BaseSchema


# region Route middleware

def auth_jwt(*jwt_args, require_claims=False, admin=False, **jwt_kwargs):
    # TODO: Write docstring
    def decorator(handler):
        @wraps(handler)
        @jwt_required(*jwt_args, **jwt_kwargs)
        def wrapper(*args, **kwargs):
            jwt = get_jwt()

            missing_claims = any(
                k not in jwt for k in ('jmbg', 'forename', 'surname', 'role')
            )
            if require_claims and missing_claims:
                raise NoAuthorizationError("Bad Authorization Header")

            missing_admin_role = jwt.get('role') != 'admin'
            if admin and missing_admin_role:
                raise NoAuthorizationError("Missing Authorization Header")

            return handler(*args, **kwargs)

        return wrapper

    return decorator


def consumes(schema: BaseSchema):
    """Deserialize request data and inject it into the route handler.

    schema is a Schema object, e.g. an APIRequest.
    If applicable, @consumes should be specified right after the route
    declaration and before other route middleware or decorators.
    """
    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            params = {**request.values, **(request.json or {})}
            try:
                data = schema.load(params)
            except ValidationError as e:
                match e.messages:
                    case [message]:
                        raise BadRequest(message) from e
                    case struct:
                        raise BadRequest(struct) from e

            return handler(*args, **kwargs, data=data)

        wrapper.consumes = schema
        if hasattr(handler, 'produces'):
            wrapper.produces = handler.produces
            wrapper.status = handler.status

        return wrapper

    return decorator


def produces(schema: BaseSchema, status=200):
    """Serialize data returned by the handler and form a response body.

    schema is a Schema-like object that supports dumps operations, e.g.
    an APIResponse or the json module (good for returning flat lists
    and quick prototyping).
    @produces should be specified right after the route declaration and
    before other route middleware or decorators, except for @consumes.
    """
    def decorator(handler):
        @wraps(handler)
        def wrapper(*args, **kwargs):
            body = handler(*args, **kwargs)
            return schema.jsonify(body), status

        wrapper.produces = schema
        wrapper.status = status
        if hasattr(handler, 'consumes'):
            wrapper.consumes = handler.consumes

        return wrapper

    return decorator

# endregion


common_bp = Blueprint('common', __name__)


@common_bp.app_errorhandler(HTTPException)
def handle_http_exception(e: HTTPException):
    return {'message': e.description}, e.code
