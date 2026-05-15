# Future Operational Intelligence

This document tracks future AI-assisted operational optimization systems planned for ops-platform.

These features are intentionally deferred until the core operational foundation is stable:
- vendors
- item_categories
- storage_locations
- vendor_items
- ingredients
- recipes
- vendor_item_yields
- ordering automation

The goal is to preserve architectural direction and future opportunity ideas without prematurely implementing them.

---

# Procurement Optimization Engine

Future AI-assisted purchasing optimization system.

Concept:
After ordering automation completes for a future period, the system scans generated purchasing demand for transformation/consolidation opportunities that humans often miss due to operational complexity.

Examples:
- whole chickens vs separate breasts/thighs
- dry beans vs canned beans
- block cheese vs shredded
- whole vegetables vs pre-cut
- whole fish vs fillets

Optimization factors may include:
- usable yield
- labour cost/time
- spoilage/waste
- prep capacity
- storage constraints
- vendor pricing
- menu forecast
- ingredient demand overlap

Example recommendation:
"Buy 42 whole chickens instead of separate parts. Estimated savings after labour: $184."

System philosophy:
AI proposes.
Human approves.
System remembers.

---

# AI-Assisted Yield Estimation

Future system to estimate vendor-item yield profiles automatically.

Purpose:
Reduce massive manual data-entry burden when configuring:
- vendor item yields
- usable quantities
- transformation outputs

Approach:
- AI parses vendor item text
- reference yield data used where available
- deterministic calculations applied where possible
- user reviews/approves low-confidence estimates

Examples:
- lemons 100 ct
- canned beans drained yield
- whole chicken breakdown yield
- dry-to-cooked grain expansion

Long-term goal:
Build proprietary operational yield intelligence dataset.

---

# AI-Assisted Operational Classification

Future AI-assisted setup automation for:
- item categories
- storage locations
- canonical naming
- vendor item normalization

Goal:
Auto-populate likely classifications while showing uncertain/missed items for review.

Example:
Vendor item:
"CHIX BRST BLSL 4KG"

Suggested:
- canonical_name: Chicken Breast, Boneless Skinless
- category: Protein -> Animal -> Poultry
- storage_type: cooler

---

# Canonical Naming Strategy

Current architectural direction:
No products table for now.

Instead:
vendor_items own:
- vendor_description
- canonical_name
- normalized_canonical_name

canonical_name acts as the operational grouping identity across vendors.

This grouping supports:
- reporting
- optimization
- spend analysis
- substitution analysis
- search

without introducing a separate products abstraction layer.

---

# Important Architectural Principle

Usable culinary yield is generally a property of the purchased source form, not an abstract product identity.

Therefore:
yield logic currently belongs closer to:
- vendor_items
- vendor_item_yields

rather than a generic products table.

This decision should be periodically reevaluated as the system evolves.
