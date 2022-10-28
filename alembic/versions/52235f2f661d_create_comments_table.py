"""create comments table

Revision ID: 52235f2f661d
Revises: 94a929a0ec01
Create Date: 2022-10-20 12:16:59.331738

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52235f2f661d'
down_revision = '94a929a0ec01'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('comments',
                    sa.Column('id', sa.Integer, primary_key=True, nullable=False),
                    sa.Column('body_text', sa.String, nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
                    sa.Column('ticket_id', sa.Integer, nullable=False),
                    sa.Column('creator_id', sa.Integer, nullable=False)
                    )

    op.create_foreign_key('comments_tickets_fk', source_table='comments', referent_table='tickets', 
                        local_cols=['ticket_id'], remote_cols=['id'], ondelete="CASCADE")
    op.create_foreign_key('comments_users_fk', source_table='comments', referent_table='users', 
                        local_cols=['creator_id'], remote_cols=['id'], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('comments_tickets_fk', table_name='comments')
    op.drop_constraint('comments_users_fk', table_name='comments')
    op.drop_table('comments')
