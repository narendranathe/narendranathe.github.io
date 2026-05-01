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

## Stable Resume URL — drop-in for any portfolio

> **Status: v0.1.0-experimental.** The well-known path `/.well-known/resume.json` is not yet IANA-registered ([RFC 8615 §3.1](https://datatracker.ietf.org/doc/html/rfc8615#section-3.1)); for hardened use, vendor-prefix it.

Every developer with a portfolio hits the same pain: recruiter clicks a 6-month-old resume URL → 404 (file renamed); LinkedIn / cold-outreach links rot every update; CDNs cache aggressively so content changes don't propagate. This repo ships a small protocol that fixes all three.

**The contract:**

| Path | Purpose |
|------|---------|
| `/static/resume.pdf` | Canonical PDF. Filename never changes; inbound links never break. PDF metadata (`/Producer`, `/CreationDate`, `/ID`) is sanitized at publish time to avoid toolchain fingerprinting. |
| `/.well-known/resume.json` | Discovery sidecar ([RFC 8615](https://datatracker.ietf.org/doc/html/rfc8615)). Tools probe `<host>/.well-known/resume.json` and read version + page count + last-updated date without parsing PDF bytes. |
| `/static/resume.schema.json` | JSON Schema (draft 2020-12) so adopters can validate their sidecars. |
| `<a href="/static/resume.pdf?v=<hash>">` | Cache-bust uses content-derived `version_hash`. Stable URL, immediate invalidation on content change. |

**Regenerate:**

```bash
# 1. Drop your latest resume at scripts/_in/resume.pdf (gitignored)
# 2. Run — script auto-strips PDF metadata, writes sidecar+schema, and
#    rewrites every /static/resume.pdf?v=<hash> in index.html in place.
python scripts/snap-resume.py
# 3. Commit and push.
```

Self-test (11 assertions, stdlib only):

```bash
python scripts/snap-resume.py --self-test
```

A GitHub Action ([`.github/workflows/resume-self-test.yml`](.github/workflows/resume-self-test.yml)) runs the self-test, validates the sidecar against the schema, and warns if the cache-bust hash in `index.html` drifts from the sidecar.

**CDN cache-bust compatibility:**

| Host | Query-string `?v=` cache-bust works out of the box? |
|------|------|
| GitHub Pages, Vercel | Yes |
| Cloudflare Pages, Netlify | No — query strings stripped from cache key by default; configure cache-level standard or hash the path instead |
| S3 + CloudFront | No — distribution must forward query strings |

For CDNs that strip query strings, hash-suffix the filename (`/static/resume.<hash>.pdf`) and 302 from the canonical URL.

**Privacy notes:**

- The sidecar's `last_updated` field is intentionally **date-only** (not full ISO 8601 timestamp). Full timestamps broadcast job-search activity to anyone (including a current employer) probing `/.well-known/resume.json`.
- Source PDFs in `scripts/_in/` are gitignored by default; only the sanitized canonical copy ships.

## Impact Strip — drop-in pattern for project cards

Every flagship project card on this site uses an "impact strip" — 3-5 quantified-impact metrics displayed beneath the card title. Senior-engineer-credible (verifiable provenance via `aria-describedby`, AAA contrast, no font-swap CLS) and copy-pasteable into any portfolio (Hugo, Jekyll, Next.js, Astro, vanilla HTML).

See **[docs/impact-strip-pattern.md](docs/impact-strip-pattern.md)** for the full spec, HTML/CSS, conventions ("numbers > tech labels", "3-5 stats per card", "every stat has defensible provenance"), and a11y/mobile checklist.

The reference implementation ships in `index.html` + `styles.css`. Tests in `scripts/test-portfolio.py` enforce the contract:

```bash
python scripts/test-portfolio.py --self-test
```

17 assertions cover: pattern presence on every card, 3-5 stat range, semantic primitive (`<dl>`), `aria-describedby` linkage, no scrapped-project claims, no inline styles, JetBrains Mono loaded, mobile breakpoint at 600px, dark-mode + print blocks. Wired into CI ([`.github/workflows/portfolio-self-test.yml`](.github/workflows/portfolio-self-test.yml)).

## Deployment

This site is deployed through GitHub Pages from the `main` branch.

## Contact

- Email: `edara.narendranath@gmail.com`
- LinkedIn: `https://www.linkedin.com/in/narendranathe/`
- GitHub: `https://github.com/narendranathe`

