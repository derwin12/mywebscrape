"""Created and modified times

Revision ID: 7d4ececd02b6
Revises: 1587562fefe2
Create Date: 2022-04-02 15:21:19.947599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d4ececd02b6'
down_revision = '1587562fefe2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('base_url', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_created', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.add_column(sa.Column('time_updated', sa.DateTime(), nullable=True))

    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_created', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.add_column(sa.Column('time_updated', sa.DateTime(), nullable=True))

    with op.batch_alter_table('vendor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_created', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))
        batch_op.add_column(sa.Column('time_updated', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vendor', schema=None) as batch_op:
        batch_op.drop_column('time_updated')
        batch_op.drop_column('time_created')

    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.drop_column('time_updated')
        batch_op.drop_column('time_created')

    with op.batch_alter_table('base_url', schema=None) as batch_op:
        batch_op.drop_column('time_updated')
        batch_op.drop_column('time_created')

    # ### end Alembic commands ###