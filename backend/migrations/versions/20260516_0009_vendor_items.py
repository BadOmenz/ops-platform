"""vendor items

Revision ID: 20260516_0009
Revises: 20260515_0008
Create Date: 2026-05-16
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260516_0009"
down_revision: str | None = "20260515_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "vendor_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_item_code", sa.String(length=100), nullable=True),
        sa.Column("vendor_description", sa.String(length=255), nullable=False),
        sa.Column("canonical_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_canonical_name", sa.String(length=255), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("default_storage_location_id", sa.Integer(), nullable=True),
        sa.Column("purchase_unit", sa.String(length=50), nullable=True),
        sa.Column("pack_size", sa.Numeric(12, 4), nullable=True),
        sa.Column("pack_unit", sa.String(length=50), nullable=True),
        sa.Column("case_quantity", sa.Numeric(12, 4), nullable=True),
        sa.Column("case_unit", sa.String(length=50), nullable=True),
        sa.Column("last_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("last_price_date", sa.Date(), nullable=True),
        sa.Column("estimated_price", sa.Numeric(12, 4), nullable=True),
        sa.Column("price_unit", sa.String(length=50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("pack_size IS NULL OR pack_size >= 0", name="ck_vendor_items_pack_size_non_negative"),
        sa.CheckConstraint(
            "case_quantity IS NULL OR case_quantity >= 0",
            name="ck_vendor_items_case_quantity_non_negative",
        ),
        sa.CheckConstraint("last_price IS NULL OR last_price >= 0", name="ck_vendor_items_last_price_non_negative"),
        sa.CheckConstraint(
            "estimated_price IS NULL OR estimated_price >= 0",
            name="ck_vendor_items_estimated_price_non_negative",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["item_categories.id"]),
        sa.ForeignKeyConstraint(["default_storage_location_id"], ["storage_locations.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["vendor_id"], ["vendors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vendor_items_category_id"), "vendor_items", ["category_id"], unique=False)
    op.create_index(
        op.f("ix_vendor_items_default_storage_location_id"),
        "vendor_items",
        ["default_storage_location_id"],
        unique=False,
    )
    op.create_index(op.f("ix_vendor_items_public_id"), "vendor_items", ["public_id"], unique=False)
    op.create_index(op.f("ix_vendor_items_tenant_id"), "vendor_items", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_vendor_items_vendor_id"), "vendor_items", ["vendor_id"], unique=False)
    op.create_index("ix_vendor_items_tenant_category_id", "vendor_items", ["tenant_id", "category_id"], unique=False)
    op.create_index(
        "ix_vendor_items_tenant_default_storage_location_id",
        "vendor_items",
        ["tenant_id", "default_storage_location_id"],
        unique=False,
    )
    op.create_index(
        "ix_vendor_items_tenant_normalized_canonical_name",
        "vendor_items",
        ["tenant_id", "normalized_canonical_name"],
        unique=False,
    )
    op.create_index("ix_vendor_items_tenant_vendor_id", "vendor_items", ["tenant_id", "vendor_id"], unique=False)
    op.create_index("uq_vendor_items_public_id", "vendor_items", ["public_id"], unique=True)
    op.create_index(
        "uq_vendor_items_tenant_active_vendor_code",
        "vendor_items",
        ["tenant_id", "vendor_id", "vendor_item_code"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE AND vendor_item_code IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_vendor_items_tenant_active_vendor_code",
        table_name="vendor_items",
        postgresql_where=sa.text("is_active IS TRUE AND vendor_item_code IS NOT NULL"),
    )
    op.drop_index("uq_vendor_items_public_id", table_name="vendor_items")
    op.drop_index("ix_vendor_items_tenant_vendor_id", table_name="vendor_items")
    op.drop_index("ix_vendor_items_tenant_normalized_canonical_name", table_name="vendor_items")
    op.drop_index("ix_vendor_items_tenant_default_storage_location_id", table_name="vendor_items")
    op.drop_index("ix_vendor_items_tenant_category_id", table_name="vendor_items")
    op.drop_index(op.f("ix_vendor_items_vendor_id"), table_name="vendor_items")
    op.drop_index(op.f("ix_vendor_items_tenant_id"), table_name="vendor_items")
    op.drop_index(op.f("ix_vendor_items_public_id"), table_name="vendor_items")
    op.drop_index(op.f("ix_vendor_items_default_storage_location_id"), table_name="vendor_items")
    op.drop_index(op.f("ix_vendor_items_category_id"), table_name="vendor_items")
    op.drop_table("vendor_items")
