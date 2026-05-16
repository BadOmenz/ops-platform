# AGENTS.md

This repository is the operational platform for a multi-tenant SaaS application.

The stack is FastAPI, SQLAlchemy, Alembic, PostgreSQL, React/Vite/TypeScript, Docker Compose, Azure App Service, Azure Static Web Apps, and GitHub Actions CI/CD.

## Architecture Rules

- Keep backend domain logic separated under `backend/app/domains/`.
- Use the standard domain shape: `models.py`, `schemas.py`, `repository.py`, `service.py`, and `router.py`.
- Keep frontend code organized by feature modules.
- Prefer clear domain boundaries over shared generic abstractions.
- Do not introduce a `products` table.

## Tenant And Identifier Rules

- Enforce tenant scoping through tenant context dependencies.
- Never expose internal integer IDs through API responses, routes, frontend state, logs intended for users, or external workflows.
- Use external UUID `public_id` values for cross-boundary references.
- Generate operational normalization fields server-side.

## Current Domain Direction

Operational entities include vendors, vendor items, vendor item yields, ingredients, recipes, recipe ingredients, item categories, and storage locations.

`vendor_items` is the next major target. Yield belongs close to purchased vendor items, not abstract products. `canonical_name` acts as the operational grouping identity, with `normalized_canonical_name` generated server-side.

Storage locations are visually grouped by hardcoded storage classifications: `cooler`, `freezer`, `dry`, `ambient`, and `other`. There is no storage-location hierarchy in the database.

## UX Conventions

- Build compact operational admin screens.
- Favor dense rows, grouped rendering, shallow hierarchy, and alphabetical ordering.
- Avoid dashboard-heavy ERP styling.
- Keep setup/navigation workflows direct and utilitarian.

## AI Workflow Conventions

This repository should be the durable working memory for AI tools. Agents should rely on:

- `AGENTS.md`
- `docs/`
- `tasks/`
- `reviews/`
- git history

Do not rely on chat memory as the source of truth. When a decision, task, review, or convention needs to persist across sessions or tools, put it in the repository in the smallest useful form.

This foundation is for supervised, repository-centric AI workflows across Codex, Claude Code, Copilot, and future agents. Keep it practical: prefer small files, clear instructions, and reviewable changes over speculative autonomous-agent systems.
