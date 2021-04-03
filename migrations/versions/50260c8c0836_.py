"""empty message

Revision ID: 50260c8c0836
Revises: 276b8750e3a3
Create Date: 2021-03-22 22:41:18.785498

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50260c8c0836'
down_revision = '276b8750e3a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('desc_looking', sa.String(length=200), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('Venue', sa.Column('talent_looking', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'talent_looking')
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'desc_looking')
    # ### end Alembic commands ###