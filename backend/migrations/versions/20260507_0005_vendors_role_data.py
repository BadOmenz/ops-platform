"""vendors role data

Revision ID: 20260507_0005
Revises: 20260506_0004
Create Date: 2026-05-07
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260507_0005"
down_revision: str | None = "20260506_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_code", sa.String(length=100), nullable=True),
        sa.Column("account_number", sa.String(length=100), nullable=True),
        sa.Column("ordering_email", sa.String(length=255), nullable=True),
        sa.Column("ordering_phone", sa.String(length=100), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id", name="uq_vendors_public_id"),
    )
    op.create_index(op.f("ix_vendors_organization_id"), "vendors", ["organization_id"], unique=False)
    op.create_index(op.f("ix_vendors_public_id"), "vendors", ["public_id"], unique=False)
    op.create_index(op.f("ix_vendors_tenant_id"), "vendors", ["tenant_id"], unique=False)
    op.create_index(
        "uq_vendors_tenant_active_organization",
        "vendors",
        ["tenant_id", "organization_id"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )


def downgrade() -> None:
    op.drop_index("uq_vendors_tenant_active_organization", table_name="vendors", postgresql_where=sa.text("is_active IS TRUE"))
    op.drop_index(op.f("ix_vendors_tenant_id"), table_name="vendors")
    op.drop_index(op.f("ix_vendors_public_id"), table_name="vendors")
    op.drop_index(op.f("ix_vendors_organization_id"), table_name="vendors")
    op.drop_table("vendors")
