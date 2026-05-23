# M1: resume2 repo setup runbook

This is the manual half of milestone M1 (tracer bullet) from PRD [#100](https://github.com/narendranathe/narendranathe.github.io/issues/100) / child issue [#101](https://github.com/narendranathe/narendranathe.github.io/issues/101). Scope-lock decisions are in [issue #100 comment 4524042426](https://github.com/narendranathe/narendranathe.github.io/issues/100#issuecomment-4524042426).

Goal: enable GitHub Pages on the existing `narendranathe/resume2` repo so it can serve headshots, OG images, social previews, and `manifest.json` from `https://narendranathe.github.io/resume2/...` as a same-origin second Pages site. The resume PDF stays at `/static/resume.pdf` in the portfolio repo (preserves the v0.1.0-experimental contract).

Estimated time: 30-45 min including verification + lighthouse baseline capture.

---

## Step 1: Enable Pages on `narendranathe/resume2`

1. Visit https://github.com/narendranathe/resume2/settings/pages
2. Source: `Deploy from a branch`. Branch: `main`. Folder: `/ (root)`. Save.
3. First build takes 5-10 min. Watch Actions tab for the `pages-build-deployment` workflow.
4. Once green, the site URL is `https://narendranathe.github.io/resume2/` (note the trailing slash + the `/resume2` path prefix because this is a project page, not a user page).

## Step 2: Drop the canonical asset layout into `narendranathe/resume2`

Required directory structure (resume.pdf is NOT here — it stays in portfolio repo `/static/`):

```
resume2/
  headshots/
    portrait.jpg
    portrait.avif
    portrait.webp
    fullbody.jpg
    fullbody.avif
    fullbody.webp
    fullbody-800.jpg
    fullbody-800.avif
    fullbody-800.webp
  og/
    og-image.jpg
  previews/
    linkedin.png
    substack.png
    github.png
  manifest.json
```

Source files: copy from the portfolio repo's `static/` + `static/originals/`.

```bash
# From a local clone of narendranathe/resume2 at ../resume2 (relative to portfolio repo)
cp static/originals/headshot-portrait.*           ../resume2/headshots/
cp static/originals/headshot-fullbody.*           ../resume2/headshots/
cp static/originals/headshot-fullbody-800.*       ../resume2/headshots/
cp static/og-image.jpg                            ../resume2/og/og-image.jpg
cp static/preview-linkedin.png                    ../resume2/previews/linkedin.png
cp static/preview-substack.png                    ../resume2/previews/substack.png
cp static/preview-github.png                      ../resume2/previews/github.png
# manifest.json: see Step 3
```

## Step 3: Create `manifest.json`

Schema (paths are repo-root-relative, resolve against `https://narendranathe.github.io/resume2/`):

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2026-05-23",
  "headshots": {
    "portrait_jpg":         "/headshots/portrait.jpg",
    "portrait_avif":        "/headshots/portrait.avif",
    "portrait_webp":        "/headshots/portrait.webp",
    "fullbody_jpg":         "/headshots/fullbody.jpg",
    "fullbody_avif":        "/headshots/fullbody.avif",
    "fullbody_webp":        "/headshots/fullbody.webp",
    "fullbody_800_jpg":     "/headshots/fullbody-800.jpg",
    "fullbody_800_avif":    "/headshots/fullbody-800.avif",
    "fullbody_800_webp":    "/headshots/fullbody-800.webp"
  },
  "og": {
    "image":        "/og/og-image.jpg",
    "version_hash": "REPLACE_WITH_SHA256_FIRST_8"
  },
  "previews": {
    "linkedin":  "/previews/linkedin.png",
    "substack":  "/previews/substack.png",
    "github":    "/previews/github.png"
  }
}
```

Note: no `resume` field. Resume PDF stays at the portfolio repo's `/static/resume.pdf` and at `https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf` (the existing rolling Release). M4 manages the release publishing; M3's render pipeline reads `resume` URLs from `config.js`, not from this manifest.

Compute the `version_hash` for the OG image:

```bash
shasum -a 256 ../resume2/og/og-image.jpg | cut -c1-8
```

Commit + push to `narendranathe/resume2@main`.

## Step 4: Branch protection on `narendranathe/resume2`

1. Visit https://github.com/narendranathe/resume2/settings/branches
2. Add a rule for `main`: require linear history, no force push, no deletion.
3. **DO NOT** add any rule under Settings -> Rules -> Rulesets that targets `Tag` refs.
4. **DO NOT** add any pattern under Settings -> Tags that matches `resume` or `resume-*`.

Why: M4's snap-resume orchestrator force-moves the rolling `resume` tag alias every PDF cut via `gh release delete --cleanup-tag`. If tag protection blocks tag deletion, M4 falls back to dated-tags-only + a `latest.json` pointer. See [issue #100 comment 4524042426](https://github.com/narendranathe/narendranathe.github.io/issues/100#issuecomment-4524042426) for the fallback.

## Step 5: Run the smoke checks

From the portfolio repo:

```bash
bash scripts/m1-smoke-checks.sh
```

This verifies:
- Pages site is up at `https://narendranathe.github.io/resume2/`
- AVIF files serve with `Content-Type: image/avif` (the one assumption M1 is gated on)
- JPG / PNG / JSON content types are correct
- `?v=` query strings survive (cache-bust compatibility)
- Tag-deletion is not blocked by protection rules (creates + deletes `_proto_test` tag)

