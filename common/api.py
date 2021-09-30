from functools import wraps

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException

from common import schemas


# region Route middleware

def consumes(schema: schemas.Base):
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
                raise BadRequest(description=e.messages) from e

            return handler(*args, **kwargs, data=data)

        wrapper.consumes = schema
        if hasattr(handler, 'produces'):
            wrapper.produces = handler.produces
            wrapper.status = handler.status

        return wrapper

    return decorator


def produces(schema: schemas.Base, status=200):
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
            return jsonify(schema.load(body)), status

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
