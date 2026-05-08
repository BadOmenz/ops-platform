# Frontend UI Foundation

The UI direction is a compact enterprise operations tool: dense enough for repeated internal work, polished enough to feel credible, and restrained enough to avoid marketing-site noise.

## Philosophy

- Build for tables, forms, and operational workflows.
- Keep spacing compact and predictable.
- Use subtle borders and surfaces, not decorative effects.
- Preserve a professional light and dark theme.
- Use one restrained blue accent for intentional actions.
- Prefer clarity and scanability over visual novelty.

## Global Styling

Global styling lives in:

```text
frontend/src/app/styles.css
```

The stylesheet defines shared CSS variables for:

- colors
- borders
- control sizing
- spacing
- radius
- shadows/focus
- table surfaces

Prefer changing tokens before adding one-off component styles.

## Theme Rules

The app has a persisted light/dark theme toggle in `App.tsx`.

Rules:

- Do not remove or replace the theme toggle.
- Do not hardcode light-only colors.
- New UI should use existing CSS variables.
- Dark mode borders should stay close to the surface color.
- Focus states must remain visible in both themes.

## Control Style

Controls should be unified:

- buttons, inputs, selects, and textareas share compact heights
- border radius is angular but not sharp
- controls are flat, not raised or pillowy
- hover states are subtle background/border changes
- focus rings are restrained but visible

Avoid:

- oversized buttons
- playful rounded pills for normal controls
- bright blue everywhere
- inconsistent input/select/button sizing

## Spacing and Density

Use compact spacing with enough rhythm to scan:

- table rows should be readable, not bulky
- form rows should align to shared grids
- action buttons should feel like action areas, not random fields
- section dividers should be subtle

## Tables

Tables are first-class UI.

Rules:

- keep headers compact
- make filter rows visually quieter than data rows
- preserve readable row padding
- use soft row dividers
- allow horizontal scrolling when needed instead of crushing content

## Section Labels

Uppercase eyebrow labels are allowed but should stay quiet:

- muted contrast
- moderate weight
- no excessive letter spacing

## What Not To Add

- Tailwind
- component libraries
- gradients/glassmorphism
- decorative blobs/orbs
- marketing landing-page patterns
- large hero typography in operational screens
- disconnected component-specific theme systems
