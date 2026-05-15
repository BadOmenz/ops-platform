import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.storage_locations.models import StorageLocation
from app.domains.storage_locations.repository import StorageLocationRepository
from app.domains.storage_locations.schemas import (
    StorageLocationCreate,
    StorageLocationStatusFilter,
    StorageLocationType,
    StorageLocationUpdate,
)

STORAGE_LOCATION_TYPES = {"cooler", "freezer", "dry", "ambient", "other"}


def normalize_storage_location_name(display_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", display_name.lower())


class StorageLocationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = StorageLocationRepository(session)

    def list_locations(
        self,
        tenant_id: UUID,
        status_filter: StorageLocationStatusFilter,
        storage_type: StorageLocationType | None,
    ) -> list[dict]:
        return [
            self._build_location_response(location)
            for location in self.repository.list_locations(tenant_id, status_filter, storage_type)
        ]

    def create_location(self, tenant_id: UUID, payload: StorageLocationCreate) -> dict:
        display_name, normalized_name = self._prepare_display_name(payload.display_name)
        storage_type = self._prepare_storage_type(payload.storage_type)
        self._ensure_unique_active_name(tenant_id, normalized_name)

        location = StorageLocation(
            tenant_id=tenant_id,
            display_name=display_name,
            normalized_name=normalized_name,
            storage_type=storage_type,
        )

        try:
            location = self.repository.add(location)
            self.session.commit()
            self.session.refresh(location)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_exception() from exc

        return self._build_location_response(location)

    def update_location(
        self,
        tenant_id: UUID,
        public_id: UUID,
        payload: StorageLocationUpdate,
    ) -> dict:
        location = self._get_location_or_404(tenant_id, public_id)
        update_data = payload.model_dump(exclude_unset=True)

        next_normalized_name = location.normalized_name
        if "display_name" in update_data:
            display_name, next_normalized_name = self._prepare_display_name(payload.display_name or "")
            location.display_name = display_name
            location.normalized_name = next_normalized_name

        if "storage_type" in update_data and payload.storage_type is not None:
            location.storage_type = self._prepare_storage_type(payload.storage_type)

        if "is_active" in update_data:
            location.is_active = bool(payload.is_active)

        if location.is_active and ("display_name" in update_data or "is_active" in update_data):
            self._ensure_unique_active_name(tenant_id, next_normalized_name, location.id)

        try:
            location = self.repository.save(location)
            self.session.commit()
            self.session.refresh(location)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_exception() from exc

        return self._build_location_response(location)

    def deactivate_location(self, tenant_id: UUID, public_id: UUID) -> dict:
        location = self._get_location_or_404(tenant_id, public_id)
        location.is_active = False
        location = self.repository.save(location)
        self.session.commit()
        return self._build_location_response(location)

    def _get_location_or_404(self, tenant_id: UUID, public_id: UUID) -> StorageLocation:
        location = self.repository.get_by_public_id(tenant_id, public_id)
        if location is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage location not found.",
            )
        return location

    def _prepare_display_name(self, display_name: str) -> tuple[str, str]:
        prepared_name = display_name.strip()
        if not prepared_name:
            raise HTTPException(status_code=422, detail="Storage location display name is required.")
        normalized_name = normalize_storage_location_name(prepared_name)
        if not normalized_name:
            raise HTTPException(
                status_code=422,
                detail="Storage location display name must contain at least one letter or number.",
            )
        return prepared_name, normalized_name

    def _prepare_storage_type(self, storage_type: str) -> str:
        prepared_type = storage_type.strip().lower()
        if prepared_type not in STORAGE_LOCATION_TYPES:
            raise HTTPException(
                status_code=422,
                detail="Storage type must be one of: cooler, freezer, dry, ambient, other.",
            )
        return prepared_type

    def _ensure_unique_active_name(
        self,
        tenant_id: UUID,
        normalized_name: str,
        current_id: int | None = None,
    ) -> None:
        existing = self.repository.get_active_by_normalized_name(tenant_id, normalized_name)
        if existing is not None and existing.id != current_id:
            raise self._duplicate_exception()

    def _duplicate_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active storage location with this name already exists for this tenant.",
        )

    def _build_location_response(self, location: StorageLocation) -> dict:
        return {
            "public_id": location.public_id,
            "tenant_id": location.tenant_id,
            "display_name": location.display_name,
            "normalized_name": location.normalized_name,
            "storage_type": location.storage_type,
            "is_active": location.is_active,
            "created_at": location.created_at,
            "updated_at": location.updated_at,
        }
