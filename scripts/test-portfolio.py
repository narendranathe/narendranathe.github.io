#!/usr/bin/env python3
"""
Structural HTML invariants for the portfolio.

Asserts the impact-strip pattern is present + semantically correct on every
proof-point card, blocks scrapped-project claims from re-entering, and
catches regressions in the CSS module that powers the strip.

The home page was cut down to four sections (hero, proof points, prior
work, projects) and now loads home.css with no JavaScript. The guards
below encode that shape so the page cannot quietly grow back: no script
bundle, four sections, four hero links, five repos.

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
# styles.css still dresses the case-study pages (autoapply-ai.html,
# fintune.html, ...). The home page no longer loads it, so the CSS
# assertions below target home.css instead.
HOME_CSS = REPO_ROOT / "home.css"
STYLES_CSS = REPO_ROOT / "styles.css"
SUPPLY_CHAIN_POST = REPO_ROOT / "content" / "posts" / "repo-context-hooks-supply-chain.html"

REQUIRED_POST_SECTIONS = ("problem", "constraints", "design", "tradeoffs", "outcome")
POST_MIN_WORDS = 1500
POST_MAX_WORDS = 2500

# Number of impact strips expected on the home page: one per card. Three
# proof cards (ExponentHR, Fraud Detection & FinTune, repo-context-hooks)
# plus the two prior-work cards (Zomato, udaan.com), which carry the same
# four-row structure so the eye reads every card the same way.
EXPECTED_STRIP_COUNT = 5

# The home page shape. Four <section class="section"> blocks plus the
# hero, four hero links, five repos, one call to action.
EXPECTED_SECTION_COUNT = 4
EXPECTED_HERO_LINKS = 4
EXPECTED_REPO_COUNT = 5


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


# ------- Visible-text DOM walker -------
# A screen reader / human reader perceives text from inline siblings as
# space-joined (<span>400</span><span>enterprise clients</span> reads as
# "400 enterprise clients"). The raw-HTML substring check below misses
# this case because the words live in adjacent spans. This walker
# rebuilds the visible-text concatenation so adjacent-span leaks of
# scrapped claims are caught.
_VISIBLE_TEXT_SUPPRESS_TAGS = frozenset(
    {"script", "style", "template", "noscript"}
)
# Zero-width joiner / BOM characters - screen readers ignore them, but
# Python's \s does not match them, so a paste from Word/Google Docs
# could re-introduce a forbidden phrase split by ZWSP and bypass the
# substring guard. Strip these before whitespace collapse.
_ZERO_WIDTH_RE = re.compile(r"[​-‍﻿]")


class VisibleTextCollector(HTMLParser):
    """Concatenate visible text-node content; emit a space at every tag
    boundary so adjacent inline siblings don't fuse into one token.
    Skips <script>/<style>/<template>/<noscript>; <svg> contents (title,
    desc, text) ARE included since they are a11y-visible."""

    def __init__(self) -> None:
        # convert_charrefs=True (Python 3.5+ default) auto-decodes
        # entities into handle_data - so &#52;00 surfaces as "400" and
        # entity-encoded leaks cannot bypass the substring guard.
        super().__init__(convert_charrefs=True)
        self._suppress_depth = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        if tag in _VISIBLE_TEXT_SUPPRESS_TAGS:
            self._suppress_depth += 1
        # Space at every element boundary; final \s+ collapse pays the bill.
        self._buf.append(" ")

    def handle_startendtag(self, tag: str, attrs_list: list) -> None:
        # XHTML self-closing form (<br/>, <img/>); no end tag will fire.
        self._buf.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in _VISIBLE_TEXT_SUPPRESS_TAGS and self._suppress_depth > 0:
            self._suppress_depth -= 1
        self._buf.append(" ")

    def handle_data(self, data: str) -> None:
        if self._suppress_depth == 0:
            self._buf.append(data)

    def text(self) -> str:
        # Replace zero-width chars with a space (not empty): ZWSP is a
        # word boundary to screen readers, so "400<ZWSP>enterprise"
        # should normalise to "400 enterprise" not "400enterprise".
        text = _ZERO_WIDTH_RE.sub(" ", "".join(self._buf))
        return re.sub(r"\s+", " ", text).strip()


def extract_visible_text(html: str) -> str:
    p = VisibleTextCollector()
    p.feed(html)
    return p.text()


# Phrases that uniquely identify the scrapped ExponentHR NL-to-SQL
# Architecture 4 claim. Single source of truth for both the raw-HTML
# guard (catches attribute values, HTML comments, <script> bodies) and
# the rendered-text guard (catches adjacent-span leaks). All entries
# lowercase; comparisons normalise both sides via .lower().
#
# Land mine: the ExponentHR card on index.html says "support desk
# volume ~80%" - a future synonym swap from "desk" to "ticket" would
# trip "support ticket reduction". Preserve "desk" or rephrase rather
# than narrowing the guard.
FORBIDDEN_SCRAPPED_CLAIMS: tuple[str, ...] = (
    # "400 enterprise clients" - main offender. Substring covers plural.
    "400 enterprise client",
    "400+ enterprise client",
    # 40% support-ticket-reduction claim
    "support ticket reduction",
    # 12s -> 4s query-response claim, ASCII + Unicode arrow variants
    "12s to 4s",
    "12s -> 4s",
    "12s->4s",
    "12s → 4s",
    "12s→4s",
    "12 second",
    # Architecture vocabulary
    "catalog-driven nl-to-sql",
    "faiss retrieval",
)


# Claims marked [BLOCKED] or excluded in GROUND_TRUTH.md. These are not
# scrapped-project leftovers — they are figures that fail arithmetic,
# contradict a primary document, or claim ownership of a tool that was
# never owned. Each one reached a live surface at least once by drifting
# from "suggested phrasing" in one draft into "stated fact" in the next,
# which is the failure mode this list exists to make impossible.
#
# Checked against every public HTML page, not just index.html, because
# the case-study pages are reachable by URL and are what a recruiter
# following a resume link actually lands on.
#
# Do not delete an entry to make a build pass. Either the claim is
# wrong (fix the page) or GROUND_TRUTH.md changed (fix it there first).
BLOCKED_CLAIMS: tuple[tuple[str, str], ...] = (
    # Udaan: $4M needs a ~$57M base; documented city GMV is ~$8.1M/yr.
    ("$4 million", "Udaan savings figure does not reconcile with documented GMV; ship the 7% ROI"),
    ("$4m", "Udaan savings figure does not reconcile with documented GMV"),
    # JobScout monitors 109 career pages, not 130+.
    ("130+", "JobScout monitors 109 career pages"),
    # Fraud platform: measured P99 is 1.12 ms, which is not sub-millisecond.
    ("sub-ms", "fraud P99 is 1.12 ms, not sub-millisecond"),
    ("sub-millisecond", "fraud P99 is 1.12 ms, not sub-millisecond"),
    ("94%+ model accuracy", "no ground-truth backing for a fraud accuracy figure"),
    ("94%+ detection accuracy", "no ground-truth backing for a fraud accuracy figure"),
    ("&lt;1ms", "fraud P99 is 1.12 ms, not under 1 ms"),
    ("<1ms", "fraud P99 is 1.12 ms, not under 1 ms"),
    ("sub-second var", "portfolio-risk pipeline is console-only; frame as in progress"),
    ("live p&amp;l tracking", "portfolio-risk pipeline is console-only; frame as in progress"),
    # Portfolio Risk: Spark-to-FastAPI handoff is console-only.
    ("47.8 tps", "not supported by the portfolio-risk repo"),
    ("15k+ records", "not supported by the portfolio-risk repo"),
    ("live risk views", "the Spark to FastAPI handoff is console-only"),
    # Always On terminology: Contained AAG, never containerized.
    ("containerized aag", "the term is Contained AAG - a different thing entirely"),
    # Degree name on the diploma.
    ("m.s. data science", "the degree is MS Information Science and Technology"),
    ("ms data science", "the degree is MS Information Science and Technology"),
    # Permanent exclusions: tools never owned in production.
    ("unity catalog", "permanent exclusion - never owned in production"),
    ("delta live tables", "permanent exclusion - never owned in production"),
    ("foundry bi engine", "permanent exclusion"),
    ("networkx join resolver", "permanent exclusion"),
    ("claude query planner", "permanent exclusion"),
    # Tenure: 6 years professional, 3 in data engineering.
    ("seven years", "6 years professional, 3 in data engineering"),
    ("eight years of t-sql", "the 2018-2021 years ran on Excel, Data Studio, and Tableau"),
)

# Every page a recruiter can reach from a resume link.
PUBLIC_HTML: tuple[str, ...] = (
    "index.html", "autoapply-ai.html", "tailor-resume.html", "jobscout.html",
    "portfolio-risk.html", "fintune.html", "fraud-detection.html",
    "content/posts/repo-context-hooks-supply-chain.html",
)


# ------- Test cases -------
def test_index_html_exists() -> None:
    assert INDEX_HTML.exists(), f"missing {INDEX_HTML}"


def test_no_blocked_claims_on_any_public_page() -> None:
    """Ground-truth gate. Runs over raw HTML AND rendered text on every
    public page, so a blocked figure cannot hide in a meta description,
    an alt attribute, an SVG <desc>, or a pair of adjacent spans."""
    failures: list[str] = []
    for rel in PUBLIC_HTML:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        body = path.read_text(encoding="utf-8")
        haystacks = (body.lower(), extract_visible_text(body).lower())
        for phrase, reason in BLOCKED_CLAIMS:
            if any(phrase in h for h in haystacks):
                failures.append(f"{rel}: {phrase!r} - {reason}")
    assert not failures, (
        "Claims blocked by GROUND_TRUTH.md found on public pages:\n  "
        + "\n  ".join(failures)
    )


def test_home_css_exists_and_index_links_it() -> None:
    assert HOME_CSS.exists(), f"missing {HOME_CSS}"
    html = INDEX_HTML.read_text(encoding="utf-8")
    assert 'href="home.css"' in html, "index.html must load home.css"
    assert 'href="styles.css"' not in html, (
        "index.html must not load styles.css — that sheet exists for the "
        "case-study pages and is mostly rules for sections this page no "
        "longer has."
    )


def test_home_css_has_impact_strip_module() -> None:
    css = HOME_CSS.read_text(encoding="utf-8")
    for selector in (".impact-strip", ".impact-stat", ".impact-value", ".impact-label"):
        assert selector in css, f"home.css missing {selector}"


def test_home_css_uses_tabular_nums() -> None:
    css = HOME_CSS.read_text(encoding="utf-8")
    assert "tabular-nums" in css, (
        "home.css does not declare tabular-nums; font-swap will cause CLS on .impact-value."
    )


def test_home_css_has_print_block() -> None:
    css = HOME_CSS.read_text(encoding="utf-8")
    has_print = re.search(r"@media\s+print\s*\{[\s\S]*?\.impact-strip", css)
    assert has_print, "home.css does not include @media print block for impact-strip"


def test_home_css_mobile_breakpoint_at_600px() -> None:
    """Guard the desktop breakpoint that switches impact-strip values
    from wrap-allowed (mobile, WCAG 1.4.10 reflow at 320px) to single-
    line (>=600px). Targets .impact-value specifically — applying nowrap
    to the whole .impact-stat overflows the grid column on long labels."""
    css = HOME_CSS.read_text(encoding="utf-8")
    has_breakpoint = re.search(
        r"@media\s*\(\s*min-width:\s*600px\s*\)\s*\{[\s\S]*?\.impact-value[\s\S]*?white-space\s*:\s*nowrap",
        css,
    )
    assert has_breakpoint, (
        "home.css missing @media (min-width: 600px) rule applying "
        "white-space: nowrap to .impact-value."
    )


def test_home_css_uses_warm_palette_tokens() -> None:
    """The strip must use --accent-warm and --fg/--fg-muted so it ties to
    the site's warm palette rather than introducing cool grays."""
    css = HOME_CSS.read_text(encoding="utf-8")
    impact_block = re.search(r"\.impact-strip[\s\S]*?(?=/\* -{3,}|\Z)", css)
    assert impact_block, "could not locate .impact-strip CSS block in home.css"
    block = impact_block.group(0)
    assert "var(--accent-warm" in block, (
        ".impact-stat must use var(--accent-warm) for the left rule"
    )
    assert "var(--fg" in block, ".impact-value must use var(--fg) for text color"


def test_index_loads_no_javascript_bundle(html: str) -> None:
    """The home page ships no behavior: no splash animation, no reveal
    observer, no hover previews, no command palette. Everything renders
    on first paint. The only permitted <script> is the deferred
    analytics beacon, which draws nothing."""
    assert 'src="app.js"' not in html, (
        "index.html re-added app.js; the home page is meant to render "
        "with zero JavaScript."
    )
    srcs = re.findall(r'<script[^>]*\ssrc="([^"]+)"', html)
    for src in srcs:
        assert "plausible.io" in src, (
            f"unexpected script on the home page: {src!r}. Only the "
            "analytics beacon is allowed."
        )
    assert "splash" not in html.lower(), "splash screen re-added to index.html"
    assert "data-reveal" not in html, (
        "data-reveal re-added; it sets opacity:0 and needs JS to undo, so "
        "content disappears when the observer does not run."
    )


def test_index_has_expected_section_count(html: str) -> None:
    """Hero plus exactly three sections: proof, prior work, projects."""
    sections = re.findall(r'<section class="section"[^>]*id="([^"]+)"', html)
    assert sections == ["proof", "before", "projects", "contact"], (
        f"expected sections ['proof', 'before', 'projects', 'contact'], found {sections}"
    )
    assert len(sections) == EXPECTED_SECTION_COUNT
    assert '<section class="hero">' in html, "hero section missing"


def test_hero_has_exactly_four_links(html: str) -> None:
    """Resume, LinkedIn, GitHub, Email — and nothing else. The hero is a
    six-second scan; every extra link costs one of those seconds."""
    nav = re.search(r'<nav class="hero-links"[^>]*>([\s\S]*?)</nav>', html)
    assert nav, "hero-links nav not found"
    hrefs = re.findall(r'href="([^"]+)"', nav.group(1))
    assert len(hrefs) == EXPECTED_HERO_LINKS, (
        f"hero must carry exactly {EXPECTED_HERO_LINKS} links, found "
        f"{len(hrefs)}: {hrefs}"
    )
    assert any("resume.pdf" in h for h in hrefs), "hero missing resume link"
    assert any("linkedin.com" in h for h in hrefs), "hero missing LinkedIn link"
    assert any("github.com" in h for h in hrefs), "hero missing GitHub link"
    assert any(h.startswith("mailto:") for h in hrefs), "hero missing email link"


def test_hero_carries_no_extra_content(html: str) -> None:
    """Name, role, one line, four links. No portrait, no metric grid, no
    animated terminal, no availability badge."""
    hero = re.search(r'<section class="hero">([\s\S]*?)</section>', html)
    assert hero, "hero section not found"
    body = hero.group(1)
    for tag in ("<img", "<picture", "<svg", "<ul", "<video", "<canvas"):
        assert tag not in body, f"hero contains {tag}; hero is text and links only"
    assert '<h2 class="hero-role">' in body, "hero missing the role + years <h2>"
    paragraphs = re.findall(r'<p class="([^"]+)"', body)
    assert paragraphs == ["hero-line"], (
        f"hero should carry exactly one paragraph, the value proposition; found {paragraphs}"
    )


def test_projects_section_lists_expected_repo_count(html: str) -> None:
    repos = re.findall(r'<a class="repo-name" href="([^"]+)"', html)
    assert len(repos) == EXPECTED_REPO_COUNT, (
        f"expected {EXPECTED_REPO_COUNT} repos in the projects list, found "
        f"{len(repos)}: {repos}"
    )
    for url in repos:
        assert url.startswith("https://github.com/"), (
            f"project entries link straight to GitHub; got {url!r}"
        )


def test_every_claim_number_has_a_baseline_or_unit(strips: list[dict]) -> None:
    """An impact value has to be readable on its own: either a
    before/after pair (30 min -> <8 min), a unit (100+ TPS), or a
    named control (Sigstore + CodeQL). A bare adjective is not a metric."""
    for i, s in enumerate(strips):
        for j, stat in enumerate(s["stats"]):
            value = stat["value"]
            has_arrow = "→" in value or "->" in value or "&rarr;" in value
            has_digit = any(ch.isdigit() for ch in value)
            has_named_control = value[:1].isupper()
            assert has_arrow or has_digit or has_named_control, (
                f"strip #{i} stat {j} value {value!r} carries no baseline, "
                f"number, or named control"
            )


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
    """Defense-in-depth raw-HTML check: covers attribute values
    (alt=, title=, aria-label=), HTML comments, and <script> bodies
    that the rendered-text guard cannot see. Complemented by the
    rendered-text guard below which catches adjacent-span leaks this
    raw substring search misses."""
    lower_html = html.lower()
    for phrase in FORBIDDEN_SCRAPPED_CLAIMS:
        assert phrase not in lower_html, (
            f"Found scrapped-project claim {phrase!r} in index.html - must remove."
        )


def test_no_scrapped_exponenthr_outcomes_in_rendered_text(html: str) -> None:
    """Rendered-text guard: walks the DOM, concatenates visible text
    with element-boundary spaces, then substring-checks against the
    scrapped-claim phrase list. Catches leaks that span adjacent
    elements (e.g. <span>400</span><span>enterprise clients</span>)
    which the raw-HTML substring check above silently passes."""
    rendered = extract_visible_text(html).lower()
    for phrase in FORBIDDEN_SCRAPPED_CLAIMS:
        assert phrase not in rendered, (
            f"Found scrapped-project phrase {phrase!r} in rendered DOM "
            f"text of index.html - must remove (rendered-text guard)."
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


def test_repo_context_hooks_card_present(html: str) -> None:
    assert "repo-context-hooks" in html, "Expected a card mentioning repo-context-hooks"


def test_supply_chain_post_exists() -> None:
    assert SUPPLY_CHAIN_POST.exists(), (
        f"missing {SUPPLY_CHAIN_POST} (issue #64 + #56 architecture write-up)"
    )


def test_supply_chain_post_has_required_sections() -> None:
    """Post must follow Problem -> Constraints -> Design -> Tradeoffs -> Outcome."""
    html = SUPPLY_CHAIN_POST.read_text(encoding="utf-8")
    for sec in REQUIRED_POST_SECTIONS:
        assert f'id="{sec}"' in html, (
            f'supply-chain post missing <section id="{sec}">; '
            "required by Problem/Constraints/Design/Tradeoffs/Outcome template."
        )


def test_supply_chain_post_word_count_in_range() -> None:
    html = SUPPLY_CHAIN_POST.read_text(encoding="utf-8")
    main_match = re.search(r"<main[^>]*>(.*?)</main>", html, flags=re.S)
    assert main_match, "post missing <main> element"
    text = re.sub(r"<[^>]+>", " ", main_match.group(1))
    text = re.sub(r"\s+", " ", text)
    words = len(text.split())
    assert POST_MIN_WORDS <= words <= POST_MAX_WORDS, (
        f"supply-chain post word count {words} outside "
        f"[{POST_MIN_WORDS}, {POST_MAX_WORDS}] (HN-eligible budget)."
    )


def test_supply_chain_post_has_inline_svg_diagram() -> None:
    """Inline SVG with <title> and <desc> for a11y, currentColor for
    light/dark/print parity (impact-strip pattern conventions)."""
    html = SUPPLY_CHAIN_POST.read_text(encoding="utf-8")
    assert "<svg" in html, "post missing inline <svg> diagram"
    svg_match = re.search(r"<svg[^>]*>(.*?)</svg>", html, flags=re.S)
    assert svg_match, "post <svg> not closed properly"
    svg_body = svg_match.group(0)
    assert "<title" in svg_body, "post <svg> missing <title> for a11y"
    assert "<desc" in svg_body, "post <svg> missing <desc> for a11y"
    assert 'role="img"' in svg_body, "post <svg> missing role='img'"
    assert "currentColor" in svg_body, (
        "post <svg> hardcodes color; must use currentColor for dark/print parity"
    )


def test_supply_chain_post_no_scrapped_outcomes() -> None:
    """ExponentHR NL-to-SQL Architecture 4 was scrapped; cannot reappear here."""
    html = SUPPLY_CHAIN_POST.read_text(encoding="utf-8")
    forbidden = [
        "400 enterprise client",
        "support ticket reduction",
        "catalog-driven NL-to-SQL",
        "FAISS retrieval",
    ]
    for needle in forbidden:
        assert needle.lower() not in html.lower(), (
            f"Found scrapped-project claim {needle!r} in supply-chain post."
        )


def _skills_section_html(html: str) -> str:
    """Extract the inner HTML of the <section id="skills"> block, raising
    AssertionError if the section is missing or malformed. Reused by the
    skills-grid assertions below to keep them scoped."""
    start = html.find('<section class="section" id="skills">')
    if start == -1:
        # Allow class ordering / attribute ordering tolerance
        m = re.search(r'<section[^>]*id="skills"[^>]*>', html)
        assert m, "<section id=\"skills\"> not found in index.html"
        start = m.start()
    end = html.find("</section>", start)
    assert end != -1, "<section id=\"skills\"> not closed"
    return html[start:end]


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


def test_all_local_links_resolve() -> None:
    """Issue #43: every relative-path href and same-page #fragment in
    every HTML file must resolve to a real file or element. External
    URLs are deliberately NOT checked here — they're network-dependent
    and flaky on CI; run `python scripts/verify-links.py --live` for
    that. The local-only check is fast, deterministic, and catches the
    classes of regression that actually break the site (typos in repo
    slugs, removed pages, broken section anchors)."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "verify-links.py")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"verify-links.py reported failures:\n{result.stdout}\n{result.stderr}"
    )


def test_public_identity_surfaces_use_canonical_title() -> None:
    """Issue #129: no public surface may reintroduce the unverified
    'Senior AI Platform Engineer' claim, and the key identity anchors
    must carry the title-accurate Data Engineer positioning that
    shipped on the fix/p0-positioning-batch branch."""
    stale = "Senior AI Platform Engineer"

    public_paths = (
        INDEX_HTML,
        REPO_ROOT / "README.md",
        REPO_ROOT / "static" / "site.webmanifest",
        REPO_ROOT / "content" / "posts" / "repo-context-hooks-supply-chain.html",
        REPO_ROOT / "autoapply-ai.html",
        REPO_ROOT / "tailor-resume.html",
        REPO_ROOT / "jobscout.html",
        REPO_ROOT / "portfolio-risk.html",
        REPO_ROOT / "fintune.html",
        REPO_ROOT / "fraud-detection.html",
        REPO_ROOT / "config.js",
    )
    contents = {p: p.read_text(encoding="utf-8") for p in public_paths if p.exists()}
    for path, body in contents.items():
        assert stale not in body, (
            f"{path.relative_to(REPO_ROOT)} still contains the stale "
            f"'{stale}' identity claim"
        )

    index_html = contents[INDEX_HTML]
    for required in (
        '<meta property="og:title" content="Narendranath Edara | '
        'Data Engineer - AI-Enabled Data Platforms">',
        "<title>Narendranath Edara | Data Engineer - "
        "AI-Enabled Data Platforms</title>",
        # The header logo carried this anchor before the rewrite; the
        # hero role heading carries it now.
        '<h2 class="hero-role">Data Engineer',
    ):
        assert required in index_html, f"index.html missing identity anchor: {required!r}"

    readme = contents[REPO_ROOT / "README.md"]
    assert "I am a Data Engineer who builds reliable data platforms first" in readme

    manifest = contents[REPO_ROOT / "static" / "site.webmanifest"]
    assert "Data Engineer building AI-enabled data platforms" in manifest

    post = contents[REPO_ROOT / "content" / "posts" / "repo-context-hooks-supply-chain.html"]
    assert '"jobTitle": "Data Engineer"' in post, (
        "schema.org jobTitle must be the actual employment title, "
        "not a branding string"
    )



MAX_MECHANISM_WORDS = 8
MAX_SENTENCE_WORDS = 15
MAX_SENTENCES_PER_PARA = 2
# Visible prose classes. sr-only spans are stripped first: they are
# screen-reader provenance notes, deliberately long, and never scanned.
PROSE_CLASSES = ("proof-mechanism", "prior-close", "hero-line", "cta-line")


def _visible_paragraphs(html: str) -> list[tuple[str, str]]:
    body = re.sub(r'<span class="sr-only">.*?</span>', "", html, flags=re.S)
    out = []
    for cls in PROSE_CLASSES:
        for m in re.finditer(r'<p class="%s">(.*?)</p>' % cls, body, re.S):
            txt = re.sub(r"<[^>]+>", " ", m.group(1))
            txt = txt.replace("&middot;", " ").replace("&nbsp;", " ")
            out.append((cls, re.sub(r"\s+", " ", txt).strip()))
    return out


def _sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.!?]) ", text) if x.strip()]


def test_mechanism_lines_stay_scannable(html: str) -> None:
    """A phone reader gives each card about two seconds. The mechanism
    line is the last thing they read and the first thing they skip, so
    it has to land in one glance."""
    for cls, txt in _visible_paragraphs(html):
        if cls != "proof-mechanism":
            continue
        n = len(txt.split())
        assert n <= MAX_MECHANISM_WORDS, (
            f"mechanism line is {n} words (max {MAX_MECHANISM_WORDS}): {txt!r}"
        )


def test_visible_prose_is_short(html: str) -> None:
    """Read-aloud limits, enforced rather than trusted."""
    for cls, txt in _visible_paragraphs(html):
        sents = _sentences(txt)
        assert len(sents) <= MAX_SENTENCES_PER_PARA, (
            f".{cls} has {len(sents)} sentences (max {MAX_SENTENCES_PER_PARA}): {txt!r}"
        )
        for sent in sents:
            n = len(sent.split())
            assert n <= MAX_SENTENCE_WORDS, (
                f".{cls} sentence is {n} words (max {MAX_SENTENCE_WORDS}): {sent!r}"
            )


def test_projects_section_is_collapsed_by_default(html: str) -> None:
    """<details> with no `open` attribute keeps roughly 900px of repo
    detail off the phone scroll until someone asks for it. It must stay
    native: adding `open` or swapping in a JS toggle both regress."""
    m = re.search(r"<details[^>]*class=\"repo-details\"[^>]*>", html)
    assert m, "projects section must use <details class=\"repo-details\">"
    assert " open" not in m.group(0), (
        "projects <details> carries `open`; it must be collapsed by default"
    )
    assert "<summary>" in html, "projects <details> missing <summary>"


def test_toc_links_resolve_to_real_sections(html: str) -> None:
    nav = re.search(r'<nav class="toc"[^>]*>([\s\S]*?)</nav>', html)
    assert nav, "section jump menu (nav.toc) not found"
    targets = re.findall(r'href="#([^"]+)"', nav.group(1))
    assert targets == ["proof", "before", "projects", "contact"], (
        f"jump menu should link the four sections in order, found {targets}"
    )
    for t in targets:
        assert f'id="{t}"' in html, f"jump menu points at #{t} but no element has that id"


def test_exactly_one_call_to_action(html: str) -> None:
    """Everything else on the page is proof. One ask, one address, and
    the subject line is pre-filled so replying costs nothing."""
    ctas = re.findall(r'<a class="cta-btn"[^>]*href="([^"]+)"', html)
    assert len(ctas) == 1, f"expected exactly one call to action, found {len(ctas)}"
    href = ctas[0]
    assert href.startswith("mailto:"), "the call to action must be a mailto link"
    assert "subject=" in href, "the mailto link must pre-fill a subject"
    assert "%5BCompany%20Name%5D" in href, (
        "the subject should carry a [Company Name] placeholder for the sender to fill"
    )


# ------- Test runner -------
TESTS = [
    test_index_html_exists,
    # ----- GROUND_TRUTH.md gate, across every public page -----
    test_no_blocked_claims_on_any_public_page,
    # ----- home.css module (was styles.css before the rewrite) -----
    test_home_css_exists_and_index_links_it,
    test_home_css_has_impact_strip_module,
    test_home_css_uses_tabular_nums,
    test_home_css_has_print_block,
    test_home_css_mobile_breakpoint_at_600px,
    test_home_css_uses_warm_palette_tokens,
    # ----- Home page shape: keeps the page from growing back -----
    test_index_loads_no_javascript_bundle,
    test_index_has_expected_section_count,
    test_hero_has_exactly_four_links,
    test_hero_carries_no_extra_content,
    test_projects_section_lists_expected_repo_count,
    test_projects_section_is_collapsed_by_default,
    test_toc_links_resolve_to_real_sections,
    test_exactly_one_call_to_action,
    # ----- Phone scan budget: short copy, one ask -----
    test_mechanism_lines_stay_scannable,
    test_visible_prose_is_short,
    test_every_claim_number_has_a_baseline_or_unit,
    # ----- Impact-strip semantics -----
    test_strip_count_matches_expected,
    test_each_strip_uses_aria_labelledby,
    test_aria_labelledby_targets_exist,
    test_each_strip_has_3_to_5_stats,
    test_each_stat_has_value_and_label,
    test_no_scrapped_exponenthr_outcomes,
    test_no_scrapped_exponenthr_outcomes_in_rendered_text,
    test_no_inline_style_attribute_on_strips,
    test_jetbrains_mono_loaded,
    test_repo_context_hooks_card_present,
    test_all_ids_unique,
    # ----- Architecture & Write-Ups (issues #56 + #64) -----
    test_supply_chain_post_exists,
    test_supply_chain_post_has_required_sections,
    test_supply_chain_post_word_count_in_range,
    test_supply_chain_post_has_inline_svg_diagram,
    test_supply_chain_post_no_scrapped_outcomes,
    # ----- System diagrams (issue #58) -----
    # ----- Hover-preview primitive (issue #70) -----
    # ----- Substack live-feed mode (hover-preview v2 follow-up) -----
    # ----- Skills grid (issue #71) -----
    test_public_identity_surfaces_use_canonical_title,
    # ----- Link verification (issue #43) -----
    test_all_local_links_resolve,
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
