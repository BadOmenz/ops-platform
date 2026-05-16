# Vendor Items Initial Build Plan

## Goal

Build the first supervised implementation slice for `vendor_items`, representing actual supplier purchasable items. This slice should establish the core operational table, tenant-scoped backend domain, and compact setup/admin frontend workflow without introducing `products`, `canonical_items`, yield logic, recipe integration, inventory integration, AI automation, or optimization engines.

`vendor_items.canonical_name` is the current operational grouping identity for similar purchasable items across vendors. If that grouping later becomes too entity-like, it may be promoted into `canonical_items`, but that is explicitly out of scope for this build.

## Architectural Constraints

- Follow the standard backend domain structure under `backend/app/domains/vendor_items/`.
- Keep all access tenant-scoped through tenant context dependencies.
- Never expose internal integer IDs through APIs or frontend state.
- Use `public_id` values externally, including for related vendor, item category, and storage location references.
- Resolve related records internally from `public_id` where applicable.
- Do not create a `products` table.
- Do not create a `canonical_items` table.
- Generate `normalized_canonical_name` server-side.
- Treat legacy/FileMaker or Project04 `products` references as loose domain inspiration only. Modernize naming, remove redundancy, and use clean snake_case.

## Proposed First-Slice Schema

### First-Slice Required

- `id`: internal primary key; never exposed.
- `public_id`: external UUID.
- `tenant_id`: required tenant owner.
- `vendor_id`: required vendor owner, resolved from vendor `public_id` at API boundaries.
- `vendor_description`: required supplier-facing item description.
- `canonical_name`: required operational grouping name.
- `normalized_canonical_name`: required server-generated normalized grouping value.
- `is_active`: active/inactive lifecycle flag.
- `created_at`: audit timestamp.
- `updated_at`: audit timestamp.

Suggested indexes/constraints for first slice:

- unique `public_id`
- tenant/vendor index for lists and lookup
- tenant/normalized canonical name index for grouping and filtering
- unique active `vendor_item_code` per tenant/vendor when `vendor_item_code` is present

### Useful But Nullable

These should be considered for the first implementation if they fit without bloating the slice:

- `vendor_item_code`: supplier SKU/code; nullable, unique per tenant/vendor when present.
- `category_id`: optional item category assignment.
- `default_storage_location_id`: optional default storage location assignment.
- `purchase_unit`: purchasing unit label, such as case, each, kg, lb, bag, or box.
- `pack_size`: package size amount or text depending on final type decision.
- `pack_unit`: package unit label.
- `case_quantity`: quantity per case.
- `case_unit`: unit for `case_quantity`.
- `last_price`: last known unit/case price.
- `last_price_date`: date of last known price.
- `estimated_price`: planning estimate when no confirmed price exists.
- `price_unit`: unit the price applies to.
- `notes`: operational notes.

Column-name refinements:

- Prefer `vendor_item_code` over `sku` because vendor codes are not always true SKUs.
- Prefer `vendor_description` over `product_name` or `item_name` because it preserves supplier wording separately from `canonical_name`.
- Consider `purchase_unit` plus `pack_size`/`pack_unit` instead of a single overloaded package description.
- Consider `price_unit` rather than `unit_price_unit` for readability.

### Future/Deferred

Defer these unless the first UI clearly needs them:

- `order_increment`
- `minimum_order_quantity`
- `minimum_order_value`
- `price_notes`
- `quality_tier`
- `preference_rank`
- `is_preferred`
- `storage_impact`
- `availability_notes`
- yield relationships and `vendor_item_yields`
- AI classification confidence, source, or suggestion metadata
- supplier choice optimization fields
- recipe/inventory integration fields

## Relationships

- `vendor_items` belongs to a tenant.
- `vendor_items` belongs to a vendor.
- `vendor_items` optionally belongs to an item category.
- `vendor_items` optionally belongs to a storage location.

Relationship validation should confirm that vendor, category, and storage location records belong to the same tenant. Inactive category/storage behavior should be explicitly decided before implementation.

## Backend Files Expected Later

```text
backend/app/domains/vendor_items/
  __init__.py
  models.py
  schemas.py
  repository.py
  service.py
  router.py
```

Expected backend shape:

- `models.py`: table definition, indexes, foreign keys, audit fields.
- `schemas.py`: create/update/read/list contracts using public UUIDs externally.
- `repository.py`: tenant-scoped queries and persistence only.
- `service.py`: normalization, duplicate checks, related-record validation, lifecycle rules.
- `router.py`: thin tenant-scoped HTTP routes using `TenantContext`.

## Frontend Files Expected Later

Use the existing feature naming convention:

```text
frontend/src/features/vendorItems/
  api.ts
  types.ts
  components/
  hooks/
```

The UI may be reachable from setup and from a vendor workspace, but the feature should own its API/types/workflow state.

## Validation Rules

- `vendor_description` is required.
- `canonical_name` is required.
- `normalized_canonical_name` is generated server-side from `canonical_name`.
- `vendor_id` is required internally and should be resolved from vendor `public_id` externally.
- `tenant_id` is required and comes from tenant context.
- `vendor_item_code` is optional but unique per tenant/vendor when present.
- Category assignment can be nullable in the first slice unless operational review decides it must be required.
- Default storage location can be nullable in the first slice unless operational review decides it must be required.
- Referenced category/storage location must belong to the same tenant.
- Decide whether inactive categories/storage locations can remain referenced on existing items, and whether new assignments must require active records.
- No API response should expose internal integer IDs.
- No `products` table.

