"""refine organization identity seed data

Revision ID: 20260506_0003
Revises: 20260506_0002
Create Date: 2026-05-06
"""

from collections.abc import Sequence
from uuid import UUID

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260506_0003"
down_revision: str | None = "20260506_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    organization_types_table = sa.table(
        "organization_types",
        sa.column("id", postgresql.UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000001"))
        .values(
            name="company",
            description="Registered companies and other incorporated entities",
            is_active=True,
        )
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000002"))
        .values(
            name="individual",
            description="Individual people represented as organizations",
            is_active=True,
        )
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000003"))
        .values(
            name="nonprofit",
            description="Nonprofit and charitable organizations",
            is_active=True,
        )
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000004"))
        .values(
            name="government",
            description="Government agencies and public-sector entities",
            is_active=True,
        )
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000005"))
        .values(
            name="educational_institution",
            description="Schools, colleges, universities, and training institutions",
            is_active=True,
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO organization_types (id, name, description, is_active)
            VALUES (
                '10000000-0000-0000-0000-000000000006',
                'internal_department',
                'Internal departments or teams represented as entities',
                true
            )
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                is_active = EXCLUDED.is_active
            """
        )
    )

def downgrade() -> None:
    organization_types_table = sa.table(
        "organization_types",
        sa.column("id", postgresql.UUID),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    op.execute(
        organization_types_table.delete().where(
            organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000006")
        )
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000001"))
        .values(name="vendor", description="Suppliers and vendors", is_active=True)
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000002"))
        .values(name="client", description="Customers and clients", is_active=True)
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000003"))
        .values(name="staff", description="Internal staff", is_active=True)
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000004"))
        .values(name="shipper", description="Shipping and logistics organizations", is_active=True)
    )
    op.execute(
        organization_types_table.update()
        .where(organization_types_table.c.id == UUID("10000000-0000-0000-0000-000000000005"))
        .values(name="instructor", description="Training and instruction organizations", is_active=True)
    )
