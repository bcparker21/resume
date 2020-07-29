"""user coverletter

Revision ID: 45ab72fbd7cd
Revises: bf2ebf7e69d1
Create Date: 2020-07-29 10:59:44.169490

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45ab72fbd7cd'
down_revision = 'bf2ebf7e69d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('coverletter', sa.String(length=99999), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'coverletter')
    # ### end Alembic commands ###