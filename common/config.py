import os
from datetime import timedelta
from zoneinfo import ZoneInfo

import tzlocal

from common.utils import parse_bool


# Operation mode
ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = parse_bool(os.getenv('FLASK_DEBUG', True))
COLLAPSE_ERROR_MESSAGES = parse_bool(os.getenv('COLLAPSE_ERROR_MESSAGES', True))

# Server config
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 9000))
SERVER_NAME = f'{SERVER_HOST}:{SERVER_PORT}'
TIMEZONE = ZoneInfo(os.getenv('TIMEZONE', tzlocal.get_localzone().key))

# JWT config
JWT_SECRET_KEY = '13С113ИЕП'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# Database config
SQLALCHEMY_TRACK_MODIFICATIONS = False
