from common.config import *


# Business logic config
ELECTIONS_TOTAL_SEATS = int(os.getenv('ELECTIONS_TOTAL_SEATS', 250))
ELECTIONS_THRESHOLD_PCT = int(os.getenv('ELECTIONS_THRESHOLD_PCT', 5))

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
