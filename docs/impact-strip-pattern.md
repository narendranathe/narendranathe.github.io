# Impact Strip — quantified-impact ledger pattern

A small accessible HTML+CSS pattern for displaying 3-5 quantified-impact metrics on a project card. Designed to be senior-engineer-credible and copy-pasteable into any portfolio (Hugo, Jekyll, Next.js, Astro, vanilla HTML).

> **Why this exists:** Project cards on most portfolios are descriptive only — recruiters can't distinguish a 200-LOC weekend project from a 40-endpoint production system in 30 seconds. This pattern fixes that without making cards look like sales decks.

**Status: `v0.1.0-experimental`.** Used in production at `narendranathe.github.io`. Class names may change before v1.

---

## The HTML

```html
<h3 id="card-myproject">My Project</h3>
<dl class="impact-strip" aria-labelledby="card-myproject">
  <div class="impact-stat">
    <dt class="impact-value">40+</dt>
    <dd class="impact-label">
      FastAPI endpoints
      <span class="sr-only"> — verified by counting @router decorators in the backend.</span>
    </dd>
  </div>
  <div class="impact-stat">
    <dt class="impact-value">190</dt>
    <dd class="impact-label">
      automated tests
      <span class="sr-only"> — pytest collect-only on the backend tests directory returns 190.</span>
    </dd>
  </div>
  <!-- 3-5 stats max per card -->
</dl>
```

**Why `<dl>` not `<ul>`** — value/label is a term/definition pair. Screen readers announce `<dl>` as "term, definition" preserving the relationship; `<ul>` flattens it to a list of disconnected strings. WCAG 1.3.1 (Info and Relationships).

**Why `aria-labelledby` not `aria-label`** — the strip's accessible name is the project heading right above. `aria-labelledby="card-myproject"` reuses the heading text; `aria-label="Quantified impact for X"` makes screen readers announce the project name twice. WCAG 2.4.6 (Headings and Labels).

**Why `<span class="sr-only">` inside `<dd>`** — provenance ("how did you arrive at this number?") must be available to screen-reader users, not just sighted developers inspecting the source. Placing it inside `<dd>` keeps the `<dl>` content model valid (only `<dt>`/`<dd>` directly inside `<dl>` group wrappers) and makes the description announce in document order after the visible label.

---

## The CSS

```css
.impact-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1.5rem;
  margin: 0 0 1.1rem;
  padding: 0;
  list-style: none;
}

.impact-strip > .impact-stat {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.05rem;
  margin: 0;
  padding: 0.1rem 0 0.1rem 0.6rem;
  border-left: 2px solid var(--accent-warm, #b5752a);
  min-width: 0;
  overflow-wrap: anywhere;
}

.impact-strip .impact-value {
  margin: 0;
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-weight: 600;
  font-size: 1.05rem;
  line-height: 1.2;
  color: var(--fg, #1a1818);
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum" 1;
}

.impact-strip .impact-label {
  margin: 0;
  font-size: 0.74rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--fg-muted, #9b9490);
  line-height: 1.3;
}

.impact-strip .sr-only {
  position: absolute;
  width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0, 0, 0, 0);
  white-space: nowrap; border: 0;
}

@media (min-width: 600px) {
  /* Keep value+label paired (no wrap mid-stat) on desktop; allow wrap
     on smaller viewports per WCAG 1.4.10 (reflow). */
  .impact-strip > .impact-stat {
    white-space: nowrap;
    flex-shrink: 0;
  }
}

@media (prefers-color-scheme: dark) {
  .impact-strip .impact-value { color: var(--fg, #f0f0f0); }
  .impact-strip .impact-label { color: var(--fg-muted, #c0c0c0); }
}

@media print {
  .impact-strip > .impact-stat { border-left-color: #000; }
  .impact-strip .impact-value,
  .impact-strip .impact-label { color: #000; }
}
```

### Why these CSS choices

