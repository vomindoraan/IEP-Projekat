import csv
import io
from uuid import UUID

import redis

from common.api import *
from . import config, schemas


service_bp = Blueprint('voting', __name__)


@service_bp.post('/vote')
@auth_jwt()
@produces(schemas.EmptyResponse.ONE)
def vote():
    try:
        f = request.files['file']
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        csv_in = csv.reader(stream)
    except KeyError as e:
        raise BadRequest("Field file missing.") from e
    except UnicodeDecodeError as e:
        raise BadRequest("Bad file encoding.") from e

    # Check and gather ballot data
    content = []
    for i, values in enumerate(csv_in):
        if len(values) != 2:
            raise BadRequest(f"Incorrect number of values on line {i}.")

        try:
            ballot_uuid = UUID(values[0])
        except ValueError as e:
            raise BadRequest(f"Incorrect ballot ID on line {i}.") from e

        error = BadRequest(f"Incorrect poll number on line {i}.")
        try:
            poll_number = int(values[1])
            if poll_number <= 0:
                raise error
        except ValueError as e:
            raise error from e

        content.append((ballot_uuid, poll_number))

    # Publish ballot data to Redis
    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    for values in content:
        r.publish(config.REDIS_VOTES_LIST, ' '.join(map(str, values)))
        # raise ServiceUnavailable("Voting service temporarily unavailable.",
        #                          retry_after=config.RETRY_DELAY)
