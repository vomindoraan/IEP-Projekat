from flask_migrate import Migrate


MG = Migrate()


if __name__ == '__main__':
    from flask_migrate import init, migrate, upgrade
    from sqlalchemy_utils import create_database, database_exists

    from . import create_app
    from .models import DB, User


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

        if not User.query.filter(User.email == "admin@admin.com").first():
            admin = User(
                jmbg="0000000000000",
                email="admin@admin.com",
                password="1",
                forename="admin",
                surname="admin",
            )
            DB.session.add(admin)
            DB.session.commit()
