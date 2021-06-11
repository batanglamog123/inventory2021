"""Initial Migration

Revision ID: 3fe9e86ed4e8
Revises: b70c946821e4
Create Date: 2021-05-28 10:45:03.273152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3fe9e86ed4e8'
down_revision = 'b70c946821e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operator_approval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('person', sa.String(length=150), nullable=True),
    sa.Column('purpose', sa.String(length=150), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('itemApproval_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['itemApproval_id'], ['item_approval.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spec_approval',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cpu', sa.String(length=150), nullable=True),
    sa.Column('gpu', sa.String(length=150), nullable=True),
    sa.Column('ram', sa.String(length=150), nullable=True),
    sa.Column('odd', sa.String(length=150), nullable=True),
    sa.Column('avr_ups', sa.String(length=150), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('itemApproval_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['itemApproval_id'], ['item_approval.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('spec_approval')
    op.drop_table('operator_approval')
    # ### end Alembic commands ###