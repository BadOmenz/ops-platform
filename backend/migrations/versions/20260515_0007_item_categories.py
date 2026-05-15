"""item categories

Revision ID: 20260515_0007
Revises: 20260515_0006
Create Date: 2026-05-15
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260515_0007"
down_revision: str | None = "20260515_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "item_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("parent_id IS NULL OR parent_id <> id", name="ck_item_categories_not_own_parent"),
        sa.ForeignKeyConstraint(["parent_id"], ["item_categories.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_item_categories_parent_id"), "item_categories", ["parent_id"], unique=False)
    op.create_index(op.f("ix_item_categories_public_id"), "item_categories", ["public_id"], unique=False)
    op.create_index(op.f("ix_item_categories_tenant_id"), "item_categories", ["tenant_id"], unique=False)
    op.create_index("ix_item_categories_tenant_parent_id", "item_categories", ["tenant_id", "parent_id"], unique=False)
    op.create_index("uq_item_categories_public_id", "item_categories", ["public_id"], unique=True)
    op.create_index(
        "uq_item_categories_tenant_active_parent_name",
        "item_categories",
        ["tenant_id", "parent_id", "normalized_name"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE AND parent_id IS NOT NULL"),
    )
    op.create_index(
        "uq_item_categories_tenant_active_top_name",
        "item_categories",
        ["tenant_id", "normalized_name"],
        unique=True,
        postgresql_where=sa.text("is_active IS TRUE AND parent_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_item_categories_tenant_active_top_name",
        table_name="item_categories",
        postgresql_where=sa.text("is_active IS TRUE AND parent_id IS NULL"),
    )
    op.drop_index(
        "uq_item_categories_tenant_active_parent_name",
        table_name="item_categories",
        postgresql_where=sa.text("is_active IS TRUE AND parent_id IS NOT NULL"),
    )
    op.drop_index("uq_item_categories_public_id", table_name="item_categories")
    op.drop_index("ix_item_categories_tenant_parent_id", table_name="item_categories")
    op.drop_index(op.f("ix_item_categories_tenant_id"), table_name="item_categories")
    op.drop_index(op.f("ix_item_categories_public_id"), table_name="item_categories")
    op.drop_index(op.f("ix_item_categories_parent_id"), table_name="item_categories")
    op.drop_table("item_categories")
