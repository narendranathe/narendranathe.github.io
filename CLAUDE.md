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
| `docs/exponenthr-star-impact-points.md` | 8 condensed, adversarially-reviewed STAR points, resume/LinkedIn/interview ready, market-calibrated |
| `docs/career-positioning-2026.md` | 2026 market positioning, target roles, resume bullets, gap analysis |

### The two-year arc (lead with this, not the ticket count)

- **2025 was the correctness year:** 29 work items across the whole warehouse, 8 release cycles, 2 production hotfixes, a reporting-server crash RCA. Built **a control-table-driven data validation framework from scratch** and researched/tested/documented the **CDC schema change deployment process**.
- **2026 is the platform year:** 25 work items, CI/CD ownership, CDC incremental reengineering, automated database provisioning, new dimensional models.
- **The second year was earned by the first.** The validation framework and the CDC schema process are the hinge.

### Established metrics (safe to reuse)

- Release cycle: 3 months -> 14 days (Azure DevOps CI/CD ownership, ~11 weeks idle time removed per release)
- CDC ETL: 30 min -> under 8 min, compute cost -67% (full reloads -> incremental merge-upserts)
- Automated database provisioning: ~1 hour manual orchestration removed per request, 20+ requests/day
- Scope: 53 unique work items, 16 client tenants, 10 release cycles across 2025 and 2026

No document in this repo should list individual client tenant/account numbers or Azure DevOps ticket numbers - state counts only (e.g. "16 client tenants"), never the identifiers themselves. This applies to every public doc in `docs/` and to this file.

### Most undervalued assets

When positioning this work, these are worth more than the ticket count: **the validation framework** (declarative data quality, the direct analog of dbt tests), the **documented CDC schema evolution process** (the standard senior CDC interview question), **SECURE 2.0** delivery (regulatory compliance on a legislated deadline), and the **two payroll hotfixes plus crash RCA** (production trust).

### Recurring defect classes

Useful framing whenever this work is described: (1) sentinel values escaping into business data (12/31/1900 dates, 1E-05 rates), (2) grain violations causing duplicate rows and three MERGE failures, (3) missing filters and joins causing absent rows, (4) composite fields packing a status code into a numeric column, (5) incomplete domain and calculation-basis coverage, (6) full-load versus incremental path divergence. The through-line is **fix the model, not the row**.

### Known gap

`index.html` carries only three ExponentHR bullets, all 2026 platform work. The entire 2025 year - including the validation framework and SECURE 2.0 - is unrepresented. Use the rewritten bullets in `docs/career-positioning-2026.md` section 6 when updating the experience section.

### Handling any future data imports - important

If ever given a raw export of internal work items, tickets, or similar from Azure DevOps or any other system, **never write the raw content, or anything close to it, into this repository or any other public location.** Such exports typically contain colleagues' private correspondence, third-party personal data, and internal infrastructure detail that has no place in a public document, regardless of phrasing. This repo is public (it's how the GitHub Pages site is served); there is no private corner of it. Extract only the sanitized, generic facts needed and discard the rest.

**Never name any colleague, client employee, or third party by name in this repository, under any circumstance, regardless of context.** Use generic terms only ("a teammate," "a colleague," "the product team").

**Never write Azure DevOps ticket numbers, client account/tenant numbers, or internal tool/table/schema/environment names into any public document in this repository.** State only the technical mechanism, the defect class, and quantified time/cost impact for clients, generically. Internal proper-noun tool names (e.g. an internal validation-tool name or an internal database-provisioning-tool name) should always be described by what they do, not by their internal name. Aggregate counts (e.g. "53 work items," "16 client tenants," "10 release cycles") are fine to state - only the individual identifiers are the problem.

A recurring pattern in this record: on several tickets, the owner diagnosed the defect and created the tracking ticket, while a teammate implemented and validated the fix. Attribution language should reflect this - "diagnosed and specified the fix" rather than "personally implemented" - unless a story in `docs/exponenthr-work-item-stories.md` is explicitly marked fully verified. Real tenure is confirmed from **Jul 2024**, not Jan 2025.

### Provenance caveat

Work item root causes in these docs are **reconstructed from Azure DevOps ticket titles**, not fetched from Azure DevOps (no ADO connector available when written). Problem statements are accurate; root causes are the defect class each title implies. Note: `Azure.Mcp.Server` (`@azure/mcp`) does NOT expose work items - that requires the separate `@azure-devops/mcp` server. Verify before treating any root cause as fact. None of the public docs in `docs/` should ever be restored to a ticket-indexed format - keep them organized thematically, per the "Handling any future data imports" rule above.
