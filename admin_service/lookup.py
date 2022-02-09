if __name__ == '__main__':
    from admin_service.api import lookup_bp
    from . import config, create_app


    app = create_app()
    app.register_blueprint(lookup_bp)

    app.run(host=config.APP_HOST, port=config.APP_PORT)