- **`border-left: 2px solid var(--accent-warm)`** — deliberately distinct from `.chip` (rounded pill, filled background). The eye reads it as "evidence ledger" instead of "another chip row." The brand-color rule ties the strip to the rest of the site palette.
- **`font-variant-numeric: tabular-nums`** — prevents Cumulative Layout Shift on font-swap. When JetBrains Mono swaps in over the proportional fallback, tabular widths stay consistent.
- **`flex-shrink: 0` only on `>= 600px`** — desktop keeps each stat tight; below 600px, allow wrap so iPhone SE (320px) doesn't horizontal-scroll. WCAG 1.4.10 (reflow).
- **CSS custom properties (`var(--fg, fallback)`)** — adopters' design tokens override the defaults without forking the rule.

---

## Conventions

### 3-5 stats per card. No padding.

More than 5 reads as a sales deck. Fewer than 3 reads as undersold. Aim for 3-5 per card. **Weaker projects should get fewer stats, not label-padding.** Uneven counts across cards is a signal — recruiters notice.

### Numbers > tech labels.

The strip should contain quantified facts (counts, percentages, throughput, scale). Tech labels (`Kafka`, `MLflow`, `FastAPI`) belong in a separate "tech chips" surface. A strip with `190 tests` next to `Kafka + Spark` muddles signal — the recruiter weights both equally and the test-suite gets undersold.

If a project has no quantified scale, **no strip is better than a weak strip.** It is acceptable for a card to have no impact strip.

### Defensible provenance.

Every stat must be back-up-able under interview pressure. The `<span class="sr-only">` inside the `<dd>` documents the verification path:

- Good: `pytest collect-only on the backend tests returns 190`
- Good: `eleven content-script adapters live in the extension's ats/ directory`
- Bad: `190 tests in tailor-resume`  (vague — what command? where?)
- Bad: `$0/month`  (every system has a real cost — reads as naive on every onsite loop)
- Bad: untimed cumulative counters like `95+ resumes generated` without a window

### Avoid these specific anti-patterns

- **Sub-ms latency without a load-test artifact.** "Sub-ms P99" is the most-probed claim in any ML platform interview. Don't claim it without a documented locust/k6 report in the repo.
- **`$0/month` cost claims.** Reads as naive. Use `free-tier hosted` or omit.
- **Untimed cumulative counters.** Drift upward over time and look vain. Either window-bound (`95+ in 12mo`) or omit.

---

## Mobile + a11y checklist

- [ ] At 320px viewport width, no horizontal scroll
- [ ] At 200% zoom on a 320px viewport, no horizontal scroll
- [ ] CLS = 0 on font-swap (verify `font-variant-numeric: tabular-nums` is set)
- [ ] Each card's `<h3 id="...">` has a unique ID; `aria-labelledby` resolves to it
- [ ] AAA contrast (verify with `axe` or Lighthouse)
- [ ] No `style=` attribute on any strip element (forces CSS class usage)

---

## Tests

The reference repo includes [`scripts/test-portfolio.py`](../scripts/test-portfolio.py) — 17 structural assertions covering presence, semantic primitive (`<dl>` not `<ul>`), `aria-labelledby` linkage, no scrapped-project claims, no inline styles, JetBrains Mono loaded, mobile breakpoint, dark + print blocks, page-wide ID uniqueness, and the warm-palette token contract.

```bash
python scripts/test-portfolio.py --self-test
```

Wired into CI ([`.github/workflows/resume-self-test.yml`](../.github/workflows/resume-self-test.yml)) so regressions fail the build.

---

## Adopting in your own portfolio

1. Copy the CSS module into your stylesheet.
2. Pick a project card; assign its `<h3>` a unique `id`.
3. Add the `<dl class="impact-strip" aria-labelledby="<h3-id>">` block.
4. Author 3-5 stats following the conventions above.
5. Validate: every stat must survive a 10-second follow-up question. If it can't, cut it.

Two CSS custom properties are the override surface: `--accent-warm` for the rule color, `--fg` and `--fg-muted` for text. If your site uses different token names, map them at the strip CSS layer or wrap your tokens in a `:root` override.
