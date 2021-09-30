from common.config import *


# Redis config
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_VOTES_LIST = os.getenv('REDIS_VOTES_LIST', 'pending-votes')
