"""create tickets table

Revision ID: 94a929a0ec01
Revises: 2c0b025e49ac
Create Date: 2022-10-20 12:10:40.893093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94a929a0ec01'
down_revision = '2c0b025e49ac'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('tickets',
                    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
                    sa.Column('caption', sa.String, nullable=False),
                    sa.Column('description', sa.String, nullable=False),
                    sa.Column('priority', sa.Integer, nullable=False),
                    sa.Column('status', sa.String, server_default='new', nullable = False),
                    sa.Column('category', sa.String, nullable = False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('project_id', sa.Integer, nullable=False),
                    sa.Column('creator_id', sa.Integer, nullable=False)
                    )

    op.create_foreign_key('tickets_projects_fk', source_table='tickets', referent_table='projects', 
                        local_cols=['project_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('tickets_users_fk', source_table='tickets', referent_table='users', 
                        local_cols=['creator_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('tickets_projects_fk', table_name='tickets')
    op.drop_constraint('tickets_users_fk', table_name='tickets')
    op.drop_table('tickets')
