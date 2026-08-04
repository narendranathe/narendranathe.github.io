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

The site owner is a Data Engineer at ExponentHR (Jul 2024 to present). The 2025.12 to 2026.04 work record is documented in `docs/` and should be treated as the source of truth when writing or revising portfolio content about that role.

| Document | Contents |
|---|---|
| `docs/exponenthr-2026-accomplishments.md` | Delivery record: 25 work items, 11 client tenants, 3 sprint cycles, grouped by theme |
| `docs/exponenthr-work-item-stories.md` | STAR stories per work item, interview-ready, with a question-to-story map |
| `docs/career-positioning-2026.md` | 2026 market positioning, target roles, resume bullets, gap analysis |

### Established metrics (safe to reuse)

- Release cycle: 3 months -> 14 days (Azure DevOps CI/CD ownership, ~11 weeks idle time removed per release)
- CDC ETL: 30 min -> under 8 min, compute cost -67% (full reloads -> incremental merge-upserts)
- AAG Copy Down: ~1 hour manual orchestration removed per request, 20+ requests/day
- Correctness: 25 work items across 11 tenants (00169, 00194, 00612, 00630, 00745, 00747, 00810, 00877, 00982, 00994, 10106)

### Recurring defect classes found across the year

Useful framing whenever this work is described: (1) sentinel values escaping into business data (12/31/1900 dates, 1E-05 rates), (2) grain violations causing duplicate rows and MERGE conflicts, (3) missing filters and joins causing absent rows, (4) composite fields packing a status code into a numeric column. The through-line is **fix the model, not the row**.

### Known gap

`index.html` currently carries only three ExponentHR bullets, all platform-focused. The data correctness and dimensional modeling work - over half the year - is not represented. Use the rewritten bullets in `docs/career-positioning-2026.md` section 5 when updating the experience section.

### Provenance caveat

The work item root causes in these docs are **reconstructed from Azure DevOps ticket titles**, not fetched from Azure DevOps itself (no ADO connector was available when they were written). Problem statements are accurate; root causes are the defect class each title implies. See the appendix of the accomplishments doc for connector setup. Verify before treating any root cause as fact.
