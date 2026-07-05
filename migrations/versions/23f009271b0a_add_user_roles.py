"""add user roles

Revision ID: 23f009271b0a
Revises: 3604054ae2ac
Create Date: 2026-07-05 23:56:32.601891

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '23f009271b0a'
down_revision: Union[str, Sequence[str], None] = '3604054ae2ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column(
            'role',
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
            server_default='user',
        ),
    )
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_column('users', 'role')

    # ### end Alembic commands ###
