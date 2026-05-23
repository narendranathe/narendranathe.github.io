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

Source files: copy from the portfolio repo's `static/` + `static/originals/`. Use the staging script — it builds the canonical layout and writes `manifest.json` with computed hashes:

```bash
# From portfolio repo root
bash scripts/m1-stage-resume2-assets.sh
# -> build/resume2-staging/ now mirrors the layout above

# Sync into a local clone of narendranathe/resume2 at ../resume2
rsync -av build/resume2-staging/ ../resume2/

cd ../resume2
git add .
git commit -m "feat: initial media layout"
git push
```

The staging script reports each file's `version_hash` (first 8 chars of sha256) and bakes them into `manifest.json` so the cache-bust query strings in Step 7 are derived deterministically.

## Step 3: `manifest.json` schema (auto-generated, for reference)

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

The hashes (`*_version_hash` fields) are computed by `scripts/m1-stage-resume2-assets.sh` from the staged files' bytes. If you replace assets later, rerun the stager — manifest.json gets regenerated.

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

## Step 7: Flip `CONFIG.identity` paths to point at resume2

M3's render pipeline is already shipped on `claude/beautiful-ptolemy-C8L4O`. The template `index.html.j2` composes asset URLs as `{{ identity.canonicalUrl }}{{ identity.ogImage }}` and `{{ identity.canonicalUrl }}{{ identity.headshot }}` — so flipping the asset paths in `CONFIG.identity` flips every identity surface in the rendered HTML at once.

Edit `config.js`:

```diff
 identity: {
     ...
-    ogImage:    '/static/og-image.jpg?v=2026-04-28',
+    ogImage:    '/resume2/og/og-image.jpg?v=4d8934bf',
     ...
-    headshot:   '/static/originals/headshot-fullbody.jpg',
+    headshot:   '/resume2/headshots/fullbody.jpg?v=7dc275e2',
     ...
 }
```

Use the `version_hash` values from Step 2's `manifest.json` (or the staging script's stdout). The `/resume2/` prefix is the GH Pages project-page subpath — when prepended to `canonicalUrl` (`https://narendranathe.github.io`), it resolves to the resume2 Pages origin.

Mirror the same edit in `config.template.js` placeholder values so forkers see the pattern.

Re-render to apply the change:

```bash
python scripts/render-portfolio.py
git diff index.html       # should show og:image, twitter:image, JSON-LD image all flipped to /resume2/ URLs
```

Commit `config.js` + `config.template.js` + `index.html` together. The Pages deploy pipeline (M6) re-renders on push, but committing the rendered output keeps local previews accurate.

## Step 8: Decide what to do with the duplicate files in portfolio `static/`

After Step 7, three files in portfolio `static/` are duplicated in `narendranathe/resume2`:

- `static/og-image.jpg` -> `resume2/og/og-image.jpg`
- `static/originals/headshot-fullbody.{jpg,avif,webp}` -> `resume2/headshots/fullbody.*`
- `static/originals/headshot-fullbody-800.{jpg,avif,webp}` -> `resume2/headshots/fullbody-800.*`
- `static/preview-{linkedin,substack,github}.png` -> `resume2/previews/*.png`

Recommend: **delete the duplicates from portfolio `static/`** after the resume2 deploy is verified live. Reasons:
- They're identity-bearing files, and the whole point of the migration is that identity lives in one place.
- Keeping duplicates means future `snap-favicon.py` runs need to write to both repos (extra coordination cost).
- The favicons (`favicon-*.png`, `favicon.ico`, `apple-touch-icon.png`, `favicon-512-maskable.png`, `site.webmanifest`) STAY in portfolio `static/` per scope-lock — those are brand chrome, not personal identity.

```bash
# AFTER verifying resume2 Pages serves the migrated files (Step 5 smoke checks):
git rm static/og-image.jpg
git rm static/preview-linkedin.png
git rm static/preview-substack.png
git rm static/preview-github.png
git rm static/originals/headshot-fullbody.{jpg,avif,webp}
git rm static/originals/headshot-fullbody-800.{jpg,avif,webp}
# Keep static/originals/headshot-portrait.jpg (snap-favicon.py source-of-truth)
# Keep favicons + site.webmanifest
```

Note: `scripts/snap-favicon.py` reads from `scripts/_in/headshot-*` to regenerate favicons; the `static/originals/` copies are downscaled archives. After deletion, the script still works (it doesn't read from `static/originals/`).

## Acceptance gate

M1 is complete when all of the following are true:

- [ ] `https://narendranathe.github.io/resume2/og/og-image.jpg` returns 200 + `Content-Type: image/jpeg`
- [ ] `https://narendranathe.github.io/resume2/headshots/fullbody.avif` returns 200 + `Content-Type: image/avif` (or `<picture>` fallback handles octet-stream)
- [ ] `https://narendranathe.github.io/resume2/manifest.json` returns 200 + `Content-Type: application/json`
- [ ] `?v=<hash>` query strings return 200 (cache-bust compat)
- [ ] `_proto_test` tag create + delete cycle succeeds (no rulesets blocking)
- [ ] `scripts/lighthouse-baseline.json` committed with real captured scores
- [ ] `CONFIG.identity.{ogImage,headshot}` in `config.js` point at `/resume2/...` paths
- [ ] `python scripts/render-portfolio.py --check` passes (rendered HTML matches template render)
- [ ] LinkedIn post-inspector at https://www.linkedin.com/post-inspector/inspect/https%3A%2F%2Fnarendranathe.github.io shows the OG image renders from the resume2 URL
- [ ] Duplicate files removed from portfolio `static/` (optional cleanup per Step 8)
