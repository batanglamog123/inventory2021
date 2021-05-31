"""Initial migration.

Revision ID: 34a6a8ffcd3f
Revises: b4dbf395ebc3
Create Date: 2021-05-13 16:44:51.292940

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34a6a8ffcd3f'
down_revision = 'b4dbf395ebc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('operator',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('person', sa.String(length=150), nullable=True),
    sa.Column('purpose', sa.String(length=150), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('operator')
    # ### end Alembic commands ###
