from common.config import *


# Server config
HOST = os.getenv('USER_SERVICE_HOST', '0.0.0.0')
PORT = int(os.getenv('USER_SERVICE_PORT', 9000))
SERVER_NAME = f'{HOST}:{PORT}'

# Database config
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'root')
DB_NAME = os.getenv('DB_NAME', 'auth')
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4'