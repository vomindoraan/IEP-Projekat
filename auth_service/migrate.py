import os

from flask_migrate import Migrate


MG = Migrate(directory=f'{os.path.dirname(__file__)}/migrations')


def main():
    from flask_migrate import init, migrate, upgrade
    from sqlalchemy_utils import create_database, database_exists

    from . import config, create_app
    from .models import DB, User


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

        if not User.query.filter_by(email='admin@admin.com').first():
            admin = User(
                jmbg='0000000000000',
                email='admin@admin.com',
                password='1',
                forename='admin',
                surname='admin',
                role='admin',
            )
            DB.session.add(admin)
            DB.session.commit()


if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception:
            pass
        else:
            break
