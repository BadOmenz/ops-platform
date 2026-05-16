from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VendorItem(Base):
    __tablename__ = "vendor_items"
    __table_args__ = (
        CheckConstraint("pack_size IS NULL OR pack_size >= 0", name="ck_vendor_items_pack_size_non_negative"),
        CheckConstraint("case_quantity IS NULL OR case_quantity >= 0", name="ck_vendor_items_case_quantity_non_negative"),
        CheckConstraint("last_price IS NULL OR last_price >= 0", name="ck_vendor_items_last_price_non_negative"),
        CheckConstraint(
            "estimated_price IS NULL OR estimated_price >= 0",
            name="ck_vendor_items_estimated_price_non_negative",
        ),
        Index("uq_vendor_items_public_id", "public_id", unique=True),
        Index("ix_vendor_items_tenant_vendor_id", "tenant_id", "vendor_id"),
        Index("ix_vendor_items_tenant_normalized_canonical_name", "tenant_id", "normalized_canonical_name"),
        Index("ix_vendor_items_tenant_category_id", "tenant_id", "category_id"),
        Index("ix_vendor_items_tenant_default_storage_location_id", "tenant_id", "default_storage_location_id"),
        Index(
            "uq_vendor_items_tenant_active_vendor_code",
            "tenant_id",
            "vendor_id",
            "vendor_item_code",
            unique=True,
            postgresql_where=text("is_active IS TRUE AND vendor_item_code IS NOT NULL"),
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
    vendor_id: Mapped[UUID] = mapped_column(ForeignKey("vendors.id"), index=True)
    vendor_item_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    vendor_description: Mapped[str] = mapped_column(String(255))
    canonical_name: Mapped[str] = mapped_column(String(255))
    normalized_canonical_name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("item_categories.id"), nullable=True, index=True)
    default_storage_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("storage_locations.id"),
        nullable=True,
        index=True,
    )
    purchase_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pack_size: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    pack_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    case_quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    case_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    last_price_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    price_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )
