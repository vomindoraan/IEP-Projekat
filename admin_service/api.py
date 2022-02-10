from datetime import datetime

from sqlalchemy import func

from common.api import *
from voting_service.models import DB, Election, Participant, Vote
from . import schemas


service_bp = Blueprint('admin', __name__)


@service_bp.post('/createParticipant')
@auth_jwt(require_role='admin')
@consumes(schemas.ParticipantCreation.ONE)
@produces(schemas.CreatedParticipant.ONE)
def create_participant(data):
    participant = Participant(**data)
    DB.session.add(participant)
    DB.session.commit()
    return participant


@service_bp.get('/getParticipants')
@auth_jwt(require_role='admin')
@produces(schemas.Participant.MANY)
def get_participants():
    return Participant.query.all()


@service_bp.post('/createElection')
@auth_jwt(require_role='admin')
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
@auth_jwt(require_role='admin')
@produces(schemas.Election.MANY)
def get_elections():
    return Election.query.all()


@service_bp.get('/getResults')
@auth_jwt(require_role='admin')
@consumes(schemas.ResultsQuery.ONE)
@produces(schemas.Results.ONE)
def get_results(data):
    eid = data['election_id']
    e = Election.query.get(eid)
    if not e:
        raise BadRequest("Election does not exist.")
    elif e.end > datetime.now(e.end.tzinfo):
        raise BadRequest("Election is ongoing.")

    participants_q = Participant.query.filter_by(election_id=eid)
    votes_q = Vote.query.filter_by(election_id=eid)

    if e.individual:
        # Presidential elections
        total_votes = votes_q.count()
        sq = (
            votes_q
            .with_entities(
                Vote.poll_number,
                func.round(func.count('*') / total_votes, 2).label('result'),
            )
            .group_by(Vote.poll_number)
            .subquery()
        )
        q = (
            participants_q
            .with_entities(
                Participant.poll_number,
                Participant.name,
                func.ifnull(sq.c.result, 0).label('result'),  # Must relabel
            )
            .outerjoin(sq, Participant.poll_number == sq.c.poll_number)
        )
        participants = (p._asdict() for p in q)
    else:
        # Parliamentary elections
        pass  # TODO

    invalid_votes = votes_q.filter(Vote.invalid != None)

    return {'participants': participants, 'invalid_votes': invalid_votes}


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
