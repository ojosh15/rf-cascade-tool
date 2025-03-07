"""New initial?

Revision ID: adadd077aa6d
Revises: 86731f4cfeee
Create Date: 2025-03-01 02:27:14.296448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'adadd077aa6d'
down_revision: Union[str, None] = '86731f4cfeee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('component_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('data_source', sa.Enum('SIMULATED', 'MEASURED', name='sourceenum'), nullable=False),
    sa.Column('gain', sa.JSON(), nullable=True),
    sa.Column('nf', sa.JSON(), nullable=True),
    sa.Column('ip2', sa.JSON(), nullable=True),
    sa.Column('ip3', sa.JSON(), nullable=True),
    sa.Column('p1db', sa.JSON(), nullable=True),
    sa.Column('max_input', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('component_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('type')
    )
    op.create_table('projects',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('components',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('component_type_id', sa.Integer(), nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('manufacturer', sa.String(length=50), nullable=False),
    sa.Column('serial_no', sa.String(length=50), nullable=False),
    sa.Column('num_ports', sa.Integer(), nullable=False),
    sa.Column('start_freq', sa.BigInteger(), nullable=False),
    sa.Column('stop_freq', sa.BigInteger(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_variable', sa.Boolean(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['component_type_id'], ['component_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('paths',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('input', sa.String(), nullable=False),
    sa.Column('output', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('component_versions',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('component_id', sa.Integer(), nullable=False),
    sa.Column('component_data_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('change_note', sa.String(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['component_data_id'], ['component_data.id'], ),
    sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('data_sheets',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('component_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('extension', sa.String(), nullable=False),
    sa.Column('mime_type', sa.String(), nullable=False),
    sa.Column('file_path', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['component_id'], ['components.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('file_path'),
    sa.UniqueConstraint('name')
    )
    op.create_table('stackups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('path_id', sa.Integer(), nullable=False),
    sa.Column('component_version_id', sa.Integer(), nullable=False),
    sa.Column('next_stackup_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['component_version_id'], ['component_versions.id'], ),
    sa.ForeignKeyConstraint(['next_stackup_id'], ['stackups.id'], ),
    sa.ForeignKeyConstraint(['path_id'], ['paths.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('next_stackup_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stackups')
    op.drop_table('data_sheets')
    op.drop_table('component_versions')
    op.drop_table('paths')
    op.drop_table('components')
    op.drop_table('projects')
    op.drop_table('component_types')
    op.drop_table('component_data')
    # ### end Alembic commands ###
