from flask import Flask

from . import config


def create_app(config_file=config.__file__):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)

    from . import auth
    auth.JWT.init_app(app)

    from . import models
    models.DB.init_app(app)

    from . import migrate
    migrate.MG.init_app(app, models.DB)

    from . import schemas
    schemas.MM.init_app(app)

    from . import api
    app.register_blueprint(api.common_bp)
    app.register_blueprint(api.service_bp)

    return app
