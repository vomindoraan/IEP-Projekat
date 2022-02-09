from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType


DB = SQLAlchemy()


class Participant(DB.Model):
    __tablename__ = 'participants'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(256), nullable=False)
    individual = DB.Column(DB.Boolean, nullable=False)

    election_id = DB.Column(DB.Integer,
                            DB.ForeignKey('elections.id', ondelete='SET NULL'))
    poll_number = DB.Column(DB.Integer)
    result = DB.Column(DB.Integer)


class Election(DB.Model):
    __tablename__ = 'elections'

    id = DB.Column(DB.Integer, primary_key=True)
    start = DB.Column(DB.DateTime, nullable=False)
    end = DB.Column(DB.DateTime, nullable=False)
    individual = DB.Column(DB.Boolean, nullable=False)

    participants = DB.relationship('Participant')


class Vote(DB.Model):
    __tablename__ = 'votes'

    id = DB.Column(DB.Integer, primary_key=True)
    ballot_uuid = DB.Column(UUIDType, nullable=False)
    poll_number = DB.Column(DB.Integer, nullable=False)
    invalid = DB.Column(DB.String(256))

    election_id = DB.Column(DB.Integer,
                            DB.ForeignKey('elections.id', ondelete='SET NULL'))
