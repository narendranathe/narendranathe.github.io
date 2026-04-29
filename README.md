# Narendranath Edara Portfolio

Personal portfolio site for Narendranath Edara, a Senior AI Platform Engineer focused on production LLM systems, retrieval pipelines, governed analytics, and backend AI infrastructure.

[Live site](https://narendranathe.github.io) | [LinkedIn](https://www.linkedin.com/in/narenedara/) | [GitHub](https://github.com/narendranathe)

## What This Repo Represents

This repository is the public source for my portfolio and career positioning. It is intentionally aligned to the roles I am targeting:

- AI Platform Engineer
- Applied AI Engineer
- Backend Engineer, AI
- ML Platform Engineer
- Software Engineer, AI Systems

The site highlights the kind of work I want to keep doing: production AI systems with strong engineering discipline, not one-off demos.

## Featured Proof Points

### AutoApply AI

Full-stack applied AI system for job-search automation with FastAPI, Chrome extension workflows, multi-provider LLM routing, and production-minded architecture.

### tailor-resume

Packaged resume tailoring system with API surfaces, MCP support, testing, and developer tooling that reflects real software distribution concerns.

### Real-Time Fraud Detection Platform

Streaming ML platform work showing event-driven design, real-time inference, and production observability patterns.

## Stack

- HTML
- CSS
- JavaScript
- GitHub Pages

The site is intentionally simple and fast: no framework, no build step, and no runtime dependencies.

## Repository Structure

- `index.html`: site structure, portfolio sections, copy, and project cards
- `config.js`: live status badge, terminal widget, metrics, recommendations, and social links
- `content/posts/`: long-form writing and supporting portfolio content

## Local Preview

Open `index.html` in a browser for a quick preview, or serve the repo with any lightweight static file server if you want local routing behavior to match GitHub Pages more closely.

## Regenerating Favicons + Social Card

The site uses a deliberate split: monogram "N" white-on-orange for the browser tab (16/32/48 px) and the actual headshot for the iOS home screen (`apple-touch-icon.png`), Android adaptive icon (`favicon-512-maskable.png`), and OpenGraph share card (`og-image.jpg`). All assets are deterministic, regenerated from a single source photo by [`scripts/snap-favicon.py`](scripts/snap-favicon.py).

```bash
# 1. Install pipeline deps (one-time)
pip install -r scripts/requirements.txt

# 2. Drop a fresh head-and-shoulders photo at scripts/_in/headshot-portrait.jpg
#    (and optionally a full-body shot at scripts/_in/headshot-fullbody.jpg)

# 3. Regenerate everything
python scripts/snap-favicon.py

# 4. Bump the cache-bust query strings in index.html (search for "?v=2026-04-28")
#    so existing browsers fetch the new files instead of stale cached copies.

# 5. Commit and push
```

The script auto-detects the face via OpenCV's Haar cascade, applies a tight 1.18× face-bbox crop, renders the monogram from Inter Black (or Arial Bold fallback), and writes all six tab/iOS/Android/OG outputs deterministically. Source masters are downscaled to 1200 px long-edge and saved to `static/originals/` so the repo stays light.

## Deployment

This site is deployed through GitHub Pages from the `main` branch.

## Contact

- Email: `edara.narendranath@gmail.com`
- LinkedIn: `https://www.linkedin.com/in/narendranathe/`
- GitHub: `https://github.com/narendranathe`

