"""vendor delivery rules

Revision ID: 20260516_0010
Revises: 20260516_0009
Create Date: 2026-05-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260516_0010"
down_revision: str | None = "20260516_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


weekday_values = "('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')"


def upgrade() -> None:
    op.create_table(
        "vendor_delivery_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_weekday", sa.String(length=20), nullable=False),
        sa.Column("order_cutoff_weekday", sa.String(length=20), nullable=False),
        sa.Column("order_cutoff_time", sa.Time(), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), nullable=True),
        sa.Column("minimum_order_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("delivery_window_start", sa.Time(), nullable=True),
        sa.Column("delivery_window_end", sa.Time(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            f"delivery_weekday IN {weekday_values}",
            name="ck_vendor_delivery_rules_delivery_weekday",
        ),
        sa.CheckConstraint(
            f"order_cutoff_weekday IN {weekday_values}",
            name="ck_vendor_delivery_rules_order_cutoff_weekday",
        ),
        sa.CheckConstraint(
            "lead_time_days IS NULL OR lead_time_days >= 0",
            name="ck_vendor_delivery_rules_lead_time_days_non_negative",
        ),
        sa.CheckConstraint(
            "minimum_order_value IS NULL OR minimum_order_value >= 0",
            name="ck_vendor_delivery_rules_minimum_order_value_non_negative",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vendor_delivery_rules_public_id"), "vendor_delivery_rules", ["public_id"], unique=False)
    op.create_index(op.f("ix_vendor_delivery_rules_tenant_id"), "vendor_delivery_rules", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vendor_delivery_rules_vendor_id"), "vendor_delivery_rules", ["vendor_id"], unique=False)
    op.create_index(
        "ix_vendor_delivery_rules_tenant_vendor_delivery_weekday",
        "vendor_delivery_rules",
        ["tenant_id", "vendor_id", "delivery_weekday"],
        unique=False,
    )
    op.create_index(
        "ix_vendor_delivery_rules_tenant_vendor_id",
        "vendor_delivery_rules",
        ["tenant_id", "vendor_id"],
        unique=False,
    )
    op.create_index("uq_vendor_delivery_rules_public_id", "vendor_delivery_rules", ["public_id"], unique=True)
    op.create_index(
        "uq_vendor_delivery_rules_tenant_vendor_active_schedule",
        "vendor_delivery_rules",
        ["tenant_id", "vendor_id", "delivery_weekday", "order_cutoff_weekday", "order_cutoff_time"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_vendor_delivery_rules_tenant_vendor_active_schedule",
        table_name="vendor_delivery_rules",
        postgresql_where=sa.text("is_active IS TRUE"),
    )
    op.drop_index("uq_vendor_delivery_rules_public_id", table_name="vendor_delivery_rules")
    op.drop_index("ix_vendor_delivery_rules_tenant_vendor_id", table_name="vendor_delivery_rules")
    op.drop_index("ix_vendor_delivery_rules_tenant_vendor_delivery_weekday", table_name="vendor_delivery_rules")
    op.drop_index(op.f("ix_vendor_delivery_rules_vendor_id"), table_name="vendor_delivery_rules")
    op.drop_index(op.f("ix_vendor_delivery_rules_tenant_id"), table_name="vendor_delivery_rules")
    op.drop_index(op.f("ix_vendor_delivery_rules_public_id"), table_name="vendor_delivery_rules")
    op.drop_table("vendor_delivery_rules")
