# PRD v3: Portfolio UI Upgrade — Trimmed for Career Leverage

**Status:** v3 (trimmed after second-round 3-agent self-critique; scope-frozen)
**Author:** Naren + Claude
**Branch:** `feat/portfolio-ui-upgrade-2026` (off `feat/portfolio-apex`)
**Date:** 2026-04-28

---

## v2 → v3 Changelog

A second round of critique (Skeptic + Shipper + Strategist) revealed that v2 was **a well-engineered software project that was the wrong project**. The strategist's verdict dominated:

> "Naren is targeting Senior+ AI roles at Anthropic, Stripe, Citadel — the rate-limiter on those interviews is **not portfolio polish**; it's getting past the recruiter screen. 80–160 hours of UI upgrade produces zero inbound recruiter signal. The real multipliers are warm referrals, indexed public artifacts (HN-eligible blog posts, OSS PRs), and reputation work."

v3 cuts the portfolio scope by ~70% and redirects the saved hours to higher-leverage moves.

### What was cut from v2 (10 issues, all closed as superseded)

| Cut | Reason |
|-----|--------|
| F1 (hero code-class panel) | Senior recruiters don't care about syntax-highlighted hero text |
| F-PB (Lighthouse CI gate) | Vanity infra for a static page; not the recruiter funnel |
| F-A11Y (axe-core regression harness) | Senior+ a11y signal lives in production work, not personal-site CI |
| F5 (scroll nudge indicator) | Micro-UX polish; Anthropic does not care |
| F2b (resume desktop hover popover) | Over-engineered substitute for "link to PDF" |
| F2c (resume touch tap dialog) | Same; iOS testing also unrealistic on Naren's Win+Android setup |
| F3+F4 (pixel-consistent tech + contact icons) | Icon hygiene; substitutes for one paragraph of LinkedIn About copy |
| F6 (In Design + recommendation engine doc) | "Designing" badge with hand-wavy doc is a weaker signal than no signal |
| F7+F8 (collapsibles + nudge animation) | Polish |
| POST-MERGE F12 (developer-portfolios entry) | List of portfolio links; recruiters don't source from it |

### What survived (5 issues — kept, scoped down)

| Survivor | Why it passes the career-leverage filter |
|----------|-------------------------------------------|
| #56 F-AW (1-2 architecture write-ups) | Only issue producing **external, indexable, shareable** artifacts. HN-eligible posts compound. Pivoted away from ExponentHR NL-to-SQL (project scrapped) to AutoApply AI + repo-context-hooks. |
| #57 F-IS (impact strips on flagship cards) | Numbers flow back to resume + LinkedIn About + cold-outreach. Reusable. |
| #58 F-SD (inline SVG system diagrams) | Diagrams compound — feed into blog posts, resume, recruiter screenshare in interviews. Pivoted to AutoApply AI + Portfolio-Risk subjects. |
| #52 F2a (canonical PDF at stable URL — PDF only) | Genuine recruiter infrastructure. AVIF screenshot half cut. |
| #50 F10 (photo favicon) | Cheap, memorable, low-risk; protects against tab-loss in 14-tab recruiter sessions. |

### What was added (3 NEW issues — the actual high-leverage moves)

| New | Action | Cadence |
|-----|--------|---------|
| **HL-1 Warm-referral campaign** | Map LinkedIn 2nd-degree to 24 dream companies; send 5 personalized notes/day for 10 days | One-shot, ~25 hours |
| **HL-2 2 OSS PRs to anthropic-cookbook (or pgvector / mlflow)** | Concrete gap on prompt-caching benchmarks for long-context workloads, using AutoApply AI + tailor-resume as real workloads | One-shot, ~30 hours |
| **HL-3 3 HN-eligible blog posts (cross-posted to Lobsters/dev.to/Substack)** | Topics: AutoApply AI provider-fallback architecture, repo-context-hooks supply-chain hardening, field-detection Strategy C audit | One-shot, ~30 hours |

### Project scrappage note

**ExponentHR NL-to-SQL Architecture 4 has been scrapped as a portfolio asset.** All references removed from index.html, README.md, memory files, and issues. The employer (ExponentHR Data Engineer role) remains valid — bullets pivot to CI/CD, CDC ETL, AAG database automation only.

---

## 1. Problem (revised)

The current portfolio is a clean, fast 1-page scroll. The previous PRD v2 added 14 issues of UI polish on the assumption that polish moves the recruiter funnel. Second-round critique established that it does not — for Senior+ AI roles at H1B-sponsoring companies, the funnel is gated by:

1. **Warm referrals** (LinkedIn 2nd-degree intros)
2. **Indexed public artifacts** (HN/Lobsters posts, OSS PR commit graphs)
3. **Recruiter inbound** (LinkedIn keywords, reposts, conference signal)

The portfolio site is a tiebreaker after the recruiter screen, not the primary signal source.

## 2. Goals (revised)

- **G1 (CONTENT, kept).** Ship 1-2 deep architecture write-ups (AutoApply AI, repo-context-hooks) and cross-post to HN/Lobsters/dev.to.
- **G2 (POLISH, scoped down).** Add a small set of senior-signal touches: quantified impact strips, system diagrams, photo favicon, canonical resume URL.
- **G3 (CAREER, NEW).** Run a 50-person warm-referral campaign + 2 OSS PRs to dream-company-adjacent repos.

## 3. Non-Goals (revised)

