"""create personnel table

Revision ID: 2c0b025e49ac
Revises: 3d786e6a670c
Create Date: 2022-10-20 12:03:42.635479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c0b025e49ac'
down_revision = '3d786e6a670c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('personnel',
                    sa.Column('project_id', sa.Integer, nullable=False, primary_key=True),
                    sa.Column('user_id', sa.Integer, nullable=False, primary_key=True),
                    sa.Column('assigned_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()'))
                    )

    op.create_foreign_key('personnel_projects_fk', source_table='personnel', referent_table='projects', 
                        local_cols=['project_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('personnel_users_fk', source_table='personnel', referent_table='users', 
                        local_cols=['user_id'], remote_cols=['id'], ondelete="CASCADE")

def downgrade() -> None:
    op.drop_constraint('personnel_projects_fk', table_name='personnel')
    op.drop_constraint('personnel_users_fk', table_name='personnel')
    op.drop_table('personnel')
