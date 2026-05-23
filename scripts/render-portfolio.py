#!/usr/bin/env python3
"""
render-portfolio.py - Jinja2 render of index.html.j2 -> index.html (M3).

Why this exists
---------------
The portfolio's identity surfaces (name, role, OG/Twitter meta, JSON-LD,
footer copyright) were duplicated in 15+ places across index.html. That
made forking the repo for a different person a multi-hour grep-and-pray
exercise and made any rebrand prone to drift. M2 collapsed identity into
a single CONFIG.identity object in config.js. M3 (this script) renders
index.html from index.html.j2 using that single source of truth.

Architecture
------------
- Source of truth: config.js -> CONFIG.identity (15 fields).
- Optional media manifest fetched from CONFIG.identity.mediaRepoUrl
  (a second GitHub Pages site that hosts headshots / OG previews).
  Falls back to scripts/manifest.last-known-good.json on network failure.
- Template: index.html.j2 - same as index.html plus Jinja2 placeholders
  for the migration surfaces and a JSON-LD Person + Twitter card block.
- Output: index.html - committed and served by GitHub Pages.

Until M6 wires this into CI, the render is run manually after editing
identity fields. The byte-identity guarantee for non-net-new surfaces is
preserved by Jinja2's autoescape=False (see security note in render()).

CLI
---
    python scripts/render-portfolio.py             # render to ./index.html
    python scripts/render-portfolio.py --check     # exit 1 if disk drifted
    python scripts/render-portfolio.py --self-test # 5+ embedded assertions
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest.mock as mock
import urllib.error
import urllib.request
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config.js"
TEMPLATE_PATH = REPO_ROOT / "index.html.j2"
OUTPUT_PATH = REPO_ROOT / "index.html"
FALLBACK_MANIFEST = REPO_ROOT / "scripts" / "manifest.last-known-good.json"

FETCH_TIMEOUT = 10
FETCH_RETRIES = 3
FETCH_BACKOFF = (1, 2, 4)


# ─────────────────────────────────────────────────────────────────────────────
# config.js parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_config(config_path: Path) -> dict:
    """
    Evaluate config.js inside a Node vm sandbox and return CONFIG + the
    window.PORTFOLIO_CONFIG bridge as a plain dict. We use Node (not a JS
    transpiler in Python) because config.js is real JavaScript - getter
    properties on PORTFOLIO_CONFIG.identity, `const` declarations, object
    literals - and Node already ships on every developer machine that runs
    this repo.
    """
    # NOTE on the trailing `;this.CONFIG = CONFIG;`:
    # config.js declares `const CONFIG = ...` at top level. In Node's vm
    # module, top-level `const`/`let` bindings live in a per-script lexical
    # scope and do NOT attach to the context object (only `var` and bare
    # assignments do). To extract CONFIG we append a one-liner that copies
    # the binding onto `this`, which at top level inside vm.runInNewContext
    # IS the context object. window.PORTFOLIO_CONFIG is already a property
    # of the seeded `window` object, so it round-trips for free.
    js = (
        "const vm = require('vm');"
        "const fs = require('fs');"
        "const ctx = { window: {} };"
        f"const src = fs.readFileSync({json.dumps(str(config_path))}, 'utf8') + ';this.CONFIG = CONFIG;';"
        "vm.runInNewContext(src, ctx);"
        "console.log(JSON.stringify({CONFIG: ctx.CONFIG, PORTFOLIO_CONFIG: ctx.window.PORTFOLIO_CONFIG}));"
    )
    try:
        out = subprocess.run(
            ["node", "-e", js],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "node executable not found on PATH - install Node.js to run the render"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"config.js evaluation failed: {exc.stderr.strip()}"
        ) from exc
    return json.loads(out.stdout)


# ─────────────────────────────────────────────────────────────────────────────
# manifest fetch (with fallback)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_manifest(media_repo_url: str) -> dict:
    """
    Fetch ${media_repo_url}/manifest.json with retries. On persistent
    failure, return the committed last-known-good fallback. Network is
    optional - the script must work fully offline against the fallback
    so that fresh clones and CI without external network still render.
    """
    url = media_repo_url.rstrip("/") + "/manifest.json"
    last_err: Exception | None = None
    for attempt, delay in enumerate(FETCH_BACKOFF[:FETCH_RETRIES], start=1):
        try:
            print(
                f"[render] manifest fetch attempt {attempt}/{FETCH_RETRIES}: {url}",
                file=sys.stderr,
            )
            with urllib.request.urlopen(url, timeout=FETCH_TIMEOUT) as resp:
                data = resp.read()
                manifest = json.loads(data.decode("utf-8"))
                print(
                    f"[render] manifest fetch OK ({len(data)} bytes)",
                    file=sys.stderr,
                )
                return manifest
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_err = exc
            print(
                f"[render] manifest fetch attempt {attempt} failed: {exc}",
                file=sys.stderr,
            )
            if attempt < FETCH_RETRIES:
                print(f"[render] backing off {delay}s before retry", file=sys.stderr)
                time.sleep(delay)
    print(
        f"[render] manifest fetch exhausted retries (last error: {last_err}); "
        f"falling back to {FALLBACK_MANIFEST.relative_to(REPO_ROOT)}",
        file=sys.stderr,
    )
    return json.loads(FALLBACK_MANIFEST.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────────────────────
# render
# ─────────────────────────────────────────────────────────────────────────────

def render(identity: dict, manifest: dict, template_dir: Path = REPO_ROOT,
           template_name: str = "index.html.j2") -> str:
    """
    Render the template with the identity + manifest context.

    autoescape is deliberately OFF. The template is authored HTML
    (trusted content under version control), the identity values come
    from config.js (also trusted, version-controlled), and the
    migration surfaces include attribute values that already use
    pre-escaped HTML entities (&middot;, etc.). Enabling autoescape
    would double-encode those entities and break byte-identity with
    the pre-M3 index.html. Do NOT enable autoescape unless you also
    audit every CONFIG.identity field for HTML-unsafe content.
    """
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
        keep_trailing_newline=True,
    )
    template = env.get_template(template_name)
    return template.render(identity=identity, manifest=manifest)


def do_render(check: bool = False) -> int:
    config = parse_config(CONFIG_PATH)
    identity = config["CONFIG"]["identity"]
    manifest = fetch_manifest(identity["mediaRepoUrl"])
    output = render(identity, manifest)

    if check:
        on_disk = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        if output == on_disk:
            print("[render] --check: index.html matches template render", file=sys.stderr)
            return 0
        print(
            "[render] --check FAILED: index.html drifted from template render. "
            "Re-run `python scripts/render-portfolio.py` and commit.",
            file=sys.stderr,
        )
        return 1

    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"[render] wrote {OUTPUT_PATH.relative_to(REPO_ROOT)} ({len(output)} chars)", file=sys.stderr)
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# self-test
# ─────────────────────────────────────────────────────────────────────────────

def self_test() -> int:
    """
    Embedded smoke tests. Run with `python scripts/render-portfolio.py
    --self-test` to verify the renderer end-to-end without invoking the
    network. Five assertions cover the contract points:
      a) Node parser yields a non-empty CONFIG dict.
      b) Jinja2 substitution preserves the migration surfaces byte-for-byte.
      c) --check correctly detects drift.
      d) Manifest fetch falls back to the local file on network failure.
      e) The rendered output contains the JSON-LD Person block.
    """
    failures: list[str] = []

    # (a) Node parser yields a non-empty CONFIG dict with required fields.
    try:
        config = parse_config(CONFIG_PATH)
        identity = config["CONFIG"]["identity"]
        required = {"name", "shortName", "firstName", "lastName", "role",
                    "title", "description", "ogTitle", "ogDescription", "ogImage",
                    "canonicalUrl", "headshot", "sameAs", "twitterHandle",
                    "mediaRepoUrl", "location"}
        missing = required - set(identity.keys())
        assert not missing, f"CONFIG.identity missing fields: {missing}"
        print("[self-test] (a) Node parser yields populated CONFIG.identity: PASS")
    except Exception as exc:
        failures.append(f"(a) {exc}")
        print(f"[self-test] (a) FAIL: {exc}")

    # (b) Migration surfaces render byte-identically against a fixture.
    try:
        fixture_identity = {
            "name": "Narendranath Edara",
            "shortName": "Naren",
            "firstName": "Narendranath",
            "lastName": "Edara",
            "role": "Senior AI Platform Engineer",
            "location": "Dallas TX",
            "title": "Narendranath Edara | Senior AI Platform Engineer",
            "description": "Narendranath Edara - Senior AI Platform Engineer building production LLM systems, retrieval pipelines, and governed AI-enabled data products.",
            "ogTitle": "Narendranath Edara | Senior AI Platform Engineer",
            "ogDescription": "Production AI systems that teams can run, govern, and trust.",
            "ogImage": "/static/og-image.jpg?v=2026-04-28",
            "canonicalUrl": "https://narendranathe.github.io",
            "headshot": "/static/originals/headshot-fullbody.jpg",
            "sameAs": ["https://linkedin.com/in/narendranathe", "https://github.com/narendranathe", "https://narendranathe.substack.com"],
            "twitterHandle": "@narendranathe",
            "mediaRepoUrl": "https://narendranathe.github.io/resume2",
        }
        rendered = render(fixture_identity, manifest={})
        expected_surfaces = [
            '<meta name="description" content="Narendranath Edara - Senior AI Platform Engineer building production LLM systems, retrieval pipelines, and governed AI-enabled data products.">',
            '<meta name="author" content="Narendranath Edara">',
            '<meta property="og:title" content="Narendranath Edara | Senior AI Platform Engineer">',
            '<meta property="og:description" content="Production AI systems that teams can run, govern, and trust.">',
            '<meta property="og:url" content="https://narendranathe.github.io">',
            '<meta property="og:image" content="https://narendranathe.github.io/static/og-image.jpg?v=2026-04-28">',
            '<link rel="canonical" href="https://narendranathe.github.io">',
            '<title>Narendranath Edara | Senior AI Platform Engineer</title>',
            '<span class="logo-name">Narendranath Edara</span>',
            '<span class="logo-role">Senior AI Platform Engineer</span>',
            '<h1 class="hero-name">Narendranath<br>Edara</h1>',
            'alt="Naren Edara, Senior AI Platform Engineer"',
            'alt="Narendranath Edara" class="contact-photo"',
            '<span class="footer-name">Narendranath Edara</span>',
            '<span class="footer-tagline">Senior AI Platform Engineer &middot; Dallas TX</span>',
            'data-hover-title="LinkedIn - Narendranath Edara"',
        ]
        for surface in expected_surfaces:
            assert surface in rendered, f"missing migration surface: {surface!r}"
        print(f"[self-test] (b) {len(expected_surfaces)} migration surfaces byte-identical: PASS")
    except Exception as exc:
        failures.append(f"(b) {exc}")
        print(f"[self-test] (b) FAIL: {exc}")

    # (c) --check detects drift when index.html is altered.
    try:
        original = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.exists() else ""
        # First, ensure the on-disk file is up-to-date by rendering fresh.
        # We mock fetch_manifest so this test never touches the network.
        with mock.patch(__name__ + ".fetch_manifest", return_value=json.loads(FALLBACK_MANIFEST.read_text(encoding="utf-8"))):
            rc = do_render(check=False)
            assert rc == 0
            # Now mutate on disk and confirm --check returns 1.
            OUTPUT_PATH.write_text(OUTPUT_PATH.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
            rc_drift = do_render(check=True)
            assert rc_drift == 1, "--check should return 1 after drift"
            # And restore + confirm clean.
            do_render(check=False)
            rc_clean = do_render(check=True)
            assert rc_clean == 0, "--check should return 0 after re-render"
        # Restore prior on-disk state so self-test is non-destructive when it
        # follows a manual edit cycle.
        if original:
            OUTPUT_PATH.write_text(original, encoding="utf-8")
        print("[self-test] (c) --check detects drift correctly: PASS")
    except Exception as exc:
        failures.append(f"(c) {exc}")
        print(f"[self-test] (c) FAIL: {exc}")

    # (d) Manifest fetch falls back to local on simulated network error.
    try:
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("simulated DNS failure")):
            # Patch sleep so the test doesn't burn 7s on the backoff schedule.
            with mock.patch("time.sleep"):
                manifest = fetch_manifest("https://example.invalid/media")
        assert manifest.get("schema_version") == "1.0.0", "fallback manifest schema_version mismatch"
        assert "headshots" in manifest, "fallback manifest missing headshots section"
        print("[self-test] (d) manifest fetch falls back on network error: PASS")
    except Exception as exc:
        failures.append(f"(d) {exc}")
        print(f"[self-test] (d) FAIL: {exc}")

    # (e) Rendered output contains the JSON-LD Person block.
    try:
        config = parse_config(CONFIG_PATH)
        identity = config["CONFIG"]["identity"]
        rendered = render(identity, manifest={})
        assert '<script type="application/ld+json">' in rendered
        assert '"@type": "Person"' in rendered
        assert '"jobTitle": "Senior AI Platform Engineer"' in rendered
        assert '<meta name="twitter:card" content="summary_large_image">' in rendered
        print("[self-test] (e) rendered output contains JSON-LD + Twitter meta: PASS")
    except Exception as exc:
        failures.append(f"(e) {exc}")
        print(f"[self-test] (e) FAIL: {exc}")

    if failures:
        print(f"\n[self-test] {len(failures)} failure(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\n[self-test] all 5 assertions PASSED")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render index.html.j2 -> index.html using CONFIG.identity from config.js.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Render to memory and diff against on-disk index.html. Exit 1 if differs.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run embedded smoke tests (no network required).",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    return do_render(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