## UX Notes

- Match the compact setup/admin UX already used by item categories and storage locations.
- Use dense rows, practical fields, direct filters, and alphabetical ordering.
- Avoid dashboard-heavy ERP layouts.
- Support grouping/filtering by vendor and canonical name.
- Keep hierarchy shallow; `canonical_name` grouping is visual/operational, not a separate database hierarchy.
- Plan for a future comparison workspace for similar supplier items grouped by `normalized_canonical_name`.
- Replace any user-facing "Vendor Products" placeholder language with "Vendor Items" during implementation.

## Open Questions

- Should `category_id` be required in the first slice, or nullable until classification workflows mature?
- Should `default_storage_location_id` be required in the first slice, or nullable while setup data is incomplete?
- Should `pack_size` and quantity fields be numeric, text, or split into amount/unit pairs for the first slice?
- Should `last_price` and `estimated_price` use `Numeric(12, 4)` or another precision?
- Should price metadata live directly on `vendor_items` initially, or later move into price history once workflows demand it?
- Should inactive vendors block new active vendor items?
- Should deactivating a vendor item preserve uniqueness conflicts only among active rows?

## Completion Checklist

- Confirm first-slice columns and deferred columns before coding.
- Confirm nullable vs required behavior for category and default storage location.
- Confirm package/price field types and precision.
- Add Alembic migration only after schema decision is approved.
- Add backend domain files following the standard domain structure.
- Add tenant-scoped list/get/create/update/deactivate/reactivate routes.
- Ensure API contracts use public UUIDs only.
- Add duplicate and tenant-isolation tests.
- Add frontend feature files under `frontend/src/features/vendorItems/`.
- Add compact setup/admin UI with grouping/filtering.
- Rename existing vendor workspace placeholder from products to vendor items.
- Verify backend tests and frontend build.

## Backend First-Slice Implementation Notes

Files created:

- `backend/app/domains/vendor_items/__init__.py`
- `backend/app/domains/vendor_items/models.py`
- `backend/app/domains/vendor_items/schemas.py`
- `backend/app/domains/vendor_items/repository.py`
- `backend/app/domains/vendor_items/service.py`
- `backend/app/domains/vendor_items/router.py`
- `backend/migrations/versions/20260516_0009_vendor_items.py`
- `backend/tests/test_vendor_items_api.py`

Files updated:

- `backend/app/main.py`
- `backend/migrations/env.py`

Decisions made:

- Backend create/update payloads use `vendor_public_id`, `category_public_id`, and `default_storage_location_public_id` externally.
- Responses expose related public IDs and display names, never internal integer IDs.
- `normalized_canonical_name` is generated in the service layer using the existing lowercase/alphanumeric normalization pattern.
- `category_id` and `default_storage_location_id` are nullable.
- New category/storage assignments require active records.
- Existing category/storage references can remain after deactivation, but reactivation validates active references.
- Inactive vendors cannot receive new active vendor items, and reactivation requires an active vendor.
- `pack_size`, `case_quantity`, `last_price`, and `estimated_price` use `Numeric(12, 4)` and non-negative service/database validation.

Tests run:

- `backend\venv\Scripts\python.exe -m py_compile backend\app\main.py backend\migrations\env.py backend\app\domains\vendor_items\models.py backend\app\domains\vendor_items\schemas.py backend\app\domains\vendor_items\repository.py backend\app\domains\vendor_items\service.py backend\app\domains\vendor_items\router.py backend\tests\test_vendor_items_api.py`
- From `backend/`: `venv\Scripts\python.exe -m pytest tests\test_vendor_items_api.py`
- From `backend/`: `venv\Scripts\python.exe -m pytest tests`

Open questions:

- Frontend setup/admin implementation remains pending.
- Existing vendor response still exposes `id`; vendor items intentionally do not copy that behavior.

## Frontend First-Slice Implementation Notes

Files created:

- `frontend/src/features/vendorItems/api.ts`
- `frontend/src/features/vendorItems/types.ts`
- `frontend/src/features/vendorItems/hooks/useVendorItems.ts`
- `frontend/src/features/vendorItems/components/VendorItemsPanel.tsx`

Files updated:

- `frontend/src/app/App.tsx`
- `frontend/src/app/styles.css`
- `frontend/src/features/vendors/components/VendorWorkspace.tsx`

Decisions made:

- Added a global `Vendor Items` workspace as a primary navigation entry.
- Replaced the vendor workspace placeholder with a vendor-scoped `VendorItemsPanel`.
- Shared one vendor items feature module across global and vendor-scoped entry points.
- Global mode allows vendor, canonical name, category, storage location, and status filtering.
- Vendor-scoped mode fixes `vendor_public_id` and does not ask the user to choose a vendor.
- Create/edit forms use public IDs only and allow nullable category/storage assignments.
- New category/storage assignment choices come from active setup records.
- Update payloads send only changed fields so existing inactive category/storage references can remain untouched.
- Reactivation uses the explicit backend reactivation endpoint.

Checks run:

- From `frontend/`: `npm run build`

Remaining open questions:

- No browser smoke test was performed in this implementation pass.
- Future UX polish may split the dense form into sections or tabs if the field count becomes cumbersome.
