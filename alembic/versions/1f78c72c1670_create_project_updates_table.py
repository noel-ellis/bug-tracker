"""create project_updates table

Revision ID: 1f78c72c1670
Revises: 14d36e7ee402
Create Date: 2022-10-20 12:48:33.899203

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f78c72c1670'
down_revision = '14d36e7ee402'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('project_updates',
                    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('project_id', sa.Integer, nullable=False),
                    sa.Column('editor_id', sa.Integer, nullable=False),
                    sa.Column('old_name', sa.String, server_default=None),
                    sa.Column('old_description', sa.String, server_default=None),
                    sa.Column('old_start', sa.TIMESTAMP(timezone=True), server_default=None),
                    sa.Column('old_deadline', sa.TIMESTAMP(timezone=True), server_default=None),
                    sa.Column('old_status', sa.String, server_default=None),
                    sa.Column('new_name', sa.String, server_default=None),
                    sa.Column('new_description', sa.String, server_default=None),
                    sa.Column('new_start', sa.TIMESTAMP(timezone=True), server_default=None),
                    sa.Column('new_deadline', sa.TIMESTAMP(timezone=True), server_default=None),
                    sa.Column('new_status', sa.String, server_default=None)
                    )

    op.create_foreign_key('project_updates_projects_fk', source_table='project_updates', referent_table='projects', 
                        local_cols=['project_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('project_updates_users_fk', source_table='project_updates', referent_table='users', 
                        local_cols=['editor_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('project_updates_projects_fk', table_name='project_updates')
    op.drop_constraint('project_updates_projects_fk', table_name='project_updates')
    op.drop_table('project_updates')
