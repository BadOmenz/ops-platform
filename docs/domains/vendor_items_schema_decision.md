# Vendor Items Schema Decision

## Decision

`vendor_items` will represent actual supplier purchasable items. There will be no `products` table and no `canonical_items` table in the first slice. `canonical_name` is required and remains the operational grouping identity; `normalized_canonical_name` is generated server-side.

## First-Slice Columns

Required:

- `id`: internal primary key, never exposed.
- `public_id`: external UUID.
- `tenant_id`: required tenant owner.
- `vendor_id`: required vendor relationship, resolved from vendor `public_id`.
- `vendor_description`: required supplier item description.
- `canonical_name`: required grouping identity.
- `normalized_canonical_name`: required server-generated normalized grouping value.
- `is_active`: lifecycle flag, default true.
- `created_at`
- `updated_at`

Nullable first-slice fields:

- `vendor_item_code`
- `category_id`
- `default_storage_location_id`
- `purchase_unit`
- `pack_size`
- `pack_unit`
- `case_quantity`
- `case_unit`
- `last_price`
- `last_price_date`
- `estimated_price`
- `price_unit`
- `notes`

## Deferred Columns

Defer optimization, preference, ordering, and AI-assist fields:

- `order_increment`
- `minimum_order_quantity`
- `minimum_order_value`
- `price_notes`
- `quality_tier`
- `preference_rank`
- `is_preferred`
- `storage_impact`
- `availability_notes`
- yield relationships
- AI classification metadata
- supplier choice optimization fields

## Types

- UUIDs: match existing PostgreSQL UUID usage.
- `id`: use internal integer if following item category/storage location tables; do not expose it.
- text names/descriptions/units: `String` with practical limits; `notes` as `Text`.
- `pack_size`: `Numeric(12, 4)`, nullable. Irregular package wording belongs in `notes` for now.
- `case_quantity`: `Numeric(12, 4)`, nullable.
- `last_price`: `Numeric(12, 4)`, nullable.
- `estimated_price`: `Numeric(12, 4)`, nullable.
- `last_price_date`: `Date`, nullable.
- units: string fields for now; no unit enum/lookup exists yet.
- money/quantity fields should be non-negative via service validation and, if clean, database check constraints.

## Constraints And Indexes

- Unique `public_id`.
- Index `tenant_id`.
- Index `(tenant_id, vendor_id)`.
- Index `(tenant_id, normalized_canonical_name)`.
- Index `(tenant_id, category_id)`.
- Index `(tenant_id, default_storage_location_id)`.
- Partial unique index on `(tenant_id, vendor_id, vendor_item_code)` where `is_active IS TRUE` and `vendor_item_code IS NOT NULL`.

Duplicate code behavior should match existing active-record patterns: inactive rows may keep historical values, but reactivation must fail if it would violate the active unique constraint.

## Relationships

- Vendor must belong to the same tenant.
- Category must belong to the same tenant when provided.
- Storage location must belong to the same tenant when provided.
- New category/storage assignments require active records.
- Existing references may remain if category/storage records are later deactivated.
- Inactive vendors should block creating new active vendor items.
- Reactivating a vendor item should require its vendor to be active.

## Backend API Shape

Use the standard domain folder:

```text
backend/app/domains/vendor_items/
  __init__.py
  models.py
  schemas.py
  repository.py
  service.py
  router.py
```

Routes should be tenant-scoped and use public UUIDs externally:

- `GET /tenants/{tenant_id}/vendor-items`
- `GET /tenants/{tenant_id}/vendor-items/{vendor_item_public_id}`
- `POST /tenants/{tenant_id}/vendor-items`
- `PATCH /tenants/{tenant_id}/vendor-items/{vendor_item_public_id}`
- `DELETE /tenants/{tenant_id}/vendor-items/{vendor_item_public_id}`
- `POST /tenants/{tenant_id}/vendor-items/{vendor_item_public_id}/reactivate`

List filters:

- `vendor_public_id`
- `canonical_name`
- `category_public_id`
- `storage_location_public_id`
- `status`: `active`, `inactive`, or `all`

Responses must expose related `public_id` values and display names, never internal integer IDs.

## Frontend Screen Shape

Use `frontend/src/features/vendorItems/` to match existing camelCase feature folders.

Recommended first screen:

- compact setup/admin module
- dense table
- edit/create form beside or above results, consistent with item categories and storage locations
- filters for vendor, canonical name, category, storage location, and active status
- sort/group by `canonical_name`, then vendor display name, then vendor description
- use only `public_id` values in frontend state and API calls
- rename existing "Vendor Products" placeholder language to "Vendor Items" during implementation

## Convention Notes

- Existing setup modules use `DELETE` for deactivate and no separate reactivation route; vendor items should add an explicit reactivation endpoint because reactivation must validate vendor/category/storage and active uniqueness.
- Existing vendor response currently exposes `id`; do not copy that into vendor items. This conflicts with `AGENTS.md` and should be treated as a future cleanup for vendors.
- No existing unit enum/lookup or money convention exists, so string units and `Numeric(12, 4)` price/quantity fields are the clean first slice.
