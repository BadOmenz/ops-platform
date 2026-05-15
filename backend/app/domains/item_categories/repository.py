from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, aliased

from app.domains.item_categories.models import ItemCategory


class ItemCategoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_categories(
        self,
        tenant_id: UUID,
        status_filter: str,
        parent_public_id: UUID | None,
        top_level_only: bool,
    ) -> list[tuple[ItemCategory, UUID | None, str | None]]:
        parent = aliased(ItemCategory)
        statement = (
            select(ItemCategory, parent.public_id, parent.display_name)
            .outerjoin(parent, parent.id == ItemCategory.parent_id)
            .where(ItemCategory.tenant_id == tenant_id)
            .order_by(func.lower(ItemCategory.display_name))
        )
        if status_filter != "all":
            statement = statement.where(ItemCategory.is_active.is_(status_filter == "active"))
        if parent_public_id is not None:
            parent_category = self.get_by_public_id(tenant_id, parent_public_id)
            if parent_category is None:
                return []
            statement = statement.where(ItemCategory.parent_id == parent_category.id)
        elif top_level_only:
            statement = statement.where(ItemCategory.parent_id.is_(None))
        return list(self.session.execute(statement).all())

    def get_by_public_id(self, tenant_id: UUID, public_id: UUID) -> ItemCategory | None:
        statement = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.public_id == public_id,
        )
        return self.session.scalar(statement)

    def get_by_internal_id(self, tenant_id: UUID, category_id: int) -> ItemCategory | None:
        statement = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.id == category_id,
        )
        return self.session.scalar(statement)

    def get_active_sibling_by_normalized_name(
        self,
        tenant_id: UUID,
        parent_id: int | None,
        normalized_name: str,
    ) -> ItemCategory | None:
        statement = select(ItemCategory).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.normalized_name == normalized_name,
            ItemCategory.is_active.is_(True),
        )
        if parent_id is None:
            statement = statement.where(ItemCategory.parent_id.is_(None))
        else:
            statement = statement.where(ItemCategory.parent_id == parent_id)
        return self.session.scalar(statement)

    def has_children(self, tenant_id: UUID, category_id: int) -> bool:
        statement = select(ItemCategory.id).where(
            ItemCategory.tenant_id == tenant_id,
            ItemCategory.parent_id == category_id,
        )
        return self.session.scalar(statement) is not None

    def add(self, category: ItemCategory) -> ItemCategory:
        self.session.add(category)
        self.session.flush()
        self.session.refresh(category)
        return category

    def save(self, category: ItemCategory) -> ItemCategory:
        self.session.flush()
        self.session.refresh(category)
        return category
