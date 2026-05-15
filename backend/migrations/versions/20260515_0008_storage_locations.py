"""storage locations

Revision ID: 20260515_0008
Revises: 20260515_0007
Create Date: 2026-05-15
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260515_0008"
down_revision: str | None = "20260515_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "storage_locations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("storage_type", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "storage_type IN ('cooler', 'freezer', 'dry', 'ambient', 'other')",
            name="ck_storage_locations_storage_type",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_storage_locations_public_id"), "storage_locations", ["public_id"], unique=False)
    op.create_index(op.f("ix_storage_locations_tenant_id"), "storage_locations", ["tenant_id"], unique=False)
    op.create_index("uq_storage_locations_public_id", "storage_locations", ["public_id"], unique=True)
    op.create_index(
        "uq_storage_locations_tenant_active_normalized_name",
        "storage_locations",
        ["tenant_id", "normalized_name"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_storage_locations_tenant_active_normalized_name",
        table_name="storage_locations",
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.drop_index("uq_storage_locations_public_id", table_name="storage_locations")
    op.drop_index(op.f("ix_storage_locations_tenant_id"), table_name="storage_locations")
    op.drop_index(op.f("ix_storage_locations_public_id"), table_name="storage_locations")
    op.drop_table("storage_locations")
