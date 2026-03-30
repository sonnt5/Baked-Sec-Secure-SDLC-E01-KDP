"""add inline test case content columns

Revision ID: b1c2d3e4f5a6
Revises: a830ed5ce83a
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa

revision = 'b1c2d3e4f5a6'
down_revision = 'a830ed5ce83a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('test_cases', sa.Column('input_content', sa.Text(), nullable=True))
    op.add_column('test_cases', sa.Column('output_content', sa.Text(), nullable=True))
    # Make input_file/output_file nullable (they're empty string for txt test cases)
    op.alter_column('test_cases', 'input_file', existing_type=sa.Text(), server_default='', nullable=False)
    op.alter_column('test_cases', 'output_file', existing_type=sa.Text(), server_default='', nullable=False)
    op.alter_column('test_cases', 'input_checksum', existing_type=sa.String(), server_default='', nullable=False)
    op.alter_column('test_cases', 'output_checksum', existing_type=sa.String(), server_default='', nullable=False)


def downgrade() -> None:
    op.drop_column('test_cases', 'input_content')
    op.drop_column('test_cases', 'output_content')