If any check fails, fix the underlying setup before proceeding to M2.

## Step 6: Capture the Lighthouse baseline

M5's regression gate (per scope-lock) needs a pre-M3 baseline at `scripts/lighthouse-baseline.json`. Capture it before M3 ships so the comparison is against pre-render-pipeline numbers.

```bash
# Trigger the existing lighthouse workflow on the latest production deploy
gh workflow run lighthouse.yml --ref main

# Wait ~3 min for the run to complete, then find the run ID:
gh run list --workflow=lighthouse.yml --limit 1

# Download the artifact (the workflow uploads .lighthouseci/ as `lighthouse-report`):
gh run download <RUN_ID> -n lighthouse-report -D /tmp/lh

# Manually inspect /tmp/lh/manifest.json + the per-URL JSONs and populate
# scripts/lighthouse-baseline.json with the median run's scores:
```

```json
{
  "captured_at": "2026-05-23",
  "url": "https://narendranathe.github.io",
  "mobile":  { "performance": NN, "accessibility": NN, "best_practices": NN, "seo": NN },
  "desktop": { "performance": NN, "accessibility": NN, "best_practices": NN, "seo": NN }
}
```

Commit `scripts/lighthouse-baseline.json` to the portfolio repo on the `feat/m1-resume2-tracer` branch (or merge it into `claude/beautiful-ptolemy-C8L4O` separately). M5's `scripts/lighthouse-delta-check.py` consumes this file on every Lighthouse run.

## Step 7: Update one `<meta property="og:image">` in `index.html`

The validating live-site change for M1: pick the `<meta property="og:image">` tag in `index.html` (search for `og:image` — there should be one occurrence in the head) and update its URL from the current `/static/og-image.jpg?v=...` to `https://narendranathe.github.io/resume2/og/og-image.jpg?v=<NEW_HASH>` where `<NEW_HASH>` is the first 8 chars of the SHA-256 of the file in resume2.

Don't update the other 14 identity surfaces yet — M3 will template them out. M1's job is to prove the same-origin Pages architecture works end-to-end with ONE surface as a smoke test.

After committing this single-line change and the Pages deploy finishes (5-10 min lag), inspect the LinkedIn URL previewer (https://www.linkedin.com/post-inspector/inspect/https%3A%2F%2Fnarendranathe.github.io) to confirm the OG image still renders.

## Acceptance gate

M1 is complete when all of the following are true:

- [ ] `https://narendranathe.github.io/resume2/og/og-image.jpg` returns 200 + `Content-Type: image/jpeg`
- [ ] `https://narendranathe.github.io/resume2/headshots/portrait.avif` returns 200 + `Content-Type: image/avif` (or browser-side `<picture>` fallback handles octet-stream; document which)
- [ ] `https://narendranathe.github.io/resume2/manifest.json` returns 200 + `Content-Type: application/json`
- [ ] `?v=<hash>` query strings return 200 (cache-bust compat)
- [ ] `_proto_test` tag create + delete cycle succeeds (no rulesets blocking)
- [ ] `scripts/lighthouse-baseline.json` committed with real captured scores
- [ ] `<meta property="og:image">` in `index.html` points at new origin
- [ ] LinkedIn post-inspector shows the OG image renders from the new URL

Only after these all pass should #102 (M2) be merged.
