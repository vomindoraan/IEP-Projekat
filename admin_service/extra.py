if __name__ == '__main__':
    from .api import extra_bp
    from . import config, create_app


    app = create_app()
    app.register_blueprint(extra_bp)

    app.run(host=config.APP_HOST, port=config.APP_PORT)
