from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import create_database, database_exists


MG = Migrate()


if __name__ == '__main__':
    from . import create_app, models

    app = create_app()

    if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
        create_database(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context() as context:
        init()
        migrate(message="Production migration")
        upgrade()

        admin = models.User(
            jmbg="0000000000000",
            email="admin@admin.com",
            password="1",
            forename="admin",
            surname="admin",
        )
        models.DB.session.add(admin)
        models.DB.session.commit()
