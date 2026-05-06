"""organizations foundation

Revision ID: 20260506_0002
Revises: 20260506_0001
Create Date: 2026-05-06
"""

from collections.abc import Sequence
from uuid import UUID

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260506_0002"
down_revision: str | None = "20260506_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organization_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_unique_constraint("uq_organization_types_name", "organization_types", ["name"])

    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("display_name_normalized", sa.String(length=255), nullable=False),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("main_phone", sa.String(length=100), nullable=True),
        sa.Column("main_email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "display_name_normalized",
            name="uq_organizations_tenant_display_name_normalized",
        ),
    )
    op.create_index(op.f("ix_organizations_tenant_id"), "organizations", ["tenant_id"], unique=False)

    op.create_table(
        "organization_type_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["organization_type_id"], ["organization_types.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "organization_type_id",
            name="uq_organization_type_assignments_organization_type",
        ),
    )
    op.create_index(
        op.f("ix_organization_type_assignments_tenant_id"),
        "organization_type_assignments",
        ["tenant_id"],
        unique=False,
    )

    organization_types_table = sa.table(
        "organization_types",
        sa.column("id", postgresql.UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        organization_types_table,
        [
            {
                "id": UUID("10000000-0000-0000-0000-000000000001"),
                "name": "company",
                "description": "Registered companies and other incorporated entities",
                "is_active": True,
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000002"),
                "name": "individual",
                "description": "Individual people represented as organizations",
                "is_active": True,
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000003"),
                "name": "nonprofit",
                "description": "Nonprofit and charitable organizations",
                "is_active": True,
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000004"),
                "name": "government",
                "description": "Government agencies and public-sector entities",
                "is_active": True,
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000005"),
                "name": "educational_institution",
                "description": "Schools, colleges, universities, and training institutions",
                "is_active": True,
            },
            {
                "id": UUID("10000000-0000-0000-0000-000000000006"),
                "name": "internal_department",
                "description": "Internal departments or teams represented as entities",
                "is_active": True,
            },
        ],
    )

def downgrade() -> None:
    op.drop_index(
        op.f("ix_organization_type_assignments_tenant_id"),
        table_name="organization_type_assignments",
    )
    op.drop_table("organization_type_assignments")
    op.drop_index(op.f("ix_organizations_tenant_id"), table_name="organizations")
    op.drop_table("organizations")
    op.drop_constraint("uq_organization_types_name", "organization_types", type_="unique")
    op.drop_table("organization_types")
