"""empty message

Revision ID: 4ff57560cbde
Revises: 60b3839d3384
Create Date: 2019-06-29 22:59:12.840375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ff57560cbde'
down_revision = '60b3839d3384'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tokens', sa.Column('access_token', sa.String(length=3000), nullable=False))
    op.add_column('tokens', sa.Column('refresh_token', sa.String(length=3000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tokens', 'refresh_token')
    op.drop_column('tokens', 'access_token')
    # ### end Alembic commands ###