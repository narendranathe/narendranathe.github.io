#!/usr/bin/env python3
"""
Structural HTML invariants for the portfolio.

Asserts the impact-strip pattern is present + semantically correct on every
flagship project card, blocks scrapped-project claims from re-entering, and
catches regressions in the CSS module that powers the strip.

Uses only the Python standard library (html.parser) — no BeautifulSoup,
no jsonschema. Drop-in for any CI workflow.

Usage
-----
    python scripts/test-portfolio.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
STYLES_CSS = REPO_ROOT / "styles.css"

# Number of impact strips expected on the home page. Five flagship cards
# carry a strip after the v3 trim: AutoApply AI, tailor-resume, JobScout
# (system-grid) + Azure Platform Engineering, repo-context-hooks
# (supporting-row). Cards with no defensible quantified impact (Fraud
# Detection, Portfolio Risk, FinTune) intentionally have no strip — see
# docs/impact-strip-pattern.md "no strip is better than a weak strip."
EXPECTED_STRIP_COUNT = 5


# ------- HTML parsing helpers -------
class StripCollector(HTMLParser):
    """Collect <dl class="impact-strip"> elements + every id attribute on
    the page (for cross-page uniqueness check)."""

    def __init__(self) -> None:
        super().__init__()
        self.strips: list[dict] = []
        self.all_ids: list[tuple[str, str]] = []  # (tag, id)
        self.inline_styles_in_strips: list[tuple[str, dict]] = []

        self._current_strip: dict | None = None
        self._current_stat: dict | None = None
        self._collect_text_into: str | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        attrs = dict(attrs_list)
        classes = (attrs.get("class") or "").split()

        if "id" in attrs:
            self.all_ids.append((tag, attrs["id"]))

        # Inside a strip, flag any inline style= on any element.
        if self._current_strip is not None and "style" in attrs:
            self.inline_styles_in_strips.append((tag, attrs))

        if tag == "dl" and "impact-strip" in classes:
            self._current_strip = {
                "aria-labelledby": attrs.get("aria-labelledby"),
                "aria-label": attrs.get("aria-label"),
                "stats": [],
            }
            return

        if self._current_strip is None:
            return

        if tag == "div" and "impact-stat" in classes:
            self._current_stat = {"value": None, "label": None}

        if self._current_stat is None:
            return

        if tag == "dt" and "impact-value" in classes:
            self._collect_text_into = "value"
            self._buf = []
        elif tag == "dd" and "impact-label" in classes:
            self._collect_text_into = "label"
            self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if self._current_strip is None:
            return
        if self._collect_text_into is not None and tag in ("dt", "dd"):
            text = "".join(self._buf).strip()
            if self._current_stat is not None:
                self._current_stat[self._collect_text_into] = text
            self._collect_text_into = None
            self._buf = []
        if tag == "div" and self._current_stat is not None:
            self._current_strip["stats"].append(self._current_stat)
            self._current_stat = None
        if tag == "dl":
            self.strips.append(self._current_strip)
            self._current_strip = None

    def handle_data(self, data: str) -> None:
        if self._collect_text_into is not None:
            self._buf.append(data)


def collect(html: str) -> StripCollector:
    p = StripCollector()
    p.feed(html)
    return p


# ------- Test cases -------
def test_index_html_exists() -> None:
    assert INDEX_HTML.exists(), f"missing {INDEX_HTML}"


def test_styles_css_has_impact_strip_module() -> None:
    css = STYLES_CSS.read_text(encoding="utf-8")
    for selector in (".impact-strip", ".impact-stat", ".impact-value", ".impact-label"):
        assert selector in css, f"styles.css missing {selector}"


def test_strip_count_matches_expected(strips: list[dict]) -> None:
    assert len(strips) == EXPECTED_STRIP_COUNT, (
        f"expected {EXPECTED_STRIP_COUNT} impact strips on index.html "
        f"after v3 trim, found {len(strips)}"
    )


def test_each_strip_uses_aria_labelledby(strips: list[dict]) -> None:
    """v3 changed from aria-label to aria-labelledby pointing at the
    card's <h3> heading — avoids announcing the project name twice."""
    for i, s in enumerate(strips):
        adby = s.get("aria-labelledby")
        assert adby, (
            f"strip #{i} missing aria-labelledby; v3 requires it (not aria-label)"
        )
        assert not s.get("aria-label"), (
            f"strip #{i} has both aria-label and aria-labelledby; pick one (prefer aria-labelledby)"
        )


def test_aria_labelledby_targets_exist(strips: list[dict], all_ids: list) -> None:
    id_set = {i for _, i in all_ids}
    for i, s in enumerate(strips):
        target = s["aria-labelledby"]
        assert target in id_set, (
            f"strip #{i} aria-labelledby={target!r} but no element with id={target!r} found on the page"
        )


def test_each_strip_has_3_to_5_stats(strips: list[dict]) -> None:
    for i, s in enumerate(strips):
        n = len(s["stats"])
        assert 3 <= n <= 5, (
            f"strip #{i} has {n} stats; spec requires 3-5 per docs/impact-strip-pattern.md"
        )


def test_each_stat_has_value_and_label(strips: list[dict]) -> None:
    for i, s in enumerate(strips):
        for j, stat in enumerate(s["stats"]):
            assert stat["value"], f"strip #{i} stat {j} missing dt.impact-value text"
            assert stat["label"], f"strip #{i} stat {j} missing dd.impact-label text"


def test_no_scrapped_exponenthr_outcomes(html: str) -> None:
    """ExponentHR NL-to-SQL Architecture 4 was scrapped. Its outcomes
    (400 enterprise clients, 40% support ticket reduction, 12s -> 4s
    query response) cannot be cited anywhere on the portfolio."""
    forbidden = [
        "400 enterprise client",
        "400+ enterprise client",
        "support ticket reduction",
        "catalog-driven NL-to-SQL",
        "FAISS retrieval",
    ]
    for needle in forbidden:
        assert needle.lower() not in html.lower(), (
            f"Found scrapped-project claim {needle!r} in index.html — must remove."
        )


def test_no_inline_style_attribute_on_strips(inline_styles: list) -> None:
    assert not inline_styles, (
        f"Found inline style= attributes inside impact strips: {inline_styles}; "
        "use the .impact-* classes instead."
    )


def test_jetbrains_mono_loaded(html: str) -> None:
    assert "JetBrains+Mono" in html or "JetBrains Mono" in html, (
        "JetBrains Mono not loaded; impact-value font-family will fall back."
    )


def test_css_uses_tabular_nums() -> None:
    css = STYLES_CSS.read_text(encoding="utf-8")
    assert "tabular-nums" in css, (
        "CSS does not declare tabular-nums; font-swap will cause CLS on .impact-value."
    )


def test_css_has_print_block() -> None:
    css = STYLES_CSS.read_text(encoding="utf-8")
    has_print = re.search(
        r"@media\s+print\s*\{[^}]*\.impact-strip", css, flags=re.S
    )
    assert has_print, "CSS does not include @media print block for impact-strip"


def test_css_mobile_breakpoint_at_600px() -> None:
    css = STYLES_CSS.read_text(encoding="utf-8")
    has_breakpoint = re.search(
        r"@media\s*\(\s*min-width:\s*600px\s*\)\s*\{[^}]*\.impact-stat",
        css,
        flags=re.S,
    )
    assert has_breakpoint, (
        "CSS missing @media (min-width: 600px) rule for .impact-stat — "
        "needed for WCAG 1.4.10 reflow on small viewports."
    )


def test_css_uses_warm_palette_tokens() -> None:
    """v3 visual review: strip must use --accent-warm and --fg/--fg-muted
    so it ties to the site's existing warm palette rather than introducing
    cool grays. This is a brand-fit assertion."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    impact_block = re.search(
        r"\.impact-strip[^{]*\{[\s\S]*?(?=/\*={5}|\Z)", css, flags=re.S
    )
    assert impact_block, "could not locate .impact-strip CSS block"
    block = impact_block.group(0)
    assert "var(--accent-warm" in block, (
        ".impact-stat must use var(--accent-warm) for the left rule"
    )
    assert "var(--fg" in block, (
        ".impact-value must use var(--fg) for text color"
    )


def test_repo_context_hooks_card_present(html: str) -> None:
    assert "repo-context-hooks" in html, "Expected a card mentioning repo-context-hooks"


def test_no_legacy_system_rail_in_systems_grid(html: str) -> None:
    """The system-rail (single headline metric) was dropped in favor
    of the multi-stat impact strip in v3 to avoid competing typographic
    hierarchies on the same card."""
    blocks = re.findall(
        r'<article class="system-card"[^>]*>.*?</article>', html, flags=re.S
    )
    for blk in blocks:
        assert "system-rail" not in blk, (
            "system-rail re-introduced inside system-card; remove and rely on impact strip."
        )


def test_all_ids_unique(all_ids: list) -> None:
    """No two elements share an id on the page — ID collisions would
    break aria-labelledby / aria-describedby resolution and CSS #id
    selectors. Caught at structural level, not at runtime in the
    browser."""
    seen: dict[str, str] = {}
    dupes: list[tuple[str, str, str]] = []
    for tag, id_ in all_ids:
        if id_ in seen:
            dupes.append((id_, seen[id_], tag))
        else:
            seen[id_] = tag
    assert not dupes, (
        f"Duplicate id attributes on page: {dupes}; aria-labelledby and CSS selectors will break."
    )


# ------- Test runner -------
TESTS = [
    test_index_html_exists,
    test_styles_css_has_impact_strip_module,
    test_strip_count_matches_expected,
    test_each_strip_uses_aria_labelledby,
    test_aria_labelledby_targets_exist,
    test_each_strip_has_3_to_5_stats,
    test_each_stat_has_value_and_label,
    test_no_scrapped_exponenthr_outcomes,
    test_no_inline_style_attribute_on_strips,
    test_jetbrains_mono_loaded,
    test_css_uses_tabular_nums,
    test_css_has_print_block,
    test_css_mobile_breakpoint_at_600px,
    test_css_uses_warm_palette_tokens,
    test_repo_context_hooks_card_present,
    test_no_legacy_system_rail_in_systems_grid,
    test_all_ids_unique,
]


def run_self_test() -> int:
    if not INDEX_HTML.exists():
        print(f"missing {INDEX_HTML}", file=sys.stderr)
        return 1
    html = INDEX_HTML.read_text(encoding="utf-8")
    p = collect(html)

    failed: list[tuple[str, str]] = []
    print(f"portfolio self-test ({len(TESTS)} assertions)...")
    for fn in TESTS:
        try:
            sig = fn.__code__.co_varnames[: fn.__code__.co_argcount]
            kwargs = {}
            if "strips" in sig:
                kwargs["strips"] = p.strips
            if "html" in sig:
                kwargs["html"] = html
            if "inline_styles" in sig:
                kwargs["inline_styles"] = p.inline_styles_in_strips
            if "all_ids" in sig:
                kwargs["all_ids"] = p.all_ids
            fn(**kwargs)
            print(f"  ok    {fn.__name__}")
        except AssertionError as e:
            failed.append((fn.__name__, str(e)))
            print(f"  FAIL  {fn.__name__}")
            print(f"        {e}")

    if failed:
        print(f"\n{len(failed)}/{len(TESTS)} failed")
        return 1
    print(f"\nall {len(TESTS)} assertions passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Portfolio HTML invariants self-test")
    parser.add_argument("--self-test", action="store_true", help="run all assertions")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