- **NG1.** No build step, no framework, no package manager — keep vanilla HTML/CSS/JS.
- **NG2.** No backend, no auth, no analytics beyond what already exists.
- **NG3.** No replacing 1-page scroll with multi-route SPA.
- **NG4.** No hover-popover system, no pixel-grid icon refresh, no XP mode.
- **NG5.** No Lighthouse CI / axe-core regression harnesses (deferred — not blocking the high-leverage work).
- **NG6.** No in-page "In Design" / recommendation-engine teaser.
- **NG7.** No ExponentHR NL-to-SQL references anywhere in this repo or related artifacts (project scrapped).

## 4. Personas (revised)

The personas from v2 (Recruiter Rita / Hiring-manager Hugo / Peer-engineer Priya) are still valid — but the v3 understanding is that **Rita and Hugo never reach the portfolio without warm intro or HN/LinkedIn referrer**. The portfolio is what they verify *after* deciding to engage. Optimize for verification speed (canonical PDF, 1-2 strong write-ups, defensible numbers), not first-impression theater.

## 5. Functional Requirements (final 5)

| # | Title | Issue | Lane |
|---|-------|-------|------|
| F-AW | 1-2 architecture write-ups (AutoApply AI + repo-context-hooks) | #56 | CONTENT |
| F-IS | Quantified impact strips on flagship project cards | #57 | CONTENT |
| F-SD | Inline SVG system diagrams (AutoApply AI + Portfolio-Risk) | #58 | CONTENT |
| F2a | Canonical resume PDF at stable URL (PDF only) | #52 | RESUME |
| F10 | Photo favicon (AVIF + PNG + .ico) | #50 | HERO |

**Total estimated hours (Shipper realistic estimate):** ~24 hours.

## 6. New High-Leverage Issues (parallel to portfolio work)

| # | Title | Issue |
|---|-------|-------|
| HL-1 | 50-person warm-referral campaign | NEW |
| HL-2 | 2 OSS PRs to anthropic-cookbook / pgvector / mlflow | NEW |
| HL-3 | 3 HN-eligible blog posts cross-posted to Lobsters/dev.to | NEW |

**Total estimated hours:** ~85 hours.

## 7. Non-Functional Requirements (relaxed)

- **N1.** Portfolio still loads fast (Lighthouse Perf >= 90 — unenforced; dropped from 95 + CI gate).
- **N2.** Accessibility: keep current state, do not regress; do not require axe-core gate to ship.
- **N3.** Browser support: same as today.
- **N4.** Progressive enhancement: maintained (no JS required for content).
- **N5.** SEO: unchanged.
- **N6.** Maintainability: each new component must be self-contained.

## 8. Acceptance Criteria (final)

- [ ] At least 1 architecture write-up published, cross-posted to HN + Lobsters + dev.to (#56)
- [ ] All flagship project cards show 3-5 quantified, defensible stats (#57)
- [ ] AutoApply AI + Portfolio-Risk inline SVG diagrams render with `<title>`/`<desc>` (#58)
- [ ] Canonical resume PDF live at `https://narendranathe.github.io/static/resume.pdf` (#52)
- [ ] Photo favicon visible in browser tab (#50)
- [ ] Warm-referral campaign tracking sheet shows 50 outreach attempts logged (HL-1)
- [ ] At least 1 OSS PR open or merged in anthropic-cookbook / pgvector / mlflow (HL-2)
- [ ] At least 1 blog post submitted to HN with title link captured (HL-3)
- [ ] Zero references to ExponentHR NL-to-SQL Architecture 4 anywhere in repo, memory, or GitHub issues

## 9. Sequencing

**Lane CAREER (highest priority, lowest latency to interview loops):**
- HL-1 (warm-referral campaign) — start immediately, runs 10 days

**Lane CONTENT (parallel with CAREER, content powers HL-3):**
- F-AW post #1 (AutoApply AI provider-fallback) — 8 hours
- F-AW post #2 (repo-context-hooks supply-chain) — 8 hours
- HL-3 (cross-post both posts to HN/Lobsters/dev.to) — 4 hours
- F-SD diagrams (feed posts) — 6 hours
- F-IS impact strips — 4 hours

**Lane RESUME-INFRA (small, high-ROI):**
- F2a canonical PDF URL — 1 hour
- F10 favicon — 2 hours

**Lane OSS:**
- HL-2 (2 OSS PRs) — 30 hours; pick after the first blog post lands so cross-pollination is possible

## 10. Risks

- **R1.** Warm-referral campaign requires energy + emotional discipline (rejection-tolerance) — mitigation: 5/day cadence is intentionally small, sustainable
- **R2.** Blog posts can balloon — mitigation: 1500-2000 word target; ship one before starting the next
- **R3.** OSS PR maintainer response time is unpredictable — mitigation: open the PR and move on; merge timeline is not on Naren's clock
- **R4.** ExponentHR NL-to-SQL still appears somewhere in old git history (pre-scrub commits) — mitigation: rewriting history is destructive; scrubbing the working tree + new artifacts is sufficient

## 11. Out of Scope (Explicit)

- Hover popovers / dialog patterns
- Tech-stack pixel-grid refresh
- Collapsibles
- Scroll-nudge indicators
- Code-class hero panel
- Lighthouse CI / axe-core gates
- Windows XP mode
- GitHub contribution graph
- developer-portfolios cross-repo PR
- ExponentHR NL-to-SQL Architecture 4 (project scrapped — never to be re-added)
