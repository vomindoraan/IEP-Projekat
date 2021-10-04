import csv
import io

import redis
from flask_jwt_extended import jwt_required

from common.api import *
from . import config


service_bp = Blueprint('voting', __name__)


@service_bp.post('/vote')
@jwt_required()
@produces(schemas.EmptyResponse.ONE)
def vote():
    try:
        f = request.files['file']
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        csv_in = csv.reader(stream)
    except Exception:
        return BadRequest("Field file missing.")

    content = []
    for i, values in enumerate(csv_in):
        if len(values) != 2:
            return BadRequest(f"Incorrect number of values on line {i}.")
        content.append(values)

    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    for values in content:
        r.publish(config.REDIS_VOTES_LIST, ' '.join(values))
