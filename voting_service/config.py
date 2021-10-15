from common.config import *


# Database config
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASS = os.getenv('DB_PASS', 'root')
DB_NAME = os.getenv('DB_NAME', 'vote')
SQLALCHEMY_DATABASE_URI = (
    f'mysql+pymysql://{DB_USER}:{DB_PASS}@'
    f'{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
)

# Redis config
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_VOTES_LIST = os.getenv('REDIS_VOTES_LIST', 'pending-votes')
