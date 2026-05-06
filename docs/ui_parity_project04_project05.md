# UI Parity: Project04 to Project05

This document tracks UI/UX parity between the original `project04_foodservice_ops` organization experience and the rebuilt `project05_ops_platform` organization feature.

The goal is not pixel-perfect copying. The goal is to preserve useful behavior, improve weak patterns, and avoid reintroducing large, hard-to-edit frontend files.

## Current Read

Project05 is architecturally stronger than Project04:

- feature-local API client
- feature-local types
- workflow hook
- split form/table/editor components
- tenant context is explicit
- backend contracts are cleaner

Project05 intentionally simplified the organization identity layer:

- `main_phone`, `main_email`, and `website` are direct organization fields
- generic organization detail rows were removed
- richer contacts should become a dedicated future domain only if needed

## Parity Matrix

| Area | Project04 | Project05 | Status | Recommendation |
| --- | --- | --- | --- | --- |
| Tenant selection | Tenant selector in app shell | Tenant selector in app shell | Ported | Keep Project05 pattern |
| Organization list | Dedicated page with table | Workspace list view | Ported with shell difference | Keep list-first workflow |
| Status filter | active/inactive/all | active/inactive/all | Ported | Keep |
| Table sorting | display name/type/contact/notes | display name/type/contact/notes | Ported | Keep |
| Table filters | display name/type/contact/notes | display name/type/contact/notes | Ported | Keep |
| Clear filters | Present | Present | Ported | Keep |
| Refresh button | Present | Present | Ported | Keep |
| Create form | Name/legal name/type/notes plus detail rows | Name/legal name/contact/type/notes | Simplified | Keep lean identity model |
| Duplicate handling | Specific duplicate messaging | Generic API error message | Partial | Improve duplicate-specific messaging |
| Inactive duplicate reactivation | Project04 planned/handled from API response shape | Not implemented | Missing | Decide whether backend should return inactive duplicate id |
| Organization editor | Click name to details page | Click name to local editor view | Ported with shell difference | Keep |
| Basic field edit | Upper section on details page | Editor view | Ported with change | Add explicit edit/save/cancel state |
| Type assignment | Single type in Project04 UI, backend list shape | Multiple checkboxes | Improved | Keep Project05 multi-type UI |
| Direct contact fields | Generic detail rows | Direct fields | Simplified | Keep |
| Soft delete | Deactivate/reactivate | Deactivate/reactivate | Ported | Keep |
| Empty/loading states | Basic | Basic | Partial | Improve table and editor states |
| Navigation | Local list/detail navigation | Local list/editor view state | Ported with shell difference | Revisit real routing later |

## Highest Priority Gaps

### 1. Explicit Editor State

Project05 fields are always editable in the editor view. That is fast, but it can feel ambiguous.

Needed:

- view mode
- edit mode
- save/cancel controls
- dirty-state handling

### 2. Error Handling

Project05 has a top-level error banner. Project04 had more local error awareness.

Needed:

- duplicate organization message near create/edit form
- field validation messages near relevant controls
- preserve backend as source of truth

### 3. Refresh and Loading Feedback

Project04 had explicit refresh. Project05 now has explicit refresh in the list view.

Still worth improving:

- show loading state in table body
- keep stale data visible during refresh when possible

## Recommended Next UI Slice

Next recommended UI slice: explicit editor state and local error placement.

Target files:

```text
frontend/src/features/organizations/components/OrganizationEditor.tsx
frontend/src/features/organizations/hooks/useOrganizations.ts
frontend/src/features/organizations/types.ts
```

Target behavior:

- selected organization has view/edit mode
- save/cancel controls are obvious
- duplicate and field validation errors appear near the relevant controls
- refresh remains available from the organizations panel

This should be done before adding new domains.

## Intentional Differences To Keep For Now

- Project05 uses UUID `id`, not Project04 `public_id`.
- Project05 supports multiple neutral organization identity classification assignments.
- Project05 uses direct identity contact fields instead of generic organization detail rows.
- Project05 uses local workspace view state rather than a separate route for the editor.
- Project05 keeps API and workflow logic out of page components.

## Decision Needed Later

Should Project05 eventually use real routing for:

```text
/tenants/:tenantId/organizations
/tenants/:tenantId/organizations/:organizationId
```

For now, local workspace state is acceptable. Before Azure/user testing, routing may become useful for refresh, sharing, and browser history.
