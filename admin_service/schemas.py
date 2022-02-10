from marshmallow import validates_schema

from common.schemas import *
from voting_service import models


# region Participant requests

class ParticipantCreation(SQLAlchemyMixin, APIRequest):
    class Meta(APIRequest.Meta):
        model = models.Participant

    name = MM.auto_field()
    individual = MM.auto_field()

# endregion


# region Participant responses

class BaseParticipantResponse(SQLAlchemyMixin, APIResponse):
    class Meta(APIResponse.Meta):
        model = models.Participant


class CreatedParticipant(BaseParticipantResponse):
    id = MM.auto_field()


class Participant(BaseParticipantResponse):
    class Meta(BaseParticipantResponse.Meta):
        envelope_many_key = 'participants'

    id = MM.auto_field()
    name = MM.auto_field()
    individual = MM.auto_field()

# endregion


# region Election requests

class ElectionCreation(SQLAlchemyMixin, APIRequest):
    class Meta(APIRequest.Meta):
        model = models.Election

    start = DateTimeField(required=True)
    end = DateTimeField(required=True)
    individual = MM.auto_field()
    participants = MM.List(MM.Integer(), required=True)

    @classmethod
    def make_message(cls, msg_key, data_key):
        match msg_key, data_key:
            case 'invalid', ('start' | 'end'):
                return "Invalid date and time."
            case _:
                return super().make_message(msg_key, data_key)

    @validates_schema
    def validate_interval(self, data, **kwargs):
        if data['start'] > data['end']:
            raise ValidationError("Invalid date and time.")

# endregion


# region Election responses

class PollNumbers(APIResponse):
    poll_numbers = MM.List(MM.Integer(), data_key='pollNumbers')


class ElectionParticipant(BaseParticipantResponse):
    id = MM.auto_field()
    name = MM.auto_field()


class Election(SQLAlchemyMixin, APIResponse):
    class Meta(APIResponse.Meta):
        model = models.Election
        include_relationships = True
        envelope_many_key = 'elections'

    id = MM.auto_field()
    start = DateTimeField()
    end = DateTimeField()
    individual = MM.auto_field()
    participants = MM.Nested(ElectionParticipant, many=True)

# endregion


# region Results requests

class ResultsQuery(APIQuery):
    election_id = MM.Integer(required=True, data_key='id')

# endregion


# region Results responses

class ParticipantResult(SQLAlchemyMixin, APIResponse):
    class Meta(APIResponse.Meta):
        model = models.Participant

    poll_number = MM.auto_field(data_key='pollNumber')
    name = MM.auto_field()
    result = MM.Number()


class InvalidVote(SQLAlchemyMixin, APIResponse):
    class Meta(APIResponse.Meta):
        model = models.Vote

    user_jmbg = MM.auto_field(data_key='electionOfficialJmbg')
    ballot_uuid = MM.auto_field(data_key='ballotGuid')
    poll_number = MM.auto_field(data_key='pollNumber')
    invalid = MM.auto_field(data_key='reason')


class Results(APIResponse):
    participants = MM.Nested(ParticipantResult, many=True)
    invalid_votes = MM.Nested(InvalidVote, many=True, data_key='invalidVotes')

# endregion


# region Extra requests

class LookupQuery(APIQuery):
    name = MM.String(required=True)

# endregion
