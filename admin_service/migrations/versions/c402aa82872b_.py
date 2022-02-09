"""empty message

Revision ID: c402aa82872b
Revises: ee5e65d16b69
Create Date: 2021-10-15 04:57:14.806743

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c402aa82872b'
down_revision = 'ee5e65d16b69'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('participants_ibfk_1', 'participants', type_='foreignkey')
    op.create_foreign_key(None, 'participants', 'elections', ['election_id'], ['id'], ondelete='SET NULL')
    op.drop_constraint('votes_ibfk_1', 'votes', type_='foreignkey')
    op.create_foreign_key(None, 'votes', 'elections', ['election_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'votes', type_='foreignkey')
    op.create_foreign_key('votes_ibfk_1', 'votes', 'elections', ['election_id'], ['id'])
    op.drop_constraint(None, 'participants', type_='foreignkey')
    op.create_foreign_key('participants_ibfk_1', 'participants', 'elections', ['election_id'], ['id'])
    # ### end Alembic commands ###
