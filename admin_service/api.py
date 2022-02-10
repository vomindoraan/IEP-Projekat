from collections import defaultdict

from sqlalchemy import func, literal

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
        start = e.start.astimezone(election.start.tzinfo)
        end = e.end.astimezone(election.start.tzinfo)
        if (
            start < election.start and end >= election.start or
            election.start < start and election.end >= start
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
    # TODO
    # elif e.end > datetime.now(e.end.tzinfo):
    #     raise BadRequest("Election is ongoing.")

    participants_q = Participant.query.filter_by(election_id=eid)
    votes_q = Vote.query.filter_by(election_id=eid, invalid=None)
    sq = (
        votes_q
        .with_entities(Vote.poll_number, func.count().label('votes'))
        .group_by(Vote.poll_number)
        .subquery()
    )

    if e.individual:
        # Presidential elections
        total_votes = votes_q.count()
        votes = func.ifnull(sq.c.votes, 0)
        q = (
            participants_q
            .with_entities(
                Participant.poll_number,
                Participant.name,
                func.round(votes / total_votes, 2).label('result'),
            )
            .outerjoin(sq, Participant.poll_number == sq.c.poll_number)
        )
        participants = [p._asdict() for p in q]

    else:
        # Parliamentary elections
        q = (
            participants_q
            .with_entities(
                Participant.poll_number,
                Participant.name,
                func.ifnull(sq.c.votes, 0).label('votes'),
                literal(0).label('result'),
            )
            .outerjoin(sq, Participant.poll_number == sq.c.poll_number)
        )
        participants = [p._asdict() for p in q]

        total_seats = 250
        threshold = 0.05 * total_seats
        og_votes = {p['poll_number']: p['votes'] for p in participants}
        votes = og_votes.copy()
        seats = defaultdict(int)
        d = True
        while d:
            while sum(seats.values()) < total_seats:
                next_seat = max(votes, key=votes.get)
                seats[next_seat] += 1
                votes[next_seat] = og_votes[next_seat] / (seats[next_seat] + 1)
            d = False
            for k, v in seats.items():
                if v != 0 and v < threshold:
                    votes[k] = seats[k] = 0
                    d = True
        participants = [{**p, 'result': seats[p['poll_number']]}
                        for p in participants]

    invalid_votes = Vote.query.filter(Vote.election_id == eid,
                                      Vote.invalid != None)

    return {'participants': participants, 'invalid_votes': invalid_votes}


extra_bp = Blueprint('extra', __name__)


@extra_bp.get('/lookup')
# @auth_jwt()
@produces(schemas.ElectionStats.MANY)
def lookup():
    return (
        Election.query
        .with_entities(Election.id,
                       func.count(Participant.id).label('participant_count'))
        .join(Participant)
        .group_by(Election.id)
    )
    # return (
    #     DB.session
    #     .query(Election.id,
    #            func.count(Participant.id).label('participant_count'))
    #     .join(Election.participants)
    #     .group_by(Election.id)
    # )
