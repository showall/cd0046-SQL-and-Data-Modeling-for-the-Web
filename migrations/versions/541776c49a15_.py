"""empty message

Revision ID: 541776c49a15
Revises: 
Create Date: 2022-06-23 16:23:57.033316

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '541776c49a15'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Artist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('city', sa.String(length=120), nullable=True),
    sa.Column('state', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('genres', sa.String(length=120), nullable=True),
    sa.Column('website_link', sa.String(), nullable=True),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=500), nullable=True),
    sa.Column('seeking_venue', sa.Boolean(), nullable=True),
    sa.Column('seeking_description', sa.String(), nullable=True),
    sa.Column('past_shows', sa.String(), nullable=True),
    sa.Column('upcoming_shows', sa.String(), nullable=True),
    sa.Column('past_shows_count', sa.Integer(), nullable=True),
    sa.Column('upcoming_shows_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Venue',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('genres', sa.String(), nullable=True),
    sa.Column('city', sa.String(length=120), nullable=True),
    sa.Column('state', sa.String(length=120), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('phone', sa.String(length=120), nullable=True),
    sa.Column('website_link', sa.String(length=500), nullable=True),
    sa.Column('image_link', sa.String(length=500), nullable=True),
    sa.Column('facebook_link', sa.String(length=500), nullable=True),
    sa.Column('seeking_talent', sa.Boolean(), nullable=True),
    sa.Column('seeking_description', sa.String(), nullable=True),
    sa.Column('past_shows', sa.String(), nullable=True),
    sa.Column('upcoming_shows', sa.String(), nullable=True),
    sa.Column('past_shows_count', sa.Integer(), nullable=True),
    sa.Column('upcoming_shows_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Shows',
    sa.Column('Artist', sa.Integer(), nullable=False),
    sa.Column('Venue', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['Artist'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['Venue'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('Artist', 'Venue')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Shows')
    op.drop_table('Venue')
    op.drop_table('Artist')
    # ### end Alembic commands ###
