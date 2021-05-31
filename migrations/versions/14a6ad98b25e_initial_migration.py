"""Initial Migration

Revision ID: 14a6ad98b25e
Revises: 3fe9e86ed4e8
Create Date: 2021-05-28 10:49:46.113255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14a6ad98b25e'
down_revision = '3fe9e86ed4e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('isApprove', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item', 'isApprove')
    # ### end Alembic commands ###
