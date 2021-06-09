"""empty message

Revision ID: 2d81affafde1
Revises: 5c73f7f53d60
Create Date: 2021-06-02 11:40:50.332755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d81affafde1'
down_revision = '5c73f7f53d60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent',
                  sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description',
                  sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    # ### end Alembic commands ###
