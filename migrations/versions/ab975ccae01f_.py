"""empty message

Revision ID: ab975ccae01f
Revises: c137571c05c3
Create Date: 2021-03-27 22:21:47.443689

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab975ccae01f'
down_revision = 'c137571c05c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('seeking_description', sa.String(length=200), nullable=True))
    op.add_column('artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.drop_column('artist', 'desc_seeking')
    op.drop_column('artist', 'talent_seeking')
    op.add_column('venue', sa.Column('seeking_description', sa.String(length=200), nullable=True))
    op.add_column('venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.drop_column('venue', 'talent_looking')
    op.drop_column('venue', 'desc_looking')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('desc_looking', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column('venue', sa.Column('talent_looking', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'seeking_talent')
    op.drop_column('venue', 'seeking_description')
    op.add_column('artist', sa.Column('talent_seeking', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('artist', sa.Column('desc_seeking', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.drop_column('artist', 'seeking_venue')
    op.drop_column('artist', 'seeking_description')
    # ### end Alembic commands ###