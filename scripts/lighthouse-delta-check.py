"""Compare a Lighthouse CI run against a committed baseline.

Coexists with the absolute-threshold gate already configured in
``lighthouserc.json`` (which enforces ``performance >= 0.9`` etc.).
This script adds a *relative* gate: if any tracked category on any
tracked URL drops more than 3 points vs the baseline, fail.

Why both gates?
- The absolute gate catches absolute regressions ("perf fell below 0.9").
- The delta gate catches *creeping* regressions that stay above the
  absolute floor but trend downward (perf 0.99 -> 0.92 still passes
  absolute, but is a 7-point drop worth investigating).

Inputs
------
* ``scripts/lighthouse-baseline.json`` - committed baseline scores,
  written by milestone M1. Shape:

      {
        "https://narendranathe.github.io/": {
          "mobile":  {"performance": 0.95, "accessibility": 0.98,
                      "best_practices": 0.95, "seo": 0.92},
          "desktop": {"performance": 0.99, ...}
        },
        ...
      }

* ``.lighthouseci/manifest.json`` - default output path from
  ``treosh/lighthouse-ci-action@v11``. Configurable via positional arg.

Exit codes
----------
* 0: all deltas within tolerance (or baseline missing - we warn and pass
     so this PR doesn't break CI before M1 lands the baseline).
* 1: at least one category dropped more than ``MAX_DELTA`` points.

Stdlib-only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINE_PATH = REPO_ROOT / "scripts" / "lighthouse-baseline.json"
DEFAULT_MANIFEST = REPO_ROOT / ".lighthouseci" / "manifest.json"

# Points threshold (0-100 scale). A drop greater than this fails CI.
# Lighthouse scores are 0.0-1.0; we convert to 0-100 for human-readable
# delta math (a 3-point drop = -0.03 in raw score). The 1e-6 epsilon
# absorbs floating-point noise from the 0.01-precision baseline so an
# exact -3.0 boundary doesn't trip on FP imprecision.
MAX_DELTA = 3.0
_DELTA_EPS = 1e-6

# Categories we track. Order matters for the summary table output.
TRACKED_CATEGORIES = ("performance", "accessibility", "best_practices", "seo")

# Form factors we expect in the baseline. Each Lighthouse run targets
# one form factor (mobile xor desktop); the action can collect both.
FORM_FACTORS = ("mobile", "desktop")


def _category_key(name: str, source: dict) -> str | None:
    """Resolve a tracked-category name against a scores dict.

    Tolerates both ``best_practices`` (baseline convention) and
    ``best-practices`` (Lighthouse raw category id). Returns the key
    that's actually present in ``source``, or None if neither is.
    """
    if name in source:
        return name
    alt = name.replace("_", "-")
    if alt in source:
        return alt
    return None


def load_baseline(path: Path) -> dict | None:
    """Load the baseline JSON. Returns None if missing (graceful)."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_current(manifest_path: Path) -> dict:
    """Load Lighthouse CI's manifest.json and reshape to the baseline schema.

    ``manifest.json`` is a list of run entries, each with ``url``,
    ``isRepresentativeRun``, ``summary`` (category id -> score), and
    ``htmlPath``. We keep only representative runs and group by URL +
    form factor. Form factor is inferred from the htmlPath or summary
    metadata when present; falls back to ``mobile`` (Lighthouse default).
    """
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"unexpected manifest shape: top-level not a list ({type(raw).__name__})")

    out: dict[str, dict[str, dict[str, float]]] = {}
    for entry in raw:
        if not entry.get("isRepresentativeRun", True):
            # Skip non-representative runs to avoid double-counting.
            continue
        url = entry.get("url")
        if not url:
            continue
        summary = entry.get("summary", {}) or {}
        # Form factor: try explicit field, then guess from htmlPath name.
        form_factor = (entry.get("formFactor") or "").lower()
        if form_factor not in FORM_FACTORS:
            html_path = (entry.get("htmlPath") or "").lower()
            form_factor = "desktop" if "desktop" in html_path else "mobile"

        scores: dict[str, float] = {}
        for cat in TRACKED_CATEGORIES:
            key = _category_key(cat, summary)
            if key is not None:
                scores[cat] = float(summary[key])

        out.setdefault(url, {}).setdefault(form_factor, {}).update(scores)
    return out


def compute_deltas(
    baseline: dict,
    current: dict,
) -> tuple[list[str], list[str]]:
    """Compare baseline against current. Returns (failures, summary_lines).

    ``failures`` is a list of human-readable error strings for any
    category that dropped more than ``MAX_DELTA`` points.
    ``summary_lines`` is the full per-category delta table.
    """
    failures: list[str] = []
    summary_lines: list[str] = []

    for url, form_factors in baseline.items():
        if url not in current:
            summary_lines.append(f"WARN: baseline URL {url} missing from current run")
            continue
        for ff in FORM_FACTORS:
            base_scores = form_factors.get(ff)
            curr_scores = current[url].get(ff)
            if not base_scores:
                continue
            if not curr_scores:
                summary_lines.append(f"WARN: {url} [{ff}] missing from current run")
                continue
            for cat in TRACKED_CATEGORIES:
                base_key = _category_key(cat, base_scores)
                curr_key = _category_key(cat, curr_scores)
                if base_key is None or curr_key is None:
                    continue
                base_val = float(base_scores[base_key])
                curr_val = float(curr_scores[curr_key])
                # Both scores arrive in 0.0-1.0; deltas in points (0-100).
                delta_pts = (curr_val - base_val) * 100.0
                line = (
                    f"{url} [{ff}] {cat}: "
                    f"{base_val:.2f} -> {curr_val:.2f} ({delta_pts:+.1f} pts)"
                )
                summary_lines.append(line)
                if delta_pts < -(MAX_DELTA + _DELTA_EPS):
                    failures.append(
                        f"FAIL: {url} [{ff}] {cat} dropped {-delta_pts:.1f} pts "
                        f"(baseline {base_val:.2f} -> current {curr_val:.2f}; "
                        f"threshold > {MAX_DELTA:.0f} pts)"
                    )
    return failures, summary_lines


def run(manifest_path: Path) -> int:
    """Real-mode entry point. Returns process exit code."""
    baseline = load_baseline(BASELINE_PATH)
    if baseline is None:
        # M1 will commit the baseline; until then, warn and pass so we
        # don't break CI on the very PR that adds this script.
        print(
            f"warning: baseline {BASELINE_PATH.relative_to(REPO_ROOT)} not found; "
            "skipping delta check (will activate once M1 commits the baseline)",
            file=sys.stderr,
        )
        return 0

    if not manifest_path.exists():
        print(f"error: Lighthouse manifest not found at {manifest_path}", file=sys.stderr)
        return 1

    current = load_current(manifest_path)
    failures, summary_lines = compute_deltas(baseline, current)

    print("Lighthouse delta check:")
    for line in summary_lines:
        print(f"  {line}")
    if failures:
        print()
        for f in failures:
            print(f)
        print(f"\n{len(failures)} category delta(s) exceeded the {MAX_DELTA:.0f}-point threshold.")
        return 1
    print("\nall deltas within tolerance")
    return 0


# ---------- self-test ----------
def _self_test() -> int:
    """Synthesize fake baseline + current; assert pass/fail behaviour.

    Stdlib-only; uses plain assert. Returns 0 on success, 1 on assert
    failure (which is also raised). Keeps the surface small so this
    script can be exercised in CI without a real Lighthouse run.
    """
    url = "https://example.test/"
    baseline = {
        url: {
            "mobile":  {"performance": 0.90, "accessibility": 0.95,
                        "best_practices": 0.92, "seo": 0.93},
            "desktop": {"performance": 0.99, "accessibility": 0.99,
                        "best_practices": 0.95, "seo": 0.95},
        },
    }

    # ----- case 1: all deltas within tolerance -----
    current_ok = {
        url: {
            "mobile":  {"performance": 0.89, "accessibility": 0.96,
                        "best_practices": 0.92, "seo": 0.91},  # -1, +1, 0, -2 pts
            "desktop": {"performance": 0.98, "accessibility": 0.99,
                        "best_practices": 0.95, "seo": 0.95},
        },
    }
    failures, summary = compute_deltas(baseline, current_ok)
    assert failures == [], f"case 1: expected no failures, got {failures}"
    assert any("performance" in s for s in summary), "case 1: summary missing performance row"
    assert len(summary) == 8, f"case 1: expected 8 summary rows (4 cats x 2 form factors), got {len(summary)}"

    # ----- case 2: single 4-point drop fails -----
    current_drop = {
        url: {
            "mobile":  {"performance": 0.85, "accessibility": 0.95,  # -5 pts performance
                        "best_practices": 0.92, "seo": 0.93},
            "desktop": {"performance": 0.99, "accessibility": 0.99,
                        "best_practices": 0.95, "seo": 0.95},
        },
    }
    failures, _ = compute_deltas(baseline, current_drop)
    assert len(failures) == 1, f"case 2: expected exactly 1 failure, got {len(failures)}: {failures}"
    assert "performance" in failures[0], f"case 2: failure should cite performance, got {failures[0]}"
    assert "5.0 pts" in failures[0] or "5.00" in failures[0], f"case 2: failure should report 5 pts: {failures[0]}"

    # ----- case 3: hyphenated 'best-practices' in current run -----
    current_hyphen = {
        url: {
            "mobile":  {"performance": 0.90, "accessibility": 0.95,
                        "best-practices": 0.92, "seo": 0.93},
            "desktop": {"performance": 0.99, "accessibility": 0.99,
                        "best-practices": 0.95, "seo": 0.95},
        },
    }
    failures, summary = compute_deltas(baseline, current_hyphen)
    assert failures == [], f"case 3: hyphenated key should match underscore baseline, got {failures}"
    assert any("best_practices" in s for s in summary), "case 3: summary should normalize to underscore"

    # ----- case 4: exactly -3 pts is within tolerance (boundary) -----
    current_boundary = {
        url: {
            "mobile":  {"performance": 0.87, "accessibility": 0.95,  # exactly -3 pts
                        "best_practices": 0.92, "seo": 0.93},
            "desktop": {"performance": 0.99, "accessibility": 0.99,
                        "best_practices": 0.95, "seo": 0.95},
        },
    }
    failures, _ = compute_deltas(baseline, current_boundary)
    assert failures == [], f"case 4: -3.0 pts should be within tolerance, got {failures}"

    # ----- case 5: multiple categories dropping yields multiple failures -----
    current_multi = {
        url: {
            "mobile":  {"performance": 0.80, "accessibility": 0.85,  # -10, -10
                        "best_practices": 0.80, "seo": 0.80},        # -12, -13
            "desktop": {"performance": 0.99, "accessibility": 0.99,
                        "best_practices": 0.95, "seo": 0.95},
        },
    }
    failures, _ = compute_deltas(baseline, current_multi)
    assert len(failures) == 4, f"case 5: expected 4 failures (all mobile cats), got {len(failures)}"

    # ----- case 6: missing form factor in current is a warning, not a failure -----
    current_partial = {
        url: {
            "mobile":  {"performance": 0.90, "accessibility": 0.95,
                        "best_practices": 0.92, "seo": 0.93},
            # desktop intentionally missing
        },
    }
    failures, summary = compute_deltas(baseline, current_partial)
    assert failures == [], f"case 6: missing form factor should not fail, got {failures}"
    assert any("WARN" in s and "desktop" in s for s in summary), \
        f"case 6: summary should warn about missing desktop, got {summary}"

    # ----- case 7: baseline URL absent from current is a warning -----
    failures, summary = compute_deltas(baseline, {})
    assert failures == [], f"case 7: missing URL should not fail, got {failures}"
    assert any("WARN" in s and url in s for s in summary), \
        f"case 7: summary should warn about missing URL, got {summary}"

    print("self-test: 7 cases / 14 assertions passed")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "manifest",
        nargs="?",
        default=str(DEFAULT_MANIFEST),
        help=f"Path to Lighthouse CI manifest.json (default: {DEFAULT_MANIFEST.relative_to(REPO_ROOT)})",
    )
    p.add_argument("--self-test", action="store_true", help="Run internal assertion suite and exit.")
    args = p.parse_args()

    if args.self_test:
        return _self_test()
    return run(Path(args.manifest))


if __name__ == "__main__":
    raise SystemExit(main())
