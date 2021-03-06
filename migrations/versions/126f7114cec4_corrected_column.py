"""Corrected column

Revision ID: 126f7114cec4
Revises: 82e2fa47e97f
Create Date: 2022-05-06 14:54:34.250806

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '126f7114cec4'
down_revision = '82e2fa47e97f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_price_changed', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))

    with op.batch_alter_table('vendor', schema=None) as batch_op:
        batch_op.drop_column('time_price_changed')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('vendor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('time_price_changed', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))

    with op.batch_alter_table('sequence', schema=None) as batch_op:
        batch_op.drop_column('time_price_changed')

    # ### end Alembic commands ###
