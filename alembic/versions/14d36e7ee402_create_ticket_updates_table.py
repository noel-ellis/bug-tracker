"""create ticket_updates table

Revision ID: 14d36e7ee402
Revises: 52235f2f661d
Create Date: 2022-10-20 12:41:46.506539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14d36e7ee402'
down_revision = '52235f2f661d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('ticket_updates',
                    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('ticket_id', sa.Integer, nullable=False),
                    sa.Column('editor_id', sa.Integer, nullable=False),
                    sa.Column('old_caption', sa.String, server_default=None),
                    sa.Column('old_description', sa.String, server_default=None),
                    sa.Column('old_priority', sa.String, server_default=None),
                    sa.Column('old_status', sa.String, server_default=None),
                    sa.Column('old_category', sa.String, server_default=None),
                    sa.Column('new_caption', sa.String, server_default=None),
                    sa.Column('new_description', sa.String, server_default=None),
                    sa.Column('new_priority', sa.String, server_default=None),
                    sa.Column('new_status', sa.String, server_default=None),
                    sa.Column('new_category', sa.String, server_default=None)
                    )

    op.create_foreign_key('ticket_updates_tickets_fk', source_table='ticket_updates', referent_table='tickets', 
                        local_cols=['ticket_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('ticket_updates_users_fk', source_table='ticket_updates', referent_table='users', 
                        local_cols=['editor_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('ticket_updates_tickets_fk', table_name='ticket_updates')
    op.drop_constraint('ticket_updates_tickets_fk', table_name='ticket_updates')
    op.drop_table('ticket_updates')
