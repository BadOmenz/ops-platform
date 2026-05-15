from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ItemCategory(Base):
    __tablename__ = "item_categories"
    __table_args__ = (
        CheckConstraint(
            "parent_id IS NULL OR parent_id <> id",
            name="ck_item_categories_not_own_parent",
        ),
        Index("ix_item_categories_tenant_parent_id", "tenant_id", "parent_id"),
        Index("uq_item_categories_public_id", "public_id", unique=True),
        Index(
            "uq_item_categories_tenant_active_parent_name",
            "tenant_id",
            "parent_id",
            "normalized_name",
            unique=True,
            postgresql_where=text("is_active IS TRUE AND parent_id IS NOT NULL"),
        ),
        Index(
            "uq_item_categories_tenant_active_top_name",
            "tenant_id",
            "normalized_name",
            unique=True,
            postgresql_where=text("is_active IS TRUE AND parent_id IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    public_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        default=uuid4,
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id"), index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("item_categories.id"),
        nullable=True,
        index=True,
    )
    display_name: Mapped[str] = mapped_column(String(255))
    normalized_name: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )
