"""simplify organization contacts

Revision ID: 20260506_0004
Revises: 20260506_0003
Create Date: 2026-05-06
"""

from collections.abc import Sequence

from alembic import op


revision: str = "20260506_0004"
down_revision: str | None = "20260506_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS main_phone varchar(100)")
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS main_email varchar(255)")
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS website varchar(255)")
    op.execute(
        """
        DO $$
        BEGIN
            IF to_regclass('organization_details') IS NOT NULL
               AND to_regclass('organization_detail_types') IS NOT NULL THEN
                UPDATE organizations AS org
                SET main_phone = COALESCE(org.main_phone, detail_values.value)
                FROM (
                    SELECT DISTINCT ON (od.organization_id) od.organization_id, od.value
                    FROM organization_details od
                    JOIN organization_detail_types odt
                      ON od.organization_detail_type_id = odt.id
                    WHERE odt.name = 'main phone'
                      AND od.is_active IS TRUE
                    ORDER BY od.organization_id, od.is_primary DESC, od.created_at ASC
                ) AS detail_values
                WHERE org.id = detail_values.organization_id;

                UPDATE organizations AS org
                SET main_email = COALESCE(org.main_email, detail_values.value)
                FROM (
                    SELECT DISTINCT ON (od.organization_id) od.organization_id, od.value
                    FROM organization_details od
                    JOIN organization_detail_types odt
                      ON od.organization_detail_type_id = odt.id
                    WHERE odt.name = 'main email'
                      AND od.is_active IS TRUE
                    ORDER BY od.organization_id, od.is_primary DESC, od.created_at ASC
                ) AS detail_values
                WHERE org.id = detail_values.organization_id;

                UPDATE organizations AS org
                SET website = COALESCE(org.website, detail_values.value)
                FROM (
                    SELECT DISTINCT ON (od.organization_id) od.organization_id, od.value
                    FROM organization_details od
                    JOIN organization_detail_types odt
                      ON od.organization_detail_type_id = odt.id
                    WHERE odt.name = 'website'
                      AND od.is_active IS TRUE
                    ORDER BY od.organization_id, od.is_primary DESC, od.created_at ASC
                ) AS detail_values
                WHERE org.id = detail_values.organization_id;
            END IF;
        END $$;
        """
    )
    op.execute("DROP TABLE IF EXISTS organization_details")
    op.execute("DROP TABLE IF EXISTS organization_detail_types")


def downgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organization_detail_types (
            id uuid PRIMARY KEY,
            name varchar(100) NOT NULL UNIQUE,
            data_type varchar(50) NOT NULL,
            is_active boolean NOT NULL DEFAULT true
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS organization_details (
            id uuid PRIMARY KEY,
            tenant_id uuid NOT NULL REFERENCES tenants(id),
            organization_id uuid NOT NULL REFERENCES organizations(id),
            organization_detail_type_id uuid NOT NULL REFERENCES organization_detail_types(id),
            value text NOT NULL,
            value_normalized text NOT NULL,
            notes text NULL,
            is_primary boolean NOT NULL DEFAULT false,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NULL
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_organization_details_tenant_id ON organization_details (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_organization_details_organization_id ON organization_details (organization_id)"
    )
    op.execute("ALTER TABLE organizations DROP COLUMN IF EXISTS website")
    op.execute("ALTER TABLE organizations DROP COLUMN IF EXISTS main_email")
    op.execute("ALTER TABLE organizations DROP COLUMN IF EXISTS main_phone")
