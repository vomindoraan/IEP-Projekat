from . import config, create_app

create_app().run(host=config.APP_HOST, port=config.APP_PORT)
