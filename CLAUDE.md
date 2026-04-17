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
