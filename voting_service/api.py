import csv
import io

import redis
from flask import request
from flask_jwt_extended import jwt_required

from common.api import *
from . import config


service_bp = Blueprint('voting', __name__)


@service_bp.post('/vote')
@jwt_required()
def vote():
    try:
        f = request.files['file']
        stream = io.StringIO(f.stream.read().decode('utf-8'))
        csv_in = csv.reader(stream)
    except Exception as e:
        return BadRequest("Field file missing.")

    content = []
    for i, line in enumerate(csv_in):
        if len(line.split()) != 2:
            return BadRequest(f"Incorrect number of values on line {i}.")
        content.append(line)

    r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    pubsub = r.pubsub()
    for line in content:
        pubsub.publish(config.REDIS_VOTES_LIST, line)
