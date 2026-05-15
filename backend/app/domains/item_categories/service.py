import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domains.item_categories.models import ItemCategory
from app.domains.item_categories.repository import ItemCategoryRepository
from app.domains.item_categories.schemas import (
    ItemCategoryCreate,
    ItemCategoryParentFilter,
    ItemCategoryStatusFilter,
    ItemCategoryUpdate,
)


def normalize_item_category_name(display_name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", display_name.lower())


class ItemCategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ItemCategoryRepository(session)

    def list_categories(
        self,
        tenant_id: UUID,
        status_filter: ItemCategoryStatusFilter,
        parent_public_id: UUID | None,
        parent_filter: ItemCategoryParentFilter,
    ) -> list[dict]:
        category_rows = self.repository.list_categories(
            tenant_id,
            status_filter,
            parent_public_id,
            parent_filter == "top-level",
        )
        if parent_public_id is not None or parent_filter == "top-level":
            return [
                self._build_category_response(category, response_parent_id, parent_display_name)
                for category, response_parent_id, parent_display_name in category_rows
            ]

        return [
            self._build_category_response(category, response_parent_id, parent_display_name)
            for category, response_parent_id, parent_display_name in self._order_hierarchy(category_rows)
        ]

    def create_category(self, tenant_id: UUID, payload: ItemCategoryCreate) -> dict:
        display_name, normalized_name = self._prepare_display_name(payload.display_name)
        parent = self._resolve_parent(tenant_id, payload.parent_id)
        self._ensure_unique_active_sibling(tenant_id, parent.id if parent else None, normalized_name)

        category = ItemCategory(
            tenant_id=tenant_id,
            parent_id=parent.id if parent else None,
            display_name=display_name,
            normalized_name=normalized_name,
        )

        try:
            category = self.repository.add(category)
            self.session.commit()
            self.session.refresh(category)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_exception() from exc

        return self._build_category_response(
            category,
            parent.public_id if parent else None,
            parent.display_name if parent else None,
        )

    def update_category(self, tenant_id: UUID, public_id: UUID, payload: ItemCategoryUpdate) -> dict:
        category = self._get_category_or_404(tenant_id, public_id)
        update_data = payload.model_dump(exclude_unset=True)

        parent = self._get_parent_by_internal_id(tenant_id, category.parent_id)

        next_parent = parent
        if "parent_id" in update_data:
            next_parent = self._resolve_parent(tenant_id, payload.parent_id)
            if next_parent is not None and next_parent.id == category.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="An item category cannot be its own parent.",
                )
            if next_parent is not None and self.repository.has_children(tenant_id, category.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A parent item category with children cannot be moved under another parent.",
                )
            category.parent_id = next_parent.id if next_parent else None

        next_normalized_name = category.normalized_name
        if "display_name" in update_data:
            display_name, next_normalized_name = self._prepare_display_name(payload.display_name or "")
            category.display_name = display_name
            category.normalized_name = next_normalized_name

        if ("display_name" in update_data or "parent_id" in update_data) and category.is_active:
            existing = self.repository.get_active_sibling_by_normalized_name(
                tenant_id,
                category.parent_id,
                next_normalized_name,
            )
            if existing is not None and existing.id != category.id:
                raise self._duplicate_exception()

        if "is_active" in update_data:
            category.is_active = bool(payload.is_active)
            if category.is_active:
                self._ensure_unique_active_sibling(
                    tenant_id,
                    category.parent_id,
                    category.normalized_name,
                    category.id,
                )

        try:
            category = self.repository.save(category)
            self.session.commit()
            self.session.refresh(category)
        except IntegrityError as exc:
            self.session.rollback()
            raise self._duplicate_exception() from exc

        return self._build_category_response(
            category,
            next_parent.public_id if next_parent else None,
            next_parent.display_name if next_parent else None,
        )

    def deactivate_category(self, tenant_id: UUID, public_id: UUID) -> dict:
        category = self._get_category_or_404(tenant_id, public_id)
        parent = self._get_parent_by_internal_id(tenant_id, category.parent_id)
        category.is_active = False
        category = self.repository.save(category)
        self.session.commit()
        return self._build_category_response(
            category,
            parent.public_id if parent else None,
            parent.display_name if parent else None,
        )

    def _get_category_or_404(self, tenant_id: UUID, public_id: UUID) -> ItemCategory:
        category = self.repository.get_by_public_id(tenant_id, public_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item category not found.",
            )
        return category

    def _resolve_parent(self, tenant_id: UUID, parent_public_id: UUID | None) -> ItemCategory | None:
        if parent_public_id is None:
            return None
        parent = self.repository.get_by_public_id(tenant_id, parent_public_id)
        if parent is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent item category is invalid for this tenant.",
            )
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent item category must be a top-level category.",
            )
        return parent

    def _get_parent_by_internal_id(self, tenant_id: UUID, parent_id: int | None) -> ItemCategory | None:
        if parent_id is None:
            return None
        return self.repository.get_by_internal_id(tenant_id, parent_id)

    def _prepare_display_name(self, display_name: str) -> tuple[str, str]:
        prepared_name = display_name.strip()
        if not prepared_name:
            raise HTTPException(status_code=422, detail="Item category display name is required.")
        normalized_name = normalize_item_category_name(prepared_name)
        if not normalized_name:
            raise HTTPException(
                status_code=422,
                detail="Item category display name must contain at least one letter or number.",
            )
        return prepared_name, normalized_name

    def _ensure_unique_active_sibling(
        self,
        tenant_id: UUID,
        parent_id: int | None,
        normalized_name: str,
        current_id: int | None = None,
    ) -> None:
        existing = self.repository.get_active_sibling_by_normalized_name(
            tenant_id,
            parent_id,
            normalized_name,
        )
        if existing is not None and existing.id != current_id:
            raise self._duplicate_exception()

    def _duplicate_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An active item category with this name already exists under the same parent.",
        )

    def _order_hierarchy(
        self,
        category_rows: list[tuple[ItemCategory, UUID | None, str | None]],
    ) -> list[tuple[ItemCategory, UUID | None, str | None]]:
        parent_rows = [row for row in category_rows if row[0].parent_id is None]
        child_rows = [row for row in category_rows if row[0].parent_id is not None]
        children_by_parent_id: dict[int, list[tuple[ItemCategory, UUID | None, str | None]]] = {}
        for row in child_rows:
            children_by_parent_id.setdefault(row[0].parent_id, []).append(row)

        ordered_rows: list[tuple[ItemCategory, UUID | None, str | None]] = []
        included_child_ids: set[int] = set()
        for parent_row in sorted(parent_rows, key=lambda row: row[0].display_name.lower()):
            ordered_rows.append(parent_row)
            children = sorted(
                children_by_parent_id.get(parent_row[0].id, []),
                key=lambda row: row[0].display_name.lower(),
            )
            ordered_rows.extend(children)
            included_child_ids.update(child[0].id for child in children)

        orphan_rows = [row for row in child_rows if row[0].id not in included_child_ids]
        ordered_rows.extend(sorted(orphan_rows, key=lambda row: row[0].display_name.lower()))
        return ordered_rows

    def _build_category_response(
        self,
        category: ItemCategory,
        parent_public_id: UUID | None,
        parent_display_name: str | None,
    ) -> dict:
        return {
            "public_id": category.public_id,
            "tenant_id": category.tenant_id,
            "parent_id": parent_public_id,
            "parent_display_name": parent_display_name,
            "display_name": category.display_name,
            "normalized_name": category.normalized_name,
            "is_active": category.is_active,
            "created_at": category.created_at,
            "updated_at": category.updated_at,
        }
