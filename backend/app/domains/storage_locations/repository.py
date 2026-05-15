from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.storage_locations.models import StorageLocation


class StorageLocationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_locations(
        self,
        tenant_id: UUID,
        status_filter: str,
        storage_type: str | None,
    ) -> list[StorageLocation]:
        statement = (
            select(StorageLocation)
            .where(StorageLocation.tenant_id == tenant_id)
            .order_by(func.lower(StorageLocation.display_name))
        )
        if status_filter != "all":
            statement = statement.where(StorageLocation.is_active.is_(status_filter == "active"))
        if storage_type is not None:
            statement = statement.where(StorageLocation.storage_type == storage_type)
        return list(self.session.scalars(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> StorageLocation | None:
        statement = select(StorageLocation).where(
            StorageLocation.tenant_id == tenant_id,
            StorageLocation.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_active_by_normalized_name(
        self,
        tenant_id: UUID,
        normalized_name: str,
    ) -> StorageLocation | None:
        statement = select(StorageLocation).where(
            StorageLocation.tenant_id == tenant_id,
            StorageLocation.normalized_name == normalized_name,
            StorageLocation.is_active.is_(True),
        )
        return self.session.scalar(statement)

    def add(self, location: StorageLocation) -> StorageLocation:
        self.session.add(location)
        self.session.flush()
        self.session.refresh(location)
        return location

    def save(self, location: StorageLocation) -> StorageLocation:
        self.session.flush()
        self.session.refresh(location)
        return location
