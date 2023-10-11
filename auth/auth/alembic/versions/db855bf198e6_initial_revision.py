"""Initial revision

Revision ID: db855bf198e6
Revises: 
Create Date: 2023-05-08 16:02:04.825217

"""
from alembic import op
import sqlalchemy as sa

import uuid
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "db855bf198e6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
        sa.Column("role", sa.String(32), unique=True),
    )
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False),
        sa.Column("login", sa.String, unique=True, nullable=True),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("admin", sa.Boolean, nullable=False),
        sa.Column("country", sa.String(100), unique=False, nullable=True),
    )
    op.create_table(
        "user_roles",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE")),
    )
    op.create_table(
        "login_records",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("auth_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_agent", sa.String, unique=False, nullable=False),
    )
    op.create_table(
        "social_account",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("social_id", sa.Text, nullable=False),
        sa.Column("social_name", sa.Text, nullable=False),
    )

    op.create_index("user_country_idx", "users", ["id", "country"], unique=True)
    op.create_index("user_agent", "login_records", ["user_id", "user_agent"])


def downgrade() -> None:
    op.drop_index("user_country_idx", "users")
    op.drop_index("user_agent", "login_records")
    op.execute("DROP TABLE users, roles, user_roles, login_records, social_account CASCADE")
