from datetime import datetime

from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest

from common.api import *
from . import schemas
from .models import DB, Participant, Election, Vote


service_bp = Blueprint('admin', __name__)


@service_bp.post('/createParticipant')
@jwt_required()
@consumes(schemas.ParticipantCreation.ONE)
@produces(schemas.CreatedParticipant.ONE)
def create_participant(data):
    participant = Participant(**data)
    DB.session.add(participant)
    DB.session.commit()
    return participant


@service_bp.get('/getParticipants')
@jwt_required()
@produces(schemas.Participants.ONE)  # TODO: Replace with envelope
def get_participants():
    return {
        'participants': DB.session.query(Participant).all(),
    }


@service_bp.post('/createElection')
@jwt_required()
@consumes(schemas.ElectionCreation.ONE)
@produces(schemas.PollNumbers.ONE)
def create_election(data):
    # TODO: Check dates

    participant_ids = data['participants']
    if len(participant_ids) < 2:
        raise BadRequest("Invalid participants.")

    participants = []
    poll_numbers = []
    for i, pid in enumerate(participant_ids, start=1):
        p = DB.session.query(Participant).get(pid)
        if not p or data['individual'] != p.individual:
            raise BadRequest("Invalid participants.")

        p.poll_number = i
        participants.append(p)
        poll_numbers.append(i)

    data['participants'] = participants
    election = Election(**data)
    DB.session.add(election)
    DB.session.commit()

    return {
        'poll_numbers': poll_numbers
    }


@service_bp.get('/getElections')
@jwt_required()
@produces(schemas.Elections.ONE)  # TODO: Replace with envelope
def get_elections():
    return {
        'elections': DB.session.query(Election).all(),
    }


@service_bp.get('/getResults')
@jwt_required()
@consumes(schemas.ResultsQuery.ONE)
@produces(schemas.Results.ONE)
def get_results(data):
    eid = data['election_id']
    e = DB.session.query(Election).get(eid)
    if not e:
        raise BadRequest(f"Election does not exist.")
    if e.end > datetime.now(tz=e.end.tzinfo):
        raise BadRequest(f"Election is ongoing.")

    # for p in DB.session.query(Participant).filter(Participant.election_id == eid):


    invalid_votes = DB.session.query(Vote).filter(Vote.invalid is not None)

    return {
        'invalid_votes': invalid_votes,
    }


lookup_bp = Blueprint('lookup', __name__)

@lookup_bp.get('/lookup')
@jwt_required()
@consumes(schemas.LookupQuery.ONE)
@produces(schemas.Election.MANY)
def lookup(data):
    return (
        DB.session
        .query(Election)
        .join(Election.participants)
        .filter(Participant.name.contains(data['name']))
    )
