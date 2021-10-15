from flask import Flask
from flask_jwt_extended import JWTManager

from . import config


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile(config.__file__)

    JWTManager(app)

    from . import api
    app.register_blueprint(api.common_bp)
    app.register_blueprint(api.service_bp)

    return app
