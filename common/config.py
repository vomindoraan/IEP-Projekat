import os
from datetime import timedelta

from common.utils import parse_bool


# Operation mode
ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = parse_bool(os.getenv('FLASK_DEBUG', True))

# JWT config
JWT_SECRET_KEY = 'JWT_SECRET_KEY'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Database config
SQLALCHEMY_TRACK_MODIFICATIONS = False
