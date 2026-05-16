from datetime import datetime, time
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Time, func, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


WEEKDAY_VALUES = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
WEEKDAY_SQL = "('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')"


class VendorDeliveryRule(Base):
    __tablename__ = "vendor_delivery_rules"
    __table_args__ = (
        CheckConstraint(f"delivery_weekday IN {WEEKDAY_SQL}", name="ck_vendor_delivery_rules_delivery_weekday"),
        CheckConstraint(
            f"order_cutoff_weekday IN {WEEKDAY_SQL}",
            name="ck_vendor_delivery_rules_order_cutoff_weekday",
        ),
        CheckConstraint(
            "lead_time_days IS NULL OR lead_time_days >= 0",
            name="ck_vendor_delivery_rules_lead_time_days_non_negative",
        ),
        CheckConstraint(
            "minimum_order_value IS NULL OR minimum_order_value >= 0",
            name="ck_vendor_delivery_rules_minimum_order_value_non_negative",
        ),
        Index("uq_vendor_delivery_rules_public_id", "public_id", unique=True),
        Index("ix_vendor_delivery_rules_tenant_vendor_id", "tenant_id", "vendor_id"),
        Index(
            "ix_vendor_delivery_rules_tenant_vendor_delivery_weekday",
            "tenant_id",
            "vendor_id",
            "delivery_weekday",
        ),
        Index(
            "uq_vendor_delivery_rules_tenant_vendor_active_schedule",
            "tenant_id",
            "vendor_id",
            "delivery_weekday",
            "order_cutoff_weekday",
            "order_cutoff_time",
            unique=True,
            postgresql_where=text("is_active IS TRUE"),
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
    delivery_weekday: Mapped[str] = mapped_column(String(20))
    order_cutoff_weekday: Mapped[str] = mapped_column(String(20))
    order_cutoff_time: Mapped[time] = mapped_column(Time)
    lead_time_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minimum_order_value: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    delivery_window_start: Mapped[time | None] = mapped_column(Time, nullable=True)
    delivery_window_end: Mapped[time | None] = mapped_column(Time, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )
