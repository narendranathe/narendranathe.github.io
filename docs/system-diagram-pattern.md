# System Diagram - inline SVG architecture pattern

A drop-in pattern for embedding inline SVG architecture diagrams in a portfolio. Designed to be **interview-defensible**, **dark-mode + print + Windows-HCM aware**, and **copy-pasteable** into any vanilla HTML, Hugo, Jekyll, Astro, or Next.js portfolio.

> **Why this exists:** Architecture diagrams shipped as PNG screenshots fail in dark mode, fail in print, fail under forced-colors, and fail when an interviewer asks "where's the diagram source?" Inline SVG with `currentColor` and CSS custom properties solves all four in ~3-6 KB per diagram.

**Status: `v0.1.0-experimental`.** Used in production at `narendranathe.github.io`. Companion to [`impact-strip-pattern.md`](impact-strip-pattern.md).

---

## The HTML — full worked example

A complete 3-stage diagram with one warm-accent box. Paste this whole block into any HTML file alongside the CSS module below — no extra dependencies, no build step.

```html
<figure class="system-diagram-figure"
        aria-labelledby="diagram-mything-title"
        aria-describedby="diagram-mything-desc">
  <!-- font-family is the only place fonts are bound; swap to your site's
       monospace stack (Geist Mono, IBM Plex Mono, etc.) if needed. -->
  <svg class="system-diagram" viewBox="0 0 720 200"
       xmlns="http://www.w3.org/2000/svg" role="img">
    <title id="diagram-mything-title">My system: Producer to Consumer to API</title>
    <desc id="diagram-mything-desc">A producer publishes events to a stream
      consumer at one hundred messages per second. The consumer writes
      aggregates to a downstream API which serves a dashboard.</desc>

    <defs>
      <marker id="arrow-mything" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="7" markerHeight="7" orient="auto-start-reverse">
        <path d="M0 0 L10 5 L0 10 Z" fill="currentColor"/>
      </marker>
    </defs>

    <g fill="none" stroke="currentColor" stroke-width="1.4"
       font-family="'JetBrains Mono', ui-monospace, monospace" font-size="11">
      <!-- Stage 1: Producer (regular box) -->
      <rect x="40" y="60" width="140" height="80" rx="6"/>
      <text x="110" y="86" text-anchor="middle" fill="currentColor" font-weight="600">Producer</text>
      <text x="110" y="106" text-anchor="middle" fill="currentColor" font-size="10">100 msg/s</text>

      <!-- Stage 2: Consumer (warm accent — the heart of the system) -->
      <rect x="220" y="50" width="160" height="100" rx="6"
            stroke="var(--accent-warm, #b5752a)" stroke-width="2"/>
      <text x="300" y="76" text-anchor="middle"
            fill="var(--accent-warm, #b5752a)" font-weight="600">Consumer</text>
      <text x="300" y="96" text-anchor="middle" fill="currentColor" font-size="10">5s tumbling window</text>
      <text x="300" y="112" text-anchor="middle" fill="currentColor" font-size="10">10s watermark</text>

      <!-- Stage 3: API (regular box) -->
      <rect x="420" y="60" width="140" height="80" rx="6"/>
      <text x="490" y="86" text-anchor="middle" fill="currentColor" font-weight="600">API</text>
      <text x="490" y="106" text-anchor="middle" fill="currentColor" font-size="10">REST + WS</text>

      <!-- Edges -->
      <line x1="180" y1="100" x2="220" y2="100" marker-end="url(#arrow-mything)"/>
      <line x1="380" y1="100" x2="420" y2="100" marker-end="url(#arrow-mything)"/>
    </g>
  </svg>
  <figcaption class="post-figcaption">Figure: short caption naming any non-obvious convention (e.g., dashed lines, color emphasis).</figcaption>
</figure>
```

**Why `<figure>` + `aria-labelledby`/`aria-describedby` + `<svg role="img">` + inner `<title>`/`<desc>`** - belt-and-braces for AT compatibility. The `<figure>`'s aria hookup names the figure landmark in browse mode; the SVG's own `role="img"` + `<title>` + `<desc>` names the embedded image in rotor / images-only navigation. Drop one and you regress on either NVDA browse or VoiceOver rotor. WCAG 1.1.1.

**Why namespace IDs (`diagram-mything-*`)** - `aria-labelledby` resolves IDs globally on the page. Two diagrams reusing `diagram-pipeline-*` will collide and the second diagram's accessible name will silently take the first's. Always namespace per diagram.

**Why `<desc>` describes LOGICAL FLOW, not LAYOUT** - "box on the left, three boxes on the right" is useless to SR users and stale the moment the diagram is re-laid-out for mobile. "Producer publishes events; consumer writes aggregates" survives a re-layout and tells the same story.

**Recommended `<desc>` length** - 40-60 words for a 3-4 stage linear pipeline; 70-90 words for a 5-stage diagram with fan-out. Past ~110 words, NVDA users start tabbing away mid-announcement.

**Skip `tabindex="0"` on the SVG** - the `<figure>`'s aria hookup already exposes the title + desc to SR users via figure-landmark navigation. Adding a tab stop with no interactive payoff violates WCAG 2.4.3.

---

## The CSS — full module

```css
/* Inline SVG architecture diagrams. currentColor inheritance means the
   same markup renders correctly in light, dark, print, and forced-colors
   modes. Warm-token highlights are scoped via stroke="var(--accent-warm)". */
.system-diagram-figure {
  margin: 1.5rem 0 1.8rem;
  padding: 0;
}
.system-diagram {
  width: 100%;
  height: auto;
  color: var(--fg, #1a1818);
  display: block;
}
.post-figcaption {
  font-size: 0.78rem;
  color: var(--fg-muted, #6a625e);
  margin-top: 0.5rem;
  font-style: italic;
}

@media (prefers-color-scheme: dark) {
  .system-diagram { color: #f0f0f0; }
  .post-figcaption { color: #b0a8a0; }
}

@media print {
  .system-diagram { color: #000; }
  /* Warm-accent strokes drop to #000 so they meet WCAG 1.4.11 (3:1)
     on a B&W laser printer. var() lookups inside inline SVG cascade
     through this override. */
  .system-diagram { --accent-warm: #000; --fg-muted: #333; }
}

@media (forced-colors: active) {
  /* Windows High Contrast Mode: CSS custom-property warm accents are
     NOT remapped by the OS. Force every stroke + fill inside the
     diagram onto the system CanvasText token so the diagram stays
     readable when the user has selected an accessibility theme. */
  .system-diagram [stroke] { stroke: CanvasText; }
  .system-diagram [fill]:not([fill="none"]) { fill: CanvasText; }
}
```

### Token swap (for adopters who don't use these names)

The CSS uses three CSS custom properties: `--fg`, `--fg-muted`, `--accent-warm`. If your site already exposes design tokens under different names, do a one-pass replace:

| This pattern uses | Swap to your site's token |
|-------------------|---------------------------|
| `var(--fg)`        | `var(--text)`, `var(--ink)`, etc. |
| `var(--fg-muted)`  | `var(--text-secondary)`, `var(--muted)`, etc. |
| `var(--accent-warm)` | `var(--brand-accent)`, `var(--highlight)`, etc. |

Every `var(--name)` in the CSS module above carries a hardcoded fallback (`var(--fg, #1a1818)`) so the diagram still renders if the token is missing entirely. The `@media print` and `@media (forced-colors: active)` blocks are token-agnostic — leave them as-is regardless of your token names.

### Font swap

The font-family lives **inside the SVG markup** (`font-family="'JetBrains Mono', ui-monospace, monospace"`), not in the CSS. To use your own monospace stack, change that one attribute on the parent `<g>` element. The CSS module never touches font-family.

### Why these CSS choices

- **`color: var(--fg)` on the root SVG** - inline SVG inherits `color` from its parent and resolves `currentColor` against it. Light mode reads `--fg`, dark mode is overridden by the `prefers-color-scheme` block, print is overridden by the `@media print` block. One markup, three rendering contracts, zero PNG fallback.
- **`stroke="var(--accent-warm, #b5752a)"` for highlights** - critical-path nodes (the heart of the system, the "this is where the work happens" box) get a warm stroke. The `var()` lookup is overridable by the print block (forces `#000`) and by the forced-colors block (replaced with `CanvasText`).
- **`@media (forced-colors: active)`** - skipping this is the most common a11y bug in inline-SVG diagrams. Windows users on high-contrast themes see a broken diagram because `var(--accent-warm)` survives forced-colors mapping; this block fixes it.
- **`width: 100%; height: auto`** - the `viewBox` is the source of truth for the diagram's coordinate system. CSS scales it to container width and the height follows the aspect ratio. Mobile reflow at 320 px is automatic; no media queries on the SVG itself.

---

## Conventions

### viewBox aspect ratio

Lock `viewBox="0 0 720 H"` for every diagram on the same page. When two diagrams stack vertically with `width: 100%`, sharing a width keeps them visually balanced. Vary `H` to suit the topology:

- 4-stage linear pipeline: `H = 180-200`
- 5-stage with fan-out / sink: `H = 240-260`

Going wider than 720 makes mobile scaling lossy. Going taller than 280 starts to exceed first-fold on a typical laptop.

### Per-diagram byte budget

Aim for **<= 6 KB per diagram, <= 30 KB inline SVG total per page**. The total is tracked by a structural test:

```
inline-svg-byte-total per page <= 30 KB
```

Hand-authored XML stays well under 6 KB for 5 stages. Excalidraw exports start at ~8-15 KB before svgo and embed `<style>` blocks, base64 fonts, and roughjs filter noise that never round-trips cleanly. **Hand-roll the SVG.**

### Reusable `<defs>`

Scope the arrow marker inside its own `<defs>` per `<svg>`. Hoisting to a page-level `<defs>` saves ~80 bytes total but creates two failure modes:
1. ID collision if a future diagram is added with a different arrow style.
2. Self-containment loss - copy-pasting the SVG into a new post silently breaks the arrowheads.

Self-containment is worth 80 bytes. Keep markers local.

### Warm-accent discipline

Reserve `var(--accent-warm)` for **at most one box per diagram** - the critical-path node. Two warm boxes per diagram dilutes the signal and reads as decoration rather than architectural emphasis.

### Defensible labels

Every box label has to survive a 10-second interview follow-up. If a node label says "multi-LLM cascade" but the actual code does a 2-step primary + fallback, **change the label.** Diagrams that lie are worse than diagrams that show messy truth - a senior interviewer notices in 30 seconds.

Honest labels for common architectural realities:
- `FastAPI backend (async, no queue)` not `Microservices`
- `CSV sink` between Spark and a downstream API not `Real-time pipeline`
- `local[2] demo` not `Spark cluster`
- `BYOK Router (primary + fallback)` not `5-step LLM cascade`

### Cuts > additions

If a node doesn't appear in the topology's hot path (rate-limit cache, optional auth provider, internal monitoring), **cut it from the diagram and document it in the `<desc>`.** A 5-stage diagram with 3 sidecars reads as cluttered; a 5-stage diagram with sidecars described in the `<desc>` reads as disciplined.

---

## Adopting in your own portfolio

1. Copy the CSS module into your stylesheet (or paste into a `<style>` block).
2. Identify the project's hot path (3-5 stages from input to output).
3. Author the `<svg>` markup hand by hand, following the box/arrow vocabulary above.
4. Write a 40-90 word `<desc>` describing logical flow, not layout. Enumerate edges in source order.
5. Test in Chrome dev tools `Rendering > Emulate CSS media > prefers-color-scheme: dark`, then print preview, then `Rendering > Emulate forced colors: active`.
6. Validate: every node label survives a 10-second interview follow-up. If it doesn't, cut or rename.

---

## Tests

The reference repo at `narendranathe.github.io` includes structural assertions in `scripts/test-portfolio.py`:

- inline `<svg class="system-diagram">` present in every required location
- each system-diagram `<svg>` has `<title>` + `<desc>`
- each system-diagram `<svg>` uses `currentColor` for fills/strokes (no hardcoded `#hex`)
- total inline `system-diagram` SVG byte budget per page <= 30 KB

```bash
python scripts/test-portfolio.py --self-test
```

Wired into CI so regressions fail the build.
