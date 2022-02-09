from datetime import datetime

from common.api import *
from . import schemas
from .models import DB, Election, Participant, Vote


service_bp = Blueprint('admin', __name__)


@service_bp.post('/createParticipant')
@auth_jwt(admin=True)
@consumes(schemas.ParticipantCreation.ONE)
@produces(schemas.CreatedParticipant.ONE)
def create_participant(data):
    participant = Participant(**data)
    DB.session.add(participant)
    DB.session.commit()
    return participant


@service_bp.get('/getParticipants')
@auth_jwt(admin=True)
@produces(schemas.Participant.MANY)
def get_participants():
    return Participant.query.all()


@service_bp.post('/createElection')
@auth_jwt(admin=True)
@consumes(schemas.ElectionCreation.ONE)
@produces(schemas.PollNumbers.ONE)
def create_election(data):
    election = Election(start=data['start'], end=data['end'],
                        individual=data['individual'])
    # TODO: Replace loop with filter
    for e in Election.query.all():
        e.start = e.start.astimezone(election.start.tzinfo)
        e.end = e.end.astimezone(election.start.tzinfo)
        if (
            e.start < election.start and e.end >= election.start or
            election.start < e.start and election.end >= e.start
        ):
            raise BadRequest("Invalid date and time.")

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

    election.participants = participants
    DB.session.add(election)
    DB.session.commit()

    return {'poll_numbers': poll_numbers}


@service_bp.get('/getElections')
@auth_jwt(admin=True)
@produces(schemas.Election.MANY)
def get_elections():
    return Election.query.all()


@service_bp.get('/getResults')
@auth_jwt(admin=True)
@consumes(schemas.ResultsQuery.ONE)
@produces(schemas.Results.ONE)
def get_results(data):
    eid = data['election_id']
    if not (e := Election.query.get(eid)):
        raise BadRequest("Election does not exist.")
    elif e.end > datetime.now(e.end.tzinfo):
        raise BadRequest("Election is ongoing.")

    # for p in Participant.query.filter(Participant.election_id == eid):

    invalid_votes = Vote.query.filter(Vote.invalid is not None)

    return {'invalid_votes': invalid_votes}


extra_bp = Blueprint('extra', __name__)


@extra_bp.get('/lookup')
@auth_jwt()
@consumes(schemas.LookupQuery.ONE)
@produces(schemas.Election.MANY)
def lookup(data):
    return (
        Election.query
        .join(Election.participants)
        .filter(Participant.name.contains(data['name']))
    )
