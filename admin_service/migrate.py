from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import create_database, database_exists


MG = Migrate()


if __name__ == '__main__':
    from . import create_app

    app = create_app()

    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context() as context:
        try:
            init()
        except SystemExit:
            pass

        migrate(message="Production migration")
        upgrade()
