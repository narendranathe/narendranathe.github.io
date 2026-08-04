# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

Pure HTML + CSS + Vanilla JS. No build step, no framework, no package manager. GitHub Pages serves `index.html` directly from `main`.

## Local Development

```bash
python -m http.server 8080
# then open localhost:8080
```

Use an HTTP server (not `file://`) - RSS fetch requires same-origin or CORS headers that `file://` blocks.

## File Layout

| File | Purpose |
|------|---------|
| `index.html` | All portfolio content, styles, and interactive JS (~4,300 lines) |
| `config.js` | Personal config - status badge, terminal lines, RSS feeds, testimonials, Konami metrics. **Gitignored.** |
| `config.template.js` | Template for forkers - copy to `config.js` and fill in |
| `.github/workflows/deploy.yml` | GitHub Actions - auto-deploys to GitHub Pages on push to `main` |

## Config vs Content Split

- `config.js` drives: availability badge, hero terminal animation lines, RSS sources (Medium/Dev.to/Substack), testimonial carousel, Konami easter egg metrics
- `index.html` drives: all section content (bio, experience, projects, skills, education, research, achievements, contact)

When `config.js` is missing (e.g., fresh clone), the page still renders - config values gracefully degrade.

## Section Map (index.html)

Hero -> About (bio + skills grid) -> Education -> Experience (timeline) -> Projects (cards) -> Research -> Articles (RSS) -> Recommendations (carousel) -> Achievements (counters) -> Contact

## Interactive Features

- `Ctrl+K` / `Cmd+K`: command palette
- Scroll progress bar (top of page)
- Achievement counters animate on scroll (IntersectionObserver)
- Konami code `up up down down left right left right B A`: reveals JSON metrics dump in console/overlay

## Deploy

Push to `main`. GitHub Actions handles the rest - no build, no artifact upload needed.

## Typography Rule

Never use en dashes (-) or em dashes (--). Use hyphens (-) for all cases: ranges, compound words, asides, and interruptions.

## Owner Context: ExponentHR Work Record

The site owner is a Data Engineer at ExponentHR (Jul 2024 to present). The 2025 and 2026-to-date work record is documented in `docs/` and is the source of truth when writing or revising portfolio content about that role.

| Document | Contents |
|---|---|
| `docs/exponenthr-accomplishments.md` | Delivery record: 53 work items across 2025 and 2026, 16 tenants, 10 release cycles |
| `docs/exponenthr-work-item-stories.md` | 13 Tier 1 STAR stories plus supporting stories, with a question-to-story map |
| `docs/career-positioning-2026.md` | 2026 market positioning, target roles, resume bullets, gap analysis |

### The two-year arc (lead with this, not the ticket count)

- **2025 was the correctness year:** 29 work items across the whole warehouse, 8 release cycles, 2 production hotfixes, SSRS server crash RCA. Built **Data Checker** (control-table-driven validation framework) and researched/tested/documented the **CDC schema change deployment process**.
- **2026 is the platform year:** 25 work items, CI/CD ownership, CDC incremental reengineering, AAG Copy Down automation, new dimensional models.
- **The second year was earned by the first.** Data Checker and the CDC schema process are the hinge.

### Established metrics (safe to reuse)

- Release cycle: 3 months -> 14 days (Azure DevOps CI/CD ownership, ~11 weeks idle time removed per release)
- CDC ETL: 30 min -> under 8 min, compute cost -67% (full reloads -> incremental merge-upserts)
- AAG Copy Down: ~1 hour manual orchestration removed per request, 20+ requests/day
- Scope: 53 unique work items, 16 client tenants, 10 release cycles across 2025 and 2026
- Tenants: 00169, 00194, 00336, 00479, 00612, 00630, 00704, 00745, 00747, 00810, 00877, 00972, 00979, 00982, 00994, 10106

### Most undervalued assets

When positioning this work, these are worth more than the ticket count: **Data Checker** (declarative data quality, the direct analog of dbt tests), the **documented CDC schema evolution process** (the standard senior CDC interview question), **SECURE 2.0** delivery (regulatory compliance on a legislated deadline), and the **two payroll hotfixes plus crash RCA** (production trust).

### Recurring defect classes

Useful framing whenever this work is described: (1) sentinel values escaping into business data (12/31/1900 dates, 1E-05 rates), (2) grain violations causing duplicate rows and three MERGE failures, (3) missing filters and joins causing absent rows, (4) composite fields packing a status code into a numeric column, (5) incomplete domain and calculation-basis coverage, (6) full-load versus incremental path divergence. The through-line is **fix the model, not the row**.

### Known gap

`index.html` carries only three ExponentHR bullets, all 2026 platform work. The entire 2025 year - including Data Checker and SECURE 2.0 - is unrepresented. Use the rewritten bullets in `docs/career-positioning-2026.md` section 6 when updating the experience section.

### Provenance caveat

Work item root causes in these docs are **reconstructed from Azure DevOps ticket titles**, not fetched from Azure DevOps (no ADO connector available when written). Problem statements are accurate; root causes are the defect class each title implies. Note: `Azure.Mcp.Server` (`@azure/mcp`) does NOT expose work items - that requires the separate `@azure-devops/mcp` server. See the accomplishments doc appendix. Verify before treating any root cause as fact.
