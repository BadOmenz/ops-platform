# Dual Access Operational Navigation

## Purpose

Major user-facing operational tables should eventually support both global workspace access and contextual drill-down access from parent records.

This keeps dense operational data easy to audit across the whole system while also preserving the user's current work thread when they begin from a specific event, menu, recipe, vendor, or other parent record.

## Why It Matters

Operators often start from a high-level operational surface and need to follow the chain down to the records that explain or fix the work in front of them. They should be able to move from today's events through menus, recipes, ingredients, and matched vendor items without losing context.

The same users also need full global tables for quick lookup, comparison, cleanup, auditing, duplicate resolution, and cross-context investigation.

## Examples

- `vendor_items` should be accessible from a global vendor items workspace and from a vendor detail/workspace as an embedded child table.
- Future event workflows should support drilling from today's events to an event, event menus, recipes, recipe ingredients, and matched vendor items.
- Future recipe and ingredient workflows should allow both global table review and contextual access from menus or recipes.

## Implementation Implications

- Feature modules should own API/types/workflow state so the same operational data can power both global and embedded views.
- Global workspaces should optimize for filtering, comparison, cleanup, and audit workflows.
- Contextual child views should preserve parent context and expose only the controls needed for the current workflow.
- Routes and components should avoid assuming there is only one entry point into a domain.
- Use public IDs across view boundaries and preserve tenant scoping through existing dependencies.

## Risks To Avoid

- Do not build isolated one-off child tables that cannot share behavior with global workspaces.
- Do not force users to leave a high-level workflow just to inspect or fix a child record.
- Do not turn every contextual view into a full dashboard; keep embedded views compact and task-focused.
- Do not create new backend abstractions only for navigation. Let domain boundaries and API contracts stay clean.
