# PRD: Portfolio UI Upgrade — 2026 Inspirations Pass

**Status:** v2 (post-critique, scope-frozen)
**Author:** Naren + Claude
**Branch:** `feat/portfolio-ui-upgrade-2026` (off `feat/portfolio-apex`)
**Date:** 2026-04-28
**Critique round:** 5 parallel agents (UX, Perf, A11y, Senior-eng-signal, Scope) — synthesis below

---

## 0. v2 Changelog

| Change | Rationale | Source critic |
|--------|-----------|---------------|
| **CUT F11** Windows XP mode | Unanimous reject; wrong audience for Senior+ AI roles; ~80KB perf cost; a11y nightmare (2.5.7, 2.1.1, 4.1.2 violations) | All 5 |
| **CUT F9** GitHub contribution graph | Junior cargo-cult signal; senior portfolios show artifacts not commit cadence | Senior-signal |
| **REMOVE H1B line** from hero code panel | Self-sabotage at top-tier sponsoring companies (Anthropic, Google, Stripe, Databricks) | Senior-signal |
| **ADD F-AW** Architecture Write-Ups section | #1 senior-signal addition; Anthropic hires people who write | Senior-signal |
| **ADD F-IS** Quantified Impact Strip per flagship | Numbers > animations | Senior-signal, UX |
| **ADD F-SD** System Diagrams (ExponentHR, Portfolio-Risk) | Senior portfolios show topology | Senior-signal |
| **ADD F-PB** Perf-budget regression test harness | NFR enforcement, not just aspiration | Scope |
| **ADD F-A11Y** A11y regression test harness | Same | Scope, A11y |
| **REFRAME F6** "Coming Up" → "In Design" with linked architecture doc | "TODO" reads weak; "design doc" reads strong | Senior-signal |
| **REFRAME hover-reveals** F2/F3/F4 — on touch, content is always-visible inline (no tap gesture) | Tap-to-toggle competes with primary CTA on mobile | UX |
| **TIGHTEN F1** hand-rolled syntax spans, ~1.6KB; not PrismJS | Stay vanilla, avoid 14KB lib for one snippet | Perf |
| **TIGHTEN F2** AVIF screenshot of resume page 1 (~25KB), not pdf.js | pdf.js = 340KB, kills budget | Perf |
| **TIGHTEN F7** `<details>/<summary>` native; do NOT default-collapse Track Record on mobile | Native a11y; PRD persona contradiction (Rita scans on mobile) | A11y, UX |
| **TIGHTEN F4** copy: "Let's talk." not "Want to talk?" | One register, drops question-mark neediness | UX |
| **MOVE F12** developer-portfolios contribution to a separate post-merge issue, labeled `post-merge`, not in this PRD's scope | Cross-repo, zero shared code with this PRD | Scope |
| **Sequencing rebuilt** | Phase A as drafted shared `<section class="hero">` + `<head>` files, would conflict on merge | Scope |

---

## 1. Problem

The current `narendranathe.github.io` portfolio is a clean, fast 1-page scroll. It signals "competent senior engineer" but does not yet signal "distinctive, top-tier AI Platform candidate" the way reference portfolios from Yubraj Khatri, Dev Zahid, Yassine Erradouani, Maxime Haegeman, and Bjorn Melin do.

For Naren's targeting profile — Senior+ AI / Data / ML Platform roles at H1B-sponsoring companies (Anthropic, OpenAI, Databricks, Google, Microsoft, NVIDIA, Apple, Amazon, Meta, Stripe, Citadel, AQR, Two Sigma, HRT, Bloomberg, JPM, etc.) — the portfolio needs to do three jobs:

1. **Pass the 30-second scan** — recruiters making sponsorship-tier decisions
2. **Earn the 5-minute exploration** — hiring managers evaluating engineering taste
3. **Be memorable enough to share** — the "have you seen this guy's site?" effect

This PRD codifies a set of UI **and content** upgrades. The content upgrades (Architecture Write-Ups, Impact Strips, System Diagrams) are weighted higher than the visual polish, per the senior-signal critique.

