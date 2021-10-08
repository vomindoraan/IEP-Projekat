from datetime import datetime

from common.api import *
from . import schemas
from .models import DB, Election, Participant, Vote


service_bp = Blueprint('admin', __name__)


@service_bp.post('/createParticipant')
@auth_jwt()
@consumes(schemas.ParticipantCreation.ONE)
@produces(schemas.CreatedParticipant.ONE)
def create_participant(data):
    participant = Participant(**data)
    DB.session.add(participant)
    DB.session.commit()
    return participant


@service_bp.get('/getParticipants')
@auth_jwt()
@produces(schemas.Participant.MANY)
def get_participants():
    return Participant.query.all()


@service_bp.post('/createElection')
@auth_jwt()
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
        p = Participant.query.get(pid)
        if not p or data['individual'] != p.individual:
            raise BadRequest("Invalid participants.")

        p.poll_number = i
        participants.append(p)
        poll_numbers.append(i)

    data['participants'] = participants
    election = Election(**data)
    DB.session.add(election)
    DB.session.commit()

    return {'poll_numbers': poll_numbers}


@service_bp.get('/getElections')
@auth_jwt()
@produces(schemas.Election.MANY)
def get_elections():
    return Election.query.all()


@service_bp.get('/getResults')
@auth_jwt()
@consumes(schemas.ResultsQuery.ONE)
@produces(schemas.Results.ONE)
def get_results(data):
    eid = data['election_id']
    if not (e := Election.query.get(eid)):
        raise BadRequest("Election does not exist.")
    elif e.end > datetime.now(tz=e.end.tzinfo):
        raise BadRequest("Election is ongoing.")

    # for p in Participant.query.filter(Participant.election_id == eid):

    invalid_votes = Vote.query.filter(Vote.invalid is not None)

    return {'invalid_votes': invalid_votes}


lookup_bp = Blueprint('lookup', __name__)

@lookup_bp.get('/lookup')
@auth_jwt()
@consumes(schemas.LookupQuery.ONE)
@produces(schemas.Election.MANY)
def lookup(data):
    return (
        Election.query
        .join(Election.participants)
        .filter(Participant.name.contains(data['name']))
    )
