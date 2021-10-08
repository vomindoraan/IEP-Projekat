import os

from flask_migrate import Migrate


MG = Migrate(directory=f'{os.path.dirname(__file__)}/migrations')


if __name__ == '__main__':
    from flask_migrate import init, migrate, upgrade
    from sqlalchemy_utils import create_database, database_exists

    from . import create_app


    app = create_app()

    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context() as context:
        try:
            init()
        except SystemExit:
            pass

        try:
            migrate()
        except SystemExit:
            pass

        upgrade()
