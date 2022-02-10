import os

from flask_migrate import Migrate


MG = Migrate(directory=f'{os.path.dirname(__file__)}/migrations')


def main():
    from flask_migrate import init, migrate, upgrade
    from sqlalchemy_utils import create_database, database_exists

    from . import config, create_app


    app = create_app()

    if not database_exists(config.SQLALCHEMY_DATABASE_URI):
        create_database(config.SQLALCHEMY_DATABASE_URI)

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


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            e.print_exc()
        else:
            break