## 2. Goals

- **G1.** Add **content depth** that signals senior engineering: architecture write-ups, quantified impact, system diagrams
- **G2.** Add tasteful, restrained micro-interactions that signal frontend craft without crossing into gimmick territory
- **G3.** Add one **memorable signature element** (code-class hero panel + photo favicon) that gives the site a "share this" moment
- **G4.** Add an "In Design" section seeded with the recommendation-engine project, framed as a design doc with tradeoffs (not a TODO)
- **G5.** Hold Lighthouse Perf >= 95, A11y = 100, total page weight increase <= 65KB gzipped

## 3. Non-Goals

- **NG1.** No build step, no framework, no package manager — keep vanilla HTML/CSS/JS per `CLAUDE.md`
- **NG2.** No backend, no auth, no analytics beyond what already exists
- **NG3.** No replacing the current 1-page scroll architecture with multi-route SPA
- **NG4.** No JavaScript-required content — all sections render with JS disabled (progressive enhancement only)
- **NG5.** No Windows-XP-style alternate UI mode (cut from v1; out of scope for this PRD)
- **NG6.** No GitHub contribution graph in hero (cut from v1)
- **NG7.** No cross-repo automation in this branch (developer-portfolios contribution tracked as a separate post-merge issue, not in this PRD's scope)

## 4. Personas

- **Recruiter Rita** — 30s on the page on **mobile**, scanning for: role fit, location, dream-company experience. Loses interest fast. **Rita's eyes must land on three things in 30s: flagship project name, quantified impact stat, and "Senior AI Platform Engineer" title.**
- **Hiring-manager Hugo** — 5–8 min, looking for engineering taste, system thinking, production rigor. Will read project cards, write-ups, and at least one architecture diagram.
- **Peer-engineer Priya** — 15+ min, evaluating depth. Inspects source, reads architecture write-ups, judges code quality of linked repos.

## 5. Reference Portfolios + Specific Steals

### 5.1 yubrajkhatri.com.np
- Floating resume card that previews on hover — **kept, with pre-rendered AVIF screenshot, not live PDF render**
- Contact section that feels warm and personal — **kept, copy: "Let's talk."**
- Blog/notes cards subtly nudge on filter/sort — **kept**

### 5.2 devzahid.in
- Tech-stack icons at consistent pixel dimensions — **kept**
- Contact icons at uniform height/width with hover-reveal previews on desktop, **always-visible inline previews on touch devices** (revised from v1)
- ~~GitHub contribution-graph animation~~ — **CUT** (junior signal)
- Collapsible content sections — **kept, using native `<details>/<summary>`**

### 5.3 yerradouani.me
- Subtle "scroll" nudge at bottom of hero — **kept, with full `prefers-reduced-motion` gate and `aria-hidden`**
- Recommendation-engine project — **kept, REFRAMED** as "In Design" section with linked architecture note (not "TODO")

### 5.4 maximehaegeman.com
- Inline `class Naren(...)` code panel in hero — **kept, with H1B line removed** (moved to resume only)
- Hand-rolled syntax spans, ~1.6KB; not PrismJS

### 5.5 windows-xp-portfolio-tau.vercel.app
- ~~XP OS simulation~~ — **CUT** (out of scope; would warrant its own PRD if pursued)

### 5.6 bjornmelin.io
- Photo favicon — **kept, AVIF (512) + PNG (180 Apple touch) + multi-res .ico, ~18KB**

---

## 6. Functional Requirements

### Content Pillar (highest senior-signal value)

#### F-AW. Architecture Write-Ups Section
- New section between Systems and In Design, titled "Architecture & Write-Ups"
- 2–3 long-form technical posts at launch:
  1. **ExponentHR Catalog-Driven NL-to-SQL** — FAISS retrieval, Claude Sonnet planning, NetworkX join graphs, DAX-free design, multi-tenant governance
  2. **AutoApply AI Q&A Generation** — provider-fallback architecture, RAG with pgvector, category-routed model selection, prompt-cache hit rates
  3. **Portfolio Risk Real-Time Topology** — Kafka producer/Spark consumer split, p95 ingest latency, dashboard backpressure handling
- Each write-up: dedicated `content/posts/<slug>.html` with consistent template (problem, constraints, design, tradeoffs, outcome)
- Section card on home: title + 2-line teaser + "Read →" link
- Posts MAY reuse the existing `content/posts/` directory if compatible; otherwise add it

#### F-IS. Quantified Impact Strip
- Every flagship project card (ExponentHR, AutoApply AI, tailor-resume, Fraud-Detection, Portfolio-Risk, Job-Scout) gets a stat strip
- 3–5 numeric stats per card, each with a unit (e.g., "400 clients", "p95 1.4s", "12k queries/day", "$0.003/query", "99.7% uptime")
- Numbers must be real and defensible — Naren provides ground truth
- Visual: small monospace badges in a horizontal row beneath each card title
- Mobile: wraps to 2 rows, stays readable

#### F-SD. System Diagrams
- One SVG architecture diagram for ExponentHR, one for Portfolio-Risk
- Inline SVG (no `<img>`), so diagrams scale crisply and respect dark/light mode tokens
- Each diagram has a screen-reader-friendly `<title>` and `<desc>` summary
- Linked from the matching write-up + project card

### Visual Pillar (senior-signal-neutral, taste-positive)

#### F1. Hero Code-Class Panel (Maxime-inspired, H1B-removed)
- Inline code block in hero, right side desktop / below H1 mobile
- Renders:
  ```python
  from education import ComputerScience

  class Naren(DataEngineer, MLEngineer):
      """
      Building pipelines that turn raw data
      into decisions — at production scale.
      """
      def __init__(self):
          self.role = "Senior AI Platform Engineer"
          self.base = "Dallas, TX"
          self.exp = 5  # years

      def mission(self) -> str:
          return "From messy data to reliable predictions, at scale."
  ```
- Hand-rolled syntax spans, 6 token classes (kw, str, com, fn, cls, op); CSS color tokens with documented contrast ratios
- ~1.6KB total HTML+CSS budget

#### F2. Resume Hover Preview (Yubraj-inspired)
- "View Resume" link in header
- **Desktop hover** (mouseenter, 200ms debounce): pre-rendered AVIF screenshot of resume page 1 (~25KB), JPEG fallback in `<picture>`
- **Touch tap**: opens preview as a popover (`role="dialog"`, `aria-modal="false"`, dismissable via Esc + outside click)
- Click on the original "View Resume" still navigates to `/static/resume.pdf` (atomic swap on resume updates)
- Decoupled into 3 sub-issues:
  - **F2a** — canonical resume PDF artifact + atomic swap workflow
  - **F2b** — desktop hover popover component
  - **F2c** — touch tap dialog + a11y

#### F3. Tech Stack Grid (Dev-Zahid-inspired, categorized)
- Replace current skills grid with pixel-perfect logo grid
- All icons exactly 48x48px, uniform padding
- Categories: **Languages | Data Platforms | LLM Stack | Infrastructure | Observability**
- Hover reveals tech name + 1-line context ("Spark — production streaming for Portfolio-Risk")
- Touch: tech name always-visible below icon (inline, no tap gesture)
- Inline SVG icons, ~8KB total

#### F4. Contact Section (Dev-Zahid + Yubraj-inspired)
- GitHub, LinkedIn, Email, Resume icons at uniform 56x56px
- **Desktop hover** (popover pattern with proper ARIA): preview cards
  - GitHub → top 3 pinned repos
  - LinkedIn → headline + photo
  - Resume → AVIF screenshot (shares F2 asset)
- **Touch**: previews always-visible inline beneath each icon (no tap gesture)
- Copy: "Let's talk." (not "Want to talk?")
- Merged in implementation with F3 (shared icon-size design tokens, same CSS surface)

#### F5. Scroll Nudge Indicator (Yerradouani-inspired)
- Mouse-scroll SVG icon at bottom of hero, fades in after 1.5s, gently pulses
- Disappears after first scroll event
- Hidden via `@media (pointer: coarse)` on touch
- `aria-hidden="true"` and `role="presentation"`
- Under `prefers-reduced-motion: reduce`: both pulse and fade-in fully suppressed (static or hidden)

#### F6. In Design Section (Yerradouani-inspired, reframed)
- New section between Systems and Writing, titled **"In Design"** (not "Coming Up")
- Seeded with: **Job Recommendation Engine** card
  - Linked to a design doc at `content/posts/job-recommendation-engine-design.html`
  - Doc covers: collaborative filtering vs content-based hybrid, FAISS vs ScaNN, cold-start strategy, eval metrics (NDCG@10, recall@50), integration with job-scout pipeline
  - Status badge: "Designing" (not "TODO")
- Section is a list — easy to add more upcoming work later

#### F7. Collapsibles (Dev-Zahid-inspired, native semantics)
- Long sections (deep Track Record details, Writing archive) get optional collapse via native `<details>/<summary>`
- Default-open on desktop AND mobile for Track Record (do NOT default-collapse on mobile per Rita persona)
- Default-collapsed for archived/older content only (e.g., posts older than 12 months)
- Animated chevron rotation via CSS transform on `[open]` selector
- Section state persists in `localStorage`; FOUC prevented via inline `<head>` script that sets `data-collapsed` before paint
- ~1KB total

#### F8. Notes Card Nudge Animation (Yubraj-inspired)
- On filter or sort: cards subtly translate (8–12px) and fade — staggered 30ms per card, 250ms cubic-bezier easing
- Fully suppressed under `prefers-reduced-motion: reduce`
- Merged in implementation with F7 (same JS module, same easing tokens)

#### F10. Photo Favicon (Bjorn-inspired)
- Replace current favicon with photo of Naren (cropped, neutral background)
- Sizes: 512 AVIF (~6KB), 180 PNG Apple touch (~10KB), multi-res 32+16 .ico (~2KB)
- Total budget: ~18KB

### Quality Pillar (NFR enforcement)

#### F-PB. Perf Regression Test Harness
- GitHub Action runs Lighthouse CI on PR + main pushes
- Budget assertions: Perf >= 95, LCP <= 1.8s, CLS = 0, page weight delta <= 65KB
- Fail PR check on regression
- Reuses public `lighthouse-ci-action`

#### F-A11Y. A11y Regression Test Harness
- Same Action runs `axe-core` against the deployed preview
- Fail PR on any new violation
- Documents the WCAG 2.2 SCs being tracked

#### POST-MERGE. Developer-Portfolios Contribution (out of PRD scope, tracked as separate issue)
- One-time scheduled remote agent triggered after this branch merges to `main`
- Opens a PR to `https://github.com/emmabostian/developer-portfolios` with Naren's entry per repo convention
- Tracked under label `post-merge`, **not part of this PRD's definition of done**

---

## 7. Non-Functional Requirements

### N1. Performance
- Lighthouse Performance >= 95 on mobile + desktop
- No new runtime JS dependencies (keep `0` package count)
- Total page weight increase: **<= 65KB gzipped** vs current baseline (revised down from 80KB after Perf critique tally: ~63KB realistic)
- LCP <= 1.8s on Slow 4G simulation
- CLS = 0
- AVIF resume screenshot must be `loading="lazy"`, NOT in initial critical path

### N2. Accessibility (WCAG 2.2 AA conformance, not just Lighthouse 100)
- Lighthouse A11y = 100 AND axe-core 0 violations
- All interactive elements keyboard-navigable
- Hover-reveals follow popover/tooltip ARIA patterns:
  - Resume preview → `role="dialog" aria-modal="false"`, trigger has `aria-haspopup="dialog" aria-expanded`
  - Tech-stack one-liners → `role="tooltip" aria-describedby` (no interactive children)
  - Contact preview cards → popover pattern (rich content with links)
- Per WCAG 1.4.13 (Content on Hover or Focus): dismissible (Esc), hoverable (cursor enters without dismiss), persistent (stays until dismissed)
- All animations respect `prefers-reduced-motion: reduce` (full gate, not partial)
- New colors documented in a contrast table in the PR — every token >= 4.5:1 (AA) or 7:1 (AAA where feasible)
- Syntax highlight palette: each token >= 4.5:1 on code background
- F5 scroll nudge: `aria-hidden="true"`, `role="presentation"`
- Focus management: hover preview opens → focus moves to first focusable in preview; Esc closes → focus returns to trigger

### N3. Browser Support
- Latest 2 versions of Chrome, Firefox, Safari, Edge
- iOS Safari 16+, Android Chrome 110+
- Graceful degradation on older browsers

### N4. Progressive Enhancement
- All content readable with JS disabled
- All sections in `index.html` (or content/posts/*.html for write-ups)
- JS only enhances

### N5. SEO + Social
- All new sections use semantic HTML5
- OpenGraph image refreshed if hero changes
- Meta description updated to mention recommendation-engine work + write-ups

### N6. Maintainability
- All new CSS uses existing design tokens
- New components self-contained
- Hero code-class panel uses already-loaded JetBrains Mono

---

## 8. Acceptance Criteria (Demoable, all testable)

- [ ] **F-AW** Architecture & Write-Ups section live with 3 posts; each post has problem/constraints/design/tradeoffs/outcome sections
- [ ] **F-IS** Every flagship project card shows 3–5 quantified stats with units
- [ ] **F-SD** ExponentHR + Portfolio-Risk inline SVG diagrams render with `<title>`/`<desc>`, scale crisply on mobile
- [ ] **F1** Hero shows hand-rolled syntax-highlighted code panel; H1B line absent; ≤ 1.6KB total
- [ ] **F2** Resume hover preview uses pre-rendered AVIF (~25KB), JPEG fallback; popover dialog on touch with proper ARIA
- [ ] **F3** Tech stack grid: 5 categories (incl. Observability), all icons 48x48px, hover (desktop) / inline (touch) reveals tech + 1-line context
- [ ] **F4** Contact icons uniform 56x56px; previews on hover (desktop) / inline (touch); copy reads "Let's talk."
- [ ] **F5** Scroll nudge appears, fades after first scroll, hidden on touch, fully suppressed under `prefers-reduced-motion`
- [ ] **F6** "In Design" section visible with Job Recommendation Engine card linking to design doc
- [ ] **F7** Long sections collapse via `<details>/<summary>`; Track Record stays default-open on mobile; state persists in localStorage with no FOUC
- [ ] **F8** Notes cards nudge animation on filter, fully suppressed under `prefers-reduced-motion`
- [ ] **F10** Photo favicon: AVIF 512 + PNG 180 + multi-res .ico, total ~18KB
- [ ] **F-PB** Lighthouse CI Action: Perf >= 95, LCP <= 1.8s, CLS = 0, page weight delta <= 65KB on PR
- [ ] **F-A11Y** axe-core: 0 violations on PR; contrast table in PR description
- [ ] All hover-reveal interactions follow correct ARIA pattern (dialog/tooltip/popover) per N2
- [ ] All interactions keyboard-accessible; Esc dismisses; focus returns to trigger
- [ ] Tested on iOS Safari + Android Chrome (PR template checkbox)
- [ ] **(post-merge, separate issue)** `emmabostian/developer-portfolios` contains Naren's entry

---

## 9. Risks (post-critique)

- **R1.** Resume PDF screenshot must be regenerated when resume changes — mitigation: pre-commit hook or simple manual script in `scripts/snap-resume.sh`
- **R2.** Architecture write-ups require real time investment (~4–8 hours each); ship with 1 post initially if needed, not 3 — mitigation: PRD AC says "2–3 posts at launch" so 2 is acceptable minimum
- **R3.** Contrast tables for new tokens add overhead — mitigation: one-time spreadsheet, lives in `specs/contrast-table.md`
- **R4.** Lighthouse CI Action may be flaky on cold runs — mitigation: 3 runs, take median
- **R5.** F2c (touch dialog) and F4 (touch inline previews) are the most a11y-sensitive — mitigation: code-review with axe-core local run before PR

## 10. Sequencing (rebuilt after Scope critique)

The original Phase A (F1+F10+F4) shared `<head>` and hero region — would conflict on merge. Rebuilt:

**Lane HERO (serial):** F1 → F10 → F5
**Lane CONTENT (parallel-safe):** F-AW → F-IS → F-SD → F6
**Lane ICONS (parallel with HERO + CONTENT):** F3+F4 merged
**Lane RESUME (serial within lane):** F2a → F2b → F2c
**Lane POLISH (parallel):** F7+F8 merged
**Lane QUALITY (parallel):** F-PB, F-A11Y

**Parallel-safe groupings (good for `superpowers:dispatching-parallel-agents`):**
- F3+F4, F-AW, F6, F2a, F-PB can all dispatch simultaneously after F1/F10 hero pass lands

---

## 11. Out of Scope (Explicit)

- Multi-language i18n
- Dark/light mode toggle (already exists)
- Comment system on writing
- CMS migration
- Analytics dashboard
- A/B testing of variants
- Windows XP alternate UI mode (cut)
- GitHub contribution graph (cut)
- developer-portfolios cross-repo PR (separate post-merge issue)

## 12. Open Questions — RESOLVED

| # | Question | Resolution |
|---|----------|------------|
| Q1 | Windows XP mode worth shipping? | **No, cut entirely** |
| Q2 | H1B in code panel or contact? | **Neither — resume only** |
| Q3 | "Coming Up" top-level or subsection? | **Top-level, renamed "In Design"** |
| Q4 | Hover previews GIF/screenshot or iframe? | **Pre-rendered AVIF screenshot** |
| Q5 | 11 features too many? | **Yes — final scope is 14 issues across 5 lanes; 9 visual + 3 content + 2 quality = scope-frozen** |

---

## 13. Issue Decomposition Target (input to /prd-to-issues)

**Final issue count: 14**

| # | Issue Title | Lane | Blocks | Parallel-safe |
|---|-------------|------|--------|---------------|
| 1 | F1: Hero code-class panel (hand-rolled spans, no H1B line) | HERO | F2, F5 | – |
| 2 | F10: Photo favicon (AVIF + PNG + .ico) | HERO | – | yes (with F-AW lane) |
| 3 | F5: Scroll nudge indicator (a11y-gated) | HERO | – | – |
| 4 | F2a: Canonical resume PDF + screenshot artifact pipeline | RESUME | F2b | yes (with F-AW lane) |
| 5 | F2b: Desktop hover popover for resume preview | RESUME | F2c | – |
| 6 | F2c: Touch tap dialog for resume preview (a11y) | RESUME | – | – |
| 7 | F3+F4: Pixel-consistent tech stack & contact icons (uniform sizing, hover/inline) | ICONS | – | yes |
| 8 | F-AW: Architecture & Write-Ups section + 2-3 posts | CONTENT | – | yes |
| 9 | F-IS: Quantified impact strips on flagship project cards | CONTENT | – | yes |
| 10 | F-SD: System diagrams (ExponentHR + Portfolio-Risk inline SVG) | CONTENT | – | yes |
| 11 | F6: In Design section + Recommendation Engine design doc | CONTENT | – | yes |
| 12 | F7+F8: Native `<details>` collapsibles + notes nudge animation | POLISH | – | yes |
| 13 | F-PB: Lighthouse CI perf-budget regression Action | QUALITY | – | yes |
| 14 | F-A11Y: axe-core a11y regression Action + contrast table | QUALITY | – | yes |

**Plus 1 post-merge tracker (separate label, not in PRD's DoD):**
- 15 | POST-MERGE: Auto-contribute Naren's entry to emmabostian/developer-portfolios | – | merge of this PRD | – |
