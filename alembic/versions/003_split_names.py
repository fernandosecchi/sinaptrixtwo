"""Split name into first_name and last_name

Revision ID: 003_split_names
Revises: 002_create_leads
Create Date: 2025-11-19 03:18:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = '003_split_names'
down_revision: Union[str, None] = '002_create_leads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=50), nullable=True))
    
    # Migrate existing data for users - split name into first_name and last_name
    connection = op.get_bind()
    result = connection.execute(text("SELECT id, name FROM users"))
    for row in result:
        if row.name:
            parts = row.name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            connection.execute(
                text("UPDATE users SET first_name = :first, last_name = :last WHERE id = :id"),
                {"first": first_name, "last": last_name, "id": row.id}
            )
    
    # Make columns not nullable
    op.alter_column('users', 'first_name', nullable=False)
    op.alter_column('users', 'last_name', nullable=False)
    
    # Drop old name column from users
    op.drop_column('users', 'name')
    
    # Add new columns to leads table
    op.add_column('leads', sa.Column('first_name', sa.String(length=50), nullable=True))
    op.add_column('leads', sa.Column('last_name', sa.String(length=50), nullable=True))
    
    # Migrate existing data for leads - split name into first_name and last_name
    result = connection.execute(text("SELECT id, name FROM leads"))
    for row in result:
        if row.name:
            parts = row.name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ''
            connection.execute(
                text("UPDATE leads SET first_name = :first, last_name = :last WHERE id = :id"),
                {"first": first_name, "last": last_name, "id": row.id}
            )
    
    # Make columns not nullable
    op.alter_column('leads', 'first_name', nullable=False)
    op.alter_column('leads', 'last_name', nullable=False)
    
    # Drop old name column from leads
    op.drop_column('leads', 'name')


def downgrade() -> None:
    # Re-add name columns
    op.add_column('users', sa.Column('name', sa.String(length=100), nullable=True))
    op.add_column('leads', sa.Column('name', sa.String(length=100), nullable=True))
    
    # Migrate data back - combine first_name and last_name into name
    connection = op.get_bind()
    
    # For users table
    result = connection.execute(text("SELECT id, first_name, last_name FROM users"))
    for row in result:
        full_name = f"{row.first_name} {row.last_name}".strip()
        connection.execute(
            text("UPDATE users SET name = :name WHERE id = :id"),
            {"name": full_name, "id": row.id}
        )
    
    # For leads table
    result = connection.execute(text("SELECT id, first_name, last_name FROM leads"))
    for row in result:
        full_name = f"{row.first_name} {row.last_name}".strip()
        connection.execute(
            text("UPDATE leads SET name = :name WHERE id = :id"),
            {"name": full_name, "id": row.id}
        )
    
    # Make name columns not nullable
    op.alter_column('users', 'name', nullable=False)
    op.alter_column('leads', 'name', nullable=False)
    
    # Drop split columns
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
    op.drop_column('leads', 'first_name')
    op.drop_column('leads', 'last_name')