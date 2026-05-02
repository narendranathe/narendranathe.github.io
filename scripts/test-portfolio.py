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
APP_JS = REPO_ROOT / "app.js"
SUPPLY_CHAIN_POST = REPO_ROOT / "content" / "posts" / "repo-context-hooks-supply-chain.html"
HOVER_PREVIEW_PATTERN_DOC = REPO_ROOT / "docs" / "hover-preview-pattern.md"
RESUME_PREVIEW_PNG = REPO_ROOT / "static" / "resume-page1-preview.png"
GITHUB_PREVIEW_PNG = REPO_ROOT / "static" / "preview-github.png"
LINKEDIN_PREVIEW_PNG = REPO_ROOT / "static" / "preview-linkedin.png"
SUBSTACK_PREVIEW_PNG = REPO_ROOT / "static" / "preview-substack.png"
SKILLS_DIR = REPO_ROOT / "static" / "skills"
SKILLS_PATTERN_DOC = REPO_ROOT / "docs" / "skills-grid-pattern.md"

# #71 skills-grid budgets
SKILLS_EXPECTED_CATEGORIES = 6
SKILLS_MIN_ICONS_PER_CATEGORY = 4
SKILLS_MAX_ICONS_PER_CATEGORY = 6
SKILLS_MAX_ICON_BYTES = 6 * 1024
SKILLS_MAX_TOTAL_BYTES = 60 * 1024

# #70 hover-preview budget: 30 KB per asset matches #67's resume-preview budget.
HOVER_PREVIEW_BUDGET_BYTES = 30 * 1024
# Minimum trigger count: 4 resume + 6 LinkedIn (3 testimonials + peer-CTA + contact + footer)
# + 1 GitHub + 7 Substack (3 writing CTAs + hero CTA + peer-CTA + contact + footer) = 18.
# We use 14 as the floor to allow minor markup churn without test thrash.
HOVER_PREVIEW_MIN_TRIGGERS = 14
HOVER_PREVIEW_MIN_RESUME_TRIGGERS = 4
HOVER_PREVIEW_MIN_LINKEDIN_TRIGGERS = 5
HOVER_PREVIEW_MIN_SUBSTACK_TRIGGERS = 5

REQUIRED_POST_SECTIONS = ("problem", "constraints", "design", "tradeoffs", "outcome")
POST_MIN_WORDS = 1500
POST_MAX_WORDS = 2500

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


def test_hero_uses_local_photo_not_external_cdn(html: str) -> None:
    """Hero photo (issue #69): the <aside class="hero-visual"> primary
    portrait MUST be served from static/originals/ — never an external
    raw.githubusercontent.com or github.com/user-attachments URL.
    Regression guard against re-introducing CDN dependencies that
    cost LCP and add cross-origin DNS lookups. Scoped to the hero
    <aside> block only — other sections (e.g. Contact) may continue
    to use their own image sources."""
    start = html.find('<aside class="hero-visual"')
    assert start != -1, "hero-visual <aside> block not found in index.html"
    end = html.find("</aside>", start)
    assert end != -1, "hero-visual <aside> block not closed"
    hero_block = html[start:end]
    assert "static/originals/headshot-fullbody.jpg" in hero_block, (
        "hero <img> must reference static/originals/headshot-fullbody.jpg"
    )
    forbidden = (
        "raw.githubusercontent.com",
        "github.com/user-attachments/",
    )
    for url_fragment in forbidden:
        assert url_fragment not in hero_block, (
            f"hero must not reference external CDN photo {url_fragment!r}; "
            "use local static/originals/ asset instead."
        )


def test_hero_aside_no_data_reveal(html: str) -> None:
    """Issue #77: the <aside class="hero-visual"> MUST NOT carry a
    data-reveal attribute. data-reveal sets opacity:0 + 0.55s fade
    via styles.css [data-reveal] rules — Chrome's LCP algorithm
    excludes opacity:0 elements as candidates, so wrapping the hero
    img in data-reveal silently disqualifies it from being the LCP
    element. The post-merge Lighthouse audit (2026-05-01T16:05Z)
    measured Mobile LCP at 2854ms because of this exact bug.

    Removing this regression guard (or re-adding data-reveal to the
    hero aside) would re-introduce the LCP regression with no other
    CI signal."""
    m = re.search(r'<aside\s+class="hero-visual"[^>]*>', html)
    assert m, "hero-visual <aside> not found in index.html"
    aside_open = m.group(0)
    assert "data-reveal" not in aside_open, (
        f"hero-visual <aside> carries data-reveal — this disqualifies the "
        f"hero img from being Chrome's LCP candidate (opacity:0 fence). "
        f"See PR #81 / issue #77. Aside tag: {aside_open}"
    )


def test_hero_picture_has_mobile_variant(html: str) -> None:
    """Hero photo (issue #79): the hero <img> must be wrapped in a
    <picture> with a mobile <source> pointing at the 800px variant.
    The 800px file must exist on disk and be smaller than the 1200px
    source — otherwise the variant is pointless."""
    start = html.find('<aside class="hero-visual"')
    assert start != -1, "hero-visual <aside> block not found"
    end = html.find("</aside>", start)
    hero_block = html[start:end]

    assert "<picture>" in hero_block, (
        "hero <img> must be wrapped in <picture> for the mobile variant (#79)"
    )
    assert 'media="(max-width: 860px)"' in hero_block, (
        "hero <picture> must include <source media=\"(max-width: 860px)\"> "
        "to match the actual hero stacking breakpoint at styles.css:307. "
        "(Earlier 780px was a mismatch — see test_hero_picture_breakpoint_matches_layout)"
    )
    assert "headshot-fullbody-800.jpg" in hero_block, (
        "hero <picture> must reference the 800px mobile variant"
    )

    src_path = REPO_ROOT / "static" / "originals" / "headshot-fullbody.jpg"
    mobile_path = REPO_ROOT / "static" / "originals" / "headshot-fullbody-800.jpg"
    assert mobile_path.exists(), (
        f"mobile hero variant missing on disk: {mobile_path}. "
        "Run: python scripts/snap-hero-variants.py"
    )
    src_bytes = src_path.stat().st_size
    mobile_bytes = mobile_path.stat().st_size
    assert mobile_bytes < src_bytes, (
        f"mobile variant ({mobile_bytes}B) must be smaller than source ({src_bytes}B); "
        "regenerate via snap-hero-variants.py with lower JPEG quality"
    )
    # Hard cap: 50 KB. Soft target was 30 KB; allow headroom for future
    # quality bumps but fail if someone regenerates at quality 95+.
    assert mobile_bytes <= 50 * 1024, (
        f"mobile variant {mobile_bytes}B exceeds 50 KB cap; "
        "regenerate via snap-hero-variants.py at lower JPEG quality"
    )


def test_hero_preload_uses_imagesrcset(html: str) -> None:
    """Hero photo (issue #79): the <link rel="preload" as="image"> for
    the hero must include imagesrcset + imagesizes mirroring the
    <picture> in the hero. Without this, the preload scanner always
    fetches the 1200px desktop variant, defeating the mobile variant
    on Slow 4G."""
    head_end = html.find("</head>")
    assert head_end != -1
    head = html[:head_end]
    preload_match = re.search(
        r'<link[^>]+rel="preload"[^>]+as="image"[^>]+>',
        head,
        flags=re.S,
    )
    assert preload_match, "hero preload <link rel=\"preload\" as=\"image\"> not found"
    preload = preload_match.group(0)
    assert "imagesrcset" in preload, (
        "hero preload must include imagesrcset so mobile preloads the 800px variant"
    )
    assert "imagesizes" in preload, (
        "hero preload must include imagesizes for the preload scanner to pick the right variant"
    )
    assert "headshot-fullbody-800.jpg" in preload, (
        "hero preload imagesrcset must include the 800px variant"
    )


def test_hero_picture_has_avif_and_webp_variants(html: str) -> None:
    """Hero photo (issue #83): the <picture> must include AVIF and WebP
    <source> rows BEFORE the JPEG fallback, with a mobile + desktop
    pair for each. AVIF lands first because it has the smallest bytes;
    WebP second; JPEG last as the universal fallback.

    All 4 new variant files (avif/webp x desktop/mobile) must exist on
    disk and be smaller than the source JPEG."""
    start = html.find('<aside class="hero-visual"')
    assert start != -1, "hero-visual <aside> not found"
    end = html.find("</aside>", start)
    hero = html[start:end]

    # Source order matters: AVIF before WebP before JPEG.
    avif_idx = hero.find('type="image/avif"')
    webp_idx = hero.find('type="image/webp"')
    assert avif_idx != -1, "<picture> missing AVIF <source> (issue #83)"
    assert webp_idx != -1, "<picture> missing WebP <source> (issue #83)"
    assert avif_idx < webp_idx, (
        "AVIF <source> must come BEFORE WebP <source> in the <picture>; "
        "browsers pick the first format they support"
    )

    # Both formats need a mobile pair (max-width: 860px) + desktop pair.
    for fmt, sigil in (("AVIF", "avif"), ("WebP", "webp")):
        mobile = re.search(
            rf'<source\s+type="image/{sigil}"\s+media="\(max-width:\s*860px\)"\s+srcset="[^"]*-800\.{sigil}"',
            hero,
        )
        desktop = re.search(
            rf'<source\s+type="image/{sigil}"\s+srcset="[^"]*headshot-fullbody\.{sigil}"',
            hero,
        )
        assert mobile, f"<picture> missing {fmt} mobile <source> with media=(max-width: 860px)"
        assert desktop, f"<picture> missing {fmt} desktop <source>"

    # Files exist + smaller than source JPEG.
    src = REPO_ROOT / "static" / "originals" / "headshot-fullbody.jpg"
    src_bytes = src.stat().st_size
    for stem in ("headshot-fullbody", "headshot-fullbody-800"):
        for ext in ("avif", "webp"):
            p = REPO_ROOT / "static" / "originals" / f"{stem}.{ext}"
            assert p.exists(), (
                f"missing variant on disk: {p}. "
                "Run: pip install pillow-avif-plugin && python scripts/snap-hero-variants.py"
            )
            assert p.stat().st_size < src_bytes, (
                f"{p.name} ({p.stat().st_size}B) should be smaller than source "
                f"JPEG ({src_bytes}B); regenerate via snap-hero-variants.py at "
                f"the documented quality settings"
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


def test_data_reveal_reduced_motion_fallback() -> None:
    """Issue #86: under prefers-reduced-motion, [data-reveal] elements
    must override the initial opacity:0 + translateY state so content
    is visible even when JavaScript / IntersectionObserver hasn't run
    (reduced-motion users with JS disabled were seeing blank space
    below the fold). Check both opacity:1 and transform:none are
    declared inside the reduced-motion media block for [data-reveal]."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    # Find the prefers-reduced-motion block(s) and look for the
    # [data-reveal] override inside one of them.
    blocks = re.findall(
        r"@media\s*\(\s*prefers-reduced-motion:\s*reduce\s*\)\s*\{(.+?)\n\}",
        css,
        flags=re.S,
    )
    found = False
    for block in blocks:
        m = re.search(
            r"\[data-reveal\][^{]*\{[^}]*opacity\s*:\s*1[^}]*transform\s*:\s*none",
            block,
            flags=re.S,
        )
        if m:
            found = True
            break
    assert found, (
        "missing [data-reveal] reduced-motion override in styles.css. "
        "Without `opacity: 1 !important; transform: none !important;` inside "
        "the @media (prefers-reduced-motion: reduce) block, users with reduced "
        "motion AND JS disabled see blank space below the fold (the initial "
        "opacity:0 + translateY state never gets undone). See issue #86."
    )


def test_css_mobile_breakpoint_at_600px() -> None:
    """Guard the desktop breakpoint that switches impact-strip values
    from wrap-allowed (mobile, WCAG 1.4.10 reflow at 320px) to single-
    line (>=600px). Targets .impact-value specifically — earlier
    iterations applied nowrap to the whole .impact-stat which caused
    long labels (e.g. "CAREER PAGES MONITORED") to overflow the grid
    column."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    has_breakpoint = re.search(
        r"@media\s*\(\s*min-width:\s*600px\s*\)\s*\{[^}]*\.impact-value[^}]*white-space\s*:\s*nowrap",
        css,
        flags=re.S,
    )
    assert has_breakpoint, (
        "CSS missing @media (min-width: 600px) rule applying "
        "white-space: nowrap to .impact-value — needed so multi-digit "
        "values stay single-line on desktop while labels remain free "
        "to wrap (otherwise labels overflow the grid column)."
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


def test_index_links_to_supply_chain_post(html: str) -> None:
    assert "content/posts/repo-context-hooks-supply-chain.html" in html, (
        "index.html missing link to the supply-chain write-up; "
        "Architecture & Write-Ups section should link the post."
    )


def test_index_has_architecture_section(html: str) -> None:
    assert 'id="architecture"' in html, (
        "index.html missing the Architecture & Write-Ups section "
        "(issue #56 acceptance criteria)."
    )


# ----- System diagrams (issue #58) -----
SYSTEM_DIAGRAM_RE = re.compile(
    r'<svg[^>]*class="system-diagram"[^>]*>.*?</svg>', re.S
)
# Per-page inline-SVG byte budget across all .system-diagram elements.
# Hand-authored diagrams in this repo run 3-5 KB each; the gate keeps
# regressions (e.g., an Excalidraw export sneaking in) loud.
SYSTEM_DIAGRAM_PAGE_BUDGET_BYTES = 30 * 1024  # 30 KB


def test_index_has_two_system_diagrams(html: str) -> None:
    """Issue #58: D1 (AutoApply AI) + D2 (Portfolio-Risk) inline SVGs.

    Both diagrams live in the home index.html (D1 inside the AutoApply
    arch-expand, D2 inside the Portfolio Risk Analytics ml-project-entry).
    There is no separate content/posts/<slug>.html for either project,
    so the home page is the single target location for both diagrams."""
    diagrams = SYSTEM_DIAGRAM_RE.findall(html)
    assert len(diagrams) >= 2, (
        f"index.html must contain at least 2 inline <svg class=\"system-diagram\"> "
        f"elements (D1 AutoApply AI + D2 Portfolio-Risk per issue #58); "
        f"found {len(diagrams)}."
    )
    # Sanity-check both diagrams reference the right diagram IDs.
    body = "\n".join(diagrams)
    assert "diagram-d1-autoapply" in body, (
        "D1 AutoApply AI diagram missing (expected id namespace 'diagram-d1-autoapply-*')."
    )
    assert "diagram-d2-portfolio-risk" in body, (
        "D2 Portfolio-Risk diagram missing (expected id namespace 'diagram-d2-portfolio-risk-*')."
    )


def test_each_system_diagram_has_title_and_desc(html: str) -> None:
    """WCAG 1.1.1: every <svg role='img'> needs a programmatic accessible
    name + description. Pattern enshrined in docs/system-diagram-pattern.md."""
    diagrams = SYSTEM_DIAGRAM_RE.findall(html)
    for i, svg in enumerate(diagrams):
        assert "<title" in svg, (
            f"system-diagram #{i + 1} missing <title> (WCAG 1.1.1)."
        )
        assert "<desc" in svg, (
            f"system-diagram #{i + 1} missing <desc> (WCAG 1.1.1)."
        )
        assert 'role="img"' in svg, (
            f"system-diagram #{i + 1} missing role=\"img\" on the <svg> element."
        )


def test_each_system_diagram_uses_currentcolor(html: str) -> None:
    """No hardcoded #hex on fill / stroke. Diagrams must inherit color
    via currentColor or CSS custom-property var() so dark-mode + print
    + forced-colors all render correctly with one markup."""
    diagrams = SYSTEM_DIAGRAM_RE.findall(html)
    # Pattern: any fill="#xxx" or stroke="#xxx" attribute in the diagram
    # body that isn't legitimate (currentColor, var(--...), none).
    HEX_ATTR_RE = re.compile(r'(?:fill|stroke)="#[0-9a-fA-F]{3,8}"')
    for i, svg in enumerate(diagrams):
        hits = HEX_ATTR_RE.findall(svg)
        assert not hits, (
            f"system-diagram #{i + 1} hardcodes color attributes "
            f"({hits}); use currentColor or var(--accent-warm) so dark/print/HCM work."
        )


def test_index_inline_system_diagram_byte_budget(html: str) -> None:
    """Per-page inline-SVG byte budget (system-diagrams only) <= 30 KB.
    Loud regression gate against Excalidraw exports / verbose hand-edits."""
    diagrams = SYSTEM_DIAGRAM_RE.findall(html)
    total_bytes = sum(len(d.encode("utf-8")) for d in diagrams)
    assert total_bytes <= SYSTEM_DIAGRAM_PAGE_BUDGET_BYTES, (
        f"Inline system-diagram payload on index.html is {total_bytes} bytes; "
        f"budget is {SYSTEM_DIAGRAM_PAGE_BUDGET_BYTES} bytes "
        f"(issue #58 hand-rolled inline SVG contract)."
    )


# ----- Hover-preview primitive (issue #70) -----
def test_hover_preview_css_module_present() -> None:
    """styles.css must contain the .hover-preview module (selector + popover-open
    state). Catches accidental deletion of the CSS block during refactors."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    assert ".hover-preview {" in css, ".hover-preview block missing from styles.css"
    assert ".hover-preview:popover-open" in css, ".hover-preview:popover-open state missing"
    assert "(hover: none) and (pointer: coarse)" in css, "touch-device hide rule missing"
    assert "prefers-reduced-motion" in css, "reduced-motion block missing"


def test_hover_preview_js_module_present() -> None:
    """app.js must contain the hover-preview IIFE — vanilla DOM, no deps."""
    js = APP_JS.read_text(encoding="utf-8")
    assert "data-hover-preview" in js, "hover-preview JS does not query data-hover-preview triggers"
    assert "showPopover" in js, "hover-preview JS does not call native Popover API"
    assert "(hover: none) and (pointer: coarse)" in js, "hover-preview JS does not skip touch devices"


def test_hover_preview_resume_triggers_count(html: str) -> None:
    """At least 4 resume link sites in index.html annotated with the resume preview
    (header desktop, mobile menu, hero CTA, contact section per #70 AC)."""
    pattern = re.compile(
        r'data-hover-preview="/static/resume-page1-preview\.png(?:\?v=[a-f0-9]{8})?"',
        re.IGNORECASE,
    )
    matches = pattern.findall(html)
    assert len(matches) >= HOVER_PREVIEW_MIN_RESUME_TRIGGERS, (
        f"Found {len(matches)} resume hover-preview triggers; expected >= "
        f"{HOVER_PREVIEW_MIN_RESUME_TRIGGERS} (header, mobile, hero, contact)."
    )


def test_hover_preview_contact_icons_annotated(html: str) -> None:
    """GitHub + LinkedIn contact icons must carry data-hover-preview pointing at
    static/preview-github.png and static/preview-linkedin.png respectively."""
    assert 'data-hover-preview="/static/preview-github.png"' in html, (
        "GitHub contact icon missing data-hover-preview annotation"
    )
    assert 'data-hover-preview="/static/preview-linkedin.png"' in html, (
        "LinkedIn contact icon missing data-hover-preview annotation"
    )


def test_hover_preview_total_triggers_count(html: str) -> None:
    """Total data-hover-preview attribute count meets the #70 minimum
    (4 resume + 2 contact = 6)."""
    n = len(re.findall(r"data-hover-preview=", html))
    assert n >= HOVER_PREVIEW_MIN_TRIGGERS, (
        f"Found {n} hover-preview triggers; expected >= {HOVER_PREVIEW_MIN_TRIGGERS}."
    )


def test_hover_preview_assets_committed() -> None:
    """All four preview PNGs (resume + github + linkedin + substack) committed
    and within the 30 KB per-asset budget."""
    for path in (RESUME_PREVIEW_PNG, GITHUB_PREVIEW_PNG, LINKEDIN_PREVIEW_PNG, SUBSTACK_PREVIEW_PNG):
        assert path.exists(), f"missing committed preview asset: {path.relative_to(REPO_ROOT)}"
        size = path.stat().st_size
        assert size <= HOVER_PREVIEW_BUDGET_BYTES, (
            f"{path.name} is {size} B; exceeds {HOVER_PREVIEW_BUDGET_BYTES} B per-asset budget."
        )
        # PNG magic bytes
        assert path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a valid PNG"


def test_hover_preview_every_linkedin_link_annotated(html: str) -> None:
    """Every <a> pointing at linkedin.com must carry data-hover-preview.
    Consistency over coverage: the user-facing complaint about #70 v1 was
    'LinkedIn implementation isn't on every instance.' Lock this invariant."""
    # Match each opening anchor tag containing a linkedin.com URL
    anchor_re = re.compile(
        r'<a\s[^>]*href="[^"]*linkedin\.com[^"]*"[^>]*>',
        re.IGNORECASE | re.DOTALL,
    )
    bad = [a for a in anchor_re.findall(html) if "data-hover-preview" not in a]
    assert not bad, (
        f"{len(bad)} LinkedIn anchor(s) missing data-hover-preview annotation:\n  "
        + "\n  ".join(a[:140] + ("..." if len(a) > 140 else "") for a in bad)
    )


def test_hover_preview_every_substack_link_annotated(html: str) -> None:
    """Every <a> pointing at narendranathe.substack.com must carry
    data-hover-preview. Same consistency rule as LinkedIn."""
    anchor_re = re.compile(
        r'<a\s[^>]*href="[^"]*substack\.com[^"]*"[^>]*>',
        re.IGNORECASE | re.DOTALL,
    )
    bad = [a for a in anchor_re.findall(html) if "data-hover-preview" not in a]
    assert not bad, (
        f"{len(bad)} Substack anchor(s) missing data-hover-preview annotation:\n  "
        + "\n  ".join(a[:140] + ("..." if len(a) > 140 else "") for a in bad)
    )


def test_hover_preview_linkedin_trigger_count(html: str) -> None:
    """At least 5 LinkedIn hover-preview triggers — covers Naren's own profile
    (peer CTA + contact + footer) plus 3 testimonial author profiles."""
    n = len(re.findall(r'data-hover-preview="/static/preview-linkedin\.png"', html))
    assert n >= HOVER_PREVIEW_MIN_LINKEDIN_TRIGGERS, (
        f"LinkedIn hover-preview triggers: {n} < expected {HOVER_PREVIEW_MIN_LINKEDIN_TRIGGERS}."
    )


def test_hover_preview_substack_trigger_count(html: str) -> None:
    """At least 5 Substack hover-preview triggers — covers writing CTAs +
    hero follow CTA + peer CTA + contact + footer."""
    n = len(re.findall(r'data-hover-preview="/static/preview-substack\.png"', html))
    assert n >= HOVER_PREVIEW_MIN_SUBSTACK_TRIGGERS, (
        f"Substack hover-preview triggers: {n} < expected {HOVER_PREVIEW_MIN_SUBSTACK_TRIGGERS}."
    )


def test_hover_preview_resume_cache_bust_matches_sidecar(html: str) -> None:
    """Every `?v=<hash>` in resume `data-hover-preview` URLs must match the live
    `.well-known/resume.json` `preview_hash`. Catches the silent-failure class
    where snap-resume.py regenerates the PNG, sidecar bumps the hash, but the
    hover-preview markup is left stale → users see browser-cached old preview."""
    import json
    sidecar = json.loads((REPO_ROOT / ".well-known" / "resume.json").read_text(encoding="utf-8"))
    expected = sidecar.get("preview_hash")
    if not expected:
        return  # sidecar has no preview yet — handled by #67's own assertions.
    pattern = re.compile(
        r'data-hover-preview="/static/resume-page1-preview\.png\?v=([a-f0-9]{8})"',
        re.IGNORECASE,
    )
    found = pattern.findall(html)
    assert found, "no resume-preview triggers carry a ?v=<hash> cache-bust suffix"
    drifted = [h for h in found if h != expected]
    assert not drifted, (
        f"resume-preview cache-bust hash drift: markup has {drifted!r} but "
        f"sidecar preview_hash is {expected!r}. Run `python scripts/snap-resume.py` "
        f"and update the data-hover-preview attributes."
    )


def test_hover_preview_companion_attrs_present(html: str) -> None:
    """Every element with `data-hover-preview` must also carry non-empty
    `data-hover-title` AND `data-hover-caption`. These are the SR-visible
    contract for the popover content; missing them silently breaks UX."""
    # Crude but stdlib-only: extract each opening tag containing data-hover-preview
    # and check for the companion attrs in the same tag substring.
    tag_re = re.compile(r"<[^>]*data-hover-preview=[^>]*>", re.IGNORECASE)
    bad: list[str] = []
    for tag in tag_re.findall(html):
        if not re.search(r'data-hover-title="[^"]+"', tag):
            bad.append("missing data-hover-title in: " + tag[:120])
        if not re.search(r'data-hover-caption="[^"]+"', tag):
            bad.append("missing data-hover-caption in: " + tag[:120])
    assert not bad, "hover-preview companion-attribute drift:\n  " + "\n  ".join(bad)


def test_hover_preview_no_role_dialog(html: str) -> None:
    """Deliberate a11y choice: the hover-preview is decorative for sighted users
    only — neither trigger nor card carries `role="dialog"` / `aria-haspopup`.
    Promising assistive tech a "dialog" then rendering a read-only card-with-image
    is a worse SR experience than no announcement. Lock this invariant so a
    well-meaning future PR doesn't quietly add it back."""
    # Look for either attribute appearing within ~200 chars of a data-hover-preview
    # occurrence (the trigger element). Scope the check to avoid false positives
    # from unrelated dialogs elsewhere on the page.
    for m in re.finditer(r"data-hover-preview=", html):
        nearby = html[max(0, m.start() - 200):m.end() + 200]
        assert 'role="dialog"' not in nearby, (
            "hover-preview trigger or container near a `role=\"dialog\"` — "
            "the pattern intentionally omits this; re-adding it is a regression "
            "(see docs/hover-preview-pattern.md ARIA decisions)."
        )
        assert "aria-haspopup" not in nearby, (
            "hover-preview trigger has `aria-haspopup` — the pattern intentionally "
            "omits this (see docs/hover-preview-pattern.md ARIA decisions)."
        )


def test_hover_preview_pattern_doc_present() -> None:
    """docs/hover-preview-pattern.md exists and is non-trivial — drop-in
    documentation is part of the #70 deliverable."""
    assert HOVER_PREVIEW_PATTERN_DOC.exists(), (
        "docs/hover-preview-pattern.md missing — pattern doc is part of #70 deliverable"
    )
    body = HOVER_PREVIEW_PATTERN_DOC.read_text(encoding="utf-8")
    assert len(body) > 1000, f"pattern doc body is only {len(body)} chars; expected >= 1000"


# ===== Substack live-feed mode (hover-preview v2 follow-up) =====

SUBSTACK_SNAPSHOT_JSON = REPO_ROOT / "static" / "substack-latest.json"
SUBSTACK_SNAP_SCRIPT = REPO_ROOT / "scripts" / "snap-substack-feed.py"
SUBSTACK_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "substack-snapshot.yml"


def test_substack_snapshot_pipeline_present() -> None:
    """The Substack live-feed render mode depends on three artifacts
    being shipped together: the parser script, the cron workflow, and
    a same-origin JSON snapshot. Removing any one breaks the popup."""
    assert SUBSTACK_SNAP_SCRIPT.exists(), (
        "scripts/snap-substack-feed.py missing — needed by the cron workflow"
    )
    assert SUBSTACK_WORKFLOW.exists(), (
        ".github/workflows/substack-snapshot.yml missing — without this the "
        "JSON snapshot never refreshes after the seed commit"
    )
    assert SUBSTACK_SNAPSHOT_JSON.exists(), (
        "static/substack-latest.json missing — the popup will 404 on hover. "
        "Run: python scripts/snap-substack-feed.py"
    )


def test_substack_snapshot_json_schema() -> None:
    """The JSON shape is the contract between the parser + the popup
    renderer. Any change here MUST update both buildFeedDom() in app.js
    AND the parser; this test catches drift."""
    import json
    body = SUBSTACK_SNAPSHOT_JSON.read_text(encoding="utf-8")
    data = json.loads(body)
    for key in ("publication", "url", "fetched_at", "posts"):
        assert key in data, f"substack-latest.json missing required field: {key}"
    assert isinstance(data["posts"], list), "posts must be a list"
    # Parser keeps up to 10 posts so the per-trigger pin lookup can
    # resolve older posts that aren't in the absolute top 3 anymore.
    # The popup itself only shows max 3 at a time.
    assert 0 <= len(data["posts"]) <= 10, (
        f"posts length {len(data['posts'])} unexpected; parser caps at 10"
    )
    if data["posts"]:
        post = data["posts"][0]
        for key in ("title", "url", "published_at", "excerpt"):
            assert key in post, f"post entry missing field: {key}"
        assert post["url"].startswith("http"), "post.url must be an absolute URL"


def test_substack_triggers_have_embed_attrs(html: str) -> None:
    """Every <a> link to narendranathe.substack.com that uses the
    hover-preview MUST also declare data-hover-embed=\"substack-feed\"
    and data-hover-feed=\"/static/substack-latest.json\". Without these,
    the live-feed render mode falls back to the static screenshot."""
    # Find every Substack-targeted anchor that has data-hover-preview
    pattern = re.compile(
        r'<a\s+href="https://[^"]*substack\.com[^"]*"[^>]*data-hover-preview',
        flags=re.S,
    )
    anchors = pattern.findall(html)
    assert anchors, "no Substack hover-preview triggers found"
    # Each one of those anchor opening tags must include the embed attrs.
    # Use a wider re.search per occurrence.
    embed_count = len(re.findall(
        r'<a\s+href="https://[^"]*substack\.com[^>]*?data-hover-embed="substack-feed"',
        html,
        flags=re.S,
    ))
    assert embed_count == len(anchors), (
        f"{len(anchors)} Substack hover triggers found, but only {embed_count} "
        f"declare data-hover-embed=\"substack-feed\". Each Substack trigger "
        f"must opt in to the live-feed render mode."
    )


def test_app_js_has_substack_render_branch() -> None:
    """app.js must implement the renderSubstack branch, the per-trigger
    pin selector, and the scroll-aware repositioning listener; without
    any one of them, the live-feed mode is half-built."""
    js = APP_JS.read_text(encoding="utf-8")
    assert "renderSubstack" in js, (
        "app.js missing renderSubstack() — live-feed render branch absent"
    )
    assert "buildFeedDom" in js, (
        "app.js missing buildFeedDom() — feed list construction absent"
    )
    assert "selectPostsForTrigger" in js, (
        "app.js missing selectPostsForTrigger() — per-trigger pin lookup "
        "(href -> matching post first, then 2 most recent) absent"
    )
    assert "data-hover-embed" in js, (
        "app.js never reads data-hover-embed attribute — render branch dead code"
    )
    # Scroll-aware reposition listener: scroll OR resize handler that
    # re-runs position(lastTrigger). Substring-match is canary-level
    # but catches a regression where someone removes the listener.
    assert "onScrollOrResize" in js or "scroll" in js.lower(), (
        "app.js missing scroll listener that re-positions the popover"
    )


def test_styles_css_has_feed_list_module() -> None:
    """The .hp-feed-* CSS module renders the live-posts list in the
    smaller card. Removing it would leave the JS-built DOM unstyled."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    for selector in (".hp-feed-header", ".hp-feed-list", ".hp-feed-item",
                     ".hp-feed-title", ".hp-feed-meta", ".hp-feed-empty"):
        assert selector in css, f"styles.css missing {selector} rule"


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


def test_skills_section_present(html: str) -> None:
    """Issue #71: <section id="skills"> exists between Track Record and
    What Shipped, has the expected section heading + subtitle."""
    block = _skills_section_html(html)
    assert 'class="section-label">Stack<' in block, (
        "skills section missing 'Stack' section-label"
    )
    assert "Stack I work in daily" in block, (
        "skills section missing 'Stack I work in daily' h2 title"
    )
    # Section ordering: skills must come AFTER experience and BEFORE proof
    pos_experience = html.find('id="experience"')
    pos_skills = html.find('id="skills"')
    pos_proof = html.find('id="proof"')
    assert -1 < pos_experience < pos_skills < pos_proof, (
        f"section order broken: experience={pos_experience} "
        f"skills={pos_skills} proof={pos_proof} (expected ascending)"
    )


def test_skills_nav_link_present(html: str) -> None:
    """Issue #71: nav must include a 'Stack' link pointing to #skills,
    in BOTH the desktop nav and the mobile nav drawer."""
    assert html.count('href="#skills"') >= 2, (
        "expected at least 2 nav links to #skills (desktop + mobile drawer)"
    )
    desktop_nav = re.search(
        r'<a href="#skills"\s+class="nav-link">Stack</a>', html
    )
    mobile_nav = re.search(
        r'<a href="#skills"\s+class="mobile-link">Stack</a>', html
    )
    assert desktop_nav, "desktop nav missing 'Stack' link"
    assert mobile_nav, "mobile nav drawer missing 'Stack' link"


def test_skills_has_expected_category_count(html: str) -> None:
    """Issue #71: exactly 5 .skills-category subgroups, each with a
    .skills-category-title heading."""
    block = _skills_section_html(html)
    cats = re.findall(r'<div class="skills-category">', block)
    assert len(cats) == SKILLS_EXPECTED_CATEGORIES, (
        f"expected {SKILLS_EXPECTED_CATEGORIES} .skills-category subgroups, "
        f"found {len(cats)}"
    )
    titles = re.findall(
        r'<h3 class="skills-category-title">([^<]+)</h3>', block
    )
    assert len(titles) == SKILLS_EXPECTED_CATEGORIES, (
        f"expected {SKILLS_EXPECTED_CATEGORIES} category titles, found {len(titles)}"
    )


def test_skills_each_category_has_valid_icon_count(html: str) -> None:
    """Issue #71: each category has 4-6 .skill-icon tiles (the spec's
    band — fewer than 4 reads as filler, more than 6 crowds the row)."""
    block = _skills_section_html(html)
    parts = re.split(r'<div class="skills-category">', block)[1:]
    for i, part in enumerate(parts, start=1):
        end = part.find("</div>\n          </div>")
        section = part[:end] if end != -1 else part
        icon_count = section.count('class="skill-icon"')
        assert SKILLS_MIN_ICONS_PER_CATEGORY <= icon_count <= SKILLS_MAX_ICONS_PER_CATEGORY, (
            f"skills-category #{i} has {icon_count} skill-icon tiles; "
            f"expected {SKILLS_MIN_ICONS_PER_CATEGORY}-{SKILLS_MAX_ICONS_PER_CATEGORY}"
        )


def test_skills_every_icon_is_keyboard_focusable(html: str) -> None:
    """Issue #71: every .skill-icon tile must be keyboard-focusable so
    users without a pointer can read the tooltip context. Implementation
    is `<span tabindex="0">` (per a11y review: <button> would imply
    activation that doesn't happen; a <div role="button"> would have the
    same issue. <span tabindex="0"> + visible text + aria-describedby
    is the WAI-ARIA APG canonical pattern for non-actionable focusable
    tooltip triggers)."""
    block = _skills_section_html(html)
    tiles = re.findall(r'<span[^>]+class="skill-icon"[^>]*>', block)
    assert tiles, "no .skill-icon tiles found in skills section"
    missing = [t for t in tiles if 'tabindex="0"' not in t]
    assert not missing, (
        f"{len(missing)} .skill-icon tiles missing tabindex=\"0\": {missing[:3]}"
    )


def test_skills_every_icon_has_visible_name(html: str) -> None:
    """Issue #71: every tile has a visible <span class="skill-name">
    sibling so the accessible name is not duplicated via aria-label
    (which would override the visible text and create a maintenance
    fork between visible and announced content)."""
    block = _skills_section_html(html)
    tiles = re.findall(
        r'<span[^>]+class="skill-icon"[^>]*>(.+?)</span></li>',
        block,
        flags=re.DOTALL,
    )
    assert tiles, "no .skill-icon tile bodies found"
    missing = [t for t in tiles if 'class="skill-name"' not in t]
    assert not missing, (
        f"{len(missing)} .skill-icon tiles missing visible <span class=\"skill-name\">"
    )
    # Confirm aria-label is NOT used (would shadow the visible name)
    has_aria_label = re.search(r'<span[^>]+class="skill-icon"[^>]+aria-label=', block)
    assert not has_aria_label, (
        "skill-icon tiles must not use aria-label (visible .skill-name is "
        "the accessible name; aria-label would override and fork content)"
    )


def test_skills_every_icon_has_tooltip(html: str) -> None:
    """Issue #71: every .skill-icon has aria-describedby pointing to a
    role="tooltip" span. The describedby ID must resolve."""
    block = _skills_section_html(html)
    tiles = re.findall(r'<span[^>]+class="skill-icon"[^>]*>', block)
    described_ids: list[str] = []
    for t in tiles:
        m = re.search(r'aria-describedby="([^"]+)"', t)
        assert m, f".skill-icon tile missing aria-describedby: {t}"
        described_ids.append(m.group(1))
    tooltip_ids = set(re.findall(
        r'<span id="([^"]+)" role="tooltip" class="skill-tooltip">', block
    ))
    missing = [i for i in described_ids if i not in tooltip_ids]
    assert not missing, (
        f"aria-describedby IDs missing matching tooltip span: {missing[:3]}"
    )


def test_skills_no_external_cdn_refs(html: str) -> None:
    """Issue #71: skills section must NOT reference any external CDN for
    icon assets (no jsdelivr, no unpkg, no Font Awesome, no devicons.dev
    runtime). Local static/skills/ only."""
    block = _skills_section_html(html)
    forbidden = (
        "cdn.jsdelivr.net",
        "unpkg.com",
        "fontawesome",
        "devicons.dev",
        "raw.githubusercontent.com",
    )
    for token in forbidden:
        assert token not in block.lower(), (
            f"skills section references external CDN token {token!r}; "
            "icons must be local static/skills/*.svg only"
        )


def test_skills_icon_files_present(html: str) -> None:
    """Every <img src="static/skills/<slug>.svg"> referenced in the
    skills section must exist on disk at the expected path."""
    block = _skills_section_html(html)
    refs = re.findall(r'src="(static/skills/[^"]+)"', block)
    assert refs, "no static/skills/*.svg references found in skills section"
    missing = [r for r in refs if not (REPO_ROOT / r).exists()]
    assert not missing, f"missing skill SVGs on disk: {missing}"


def test_skills_icon_byte_budgets() -> None:
    """Issue #71: each skill SVG <= 5 KB; total <= 60 KB (page-weight
    delta cap)."""
    assert SKILLS_DIR.exists(), f"static/skills/ directory missing: {SKILLS_DIR}"
    svg_files = sorted(SKILLS_DIR.glob("*.svg"))
    assert svg_files, "static/skills/ contains no .svg files"
    total = 0
    overweight: list[tuple[str, int]] = []
    for f in svg_files:
        size = f.stat().st_size
        total += size
        if size > SKILLS_MAX_ICON_BYTES:
            overweight.append((f.name, size))
    assert not overweight, (
        f"skill SVGs exceed {SKILLS_MAX_ICON_BYTES}-byte cap: {overweight}"
    )
    assert total <= SKILLS_MAX_TOTAL_BYTES, (
        f"total skills/ payload {total}B exceeds {SKILLS_MAX_TOTAL_BYTES}B cap"
    )


def test_skills_pattern_doc_present() -> None:
    """docs/skills-grid-pattern.md exists + is non-trivial — drop-in
    documentation is part of the #71 deliverable."""
    assert SKILLS_PATTERN_DOC.exists(), (
        "docs/skills-grid-pattern.md missing — pattern doc is part of #71 deliverable"
    )
    body = SKILLS_PATTERN_DOC.read_text(encoding="utf-8")
    assert len(body) > 1500, f"skills pattern doc body is only {len(body)} chars; expected >= 1500"


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


def test_skills_tooltip_esc_and_overflow_polish_in_app_js() -> None:
    """Issue #80: app.js carries the skills-grid tooltip polish block:
    Esc-to-dismiss (WAI-ARIA APG: hide tooltip, KEEP FOCUS on trigger)
    + edge-tile overflow detector that shifts the tooltip horizontally
    so it stays in viewport on narrow desktop widths and at 200%
    browser zoom (WCAG 1.4.10).

    Canary-level test: substring matching, not behavior verification.
    Real behavior verification would require headless-browser tests
    (Playwright/jsdom) — out of scope for this stdlib-only suite."""
    js = APP_JS.read_text(encoding="utf-8")
    assert ".skills-grid" in js, (
        "app.js missing .skills-grid hook for the #80 tooltip polish block"
    )
    assert "shiftTooltipIfNeeded" in js, (
        "app.js missing the edge-tile overflow detector (shiftTooltipIfNeeded) for #80"
    )
    assert "Escape" in js and "skill-icon" in js, (
        "app.js missing the Esc-to-dismiss handler for skill-icon focus (#80)"
    )
    # APG canonical: Esc must hide tooltip while keeping focus on trigger.
    # The implementation uses a data-tooltip-suppressed attribute, NOT blur().
    assert "data-tooltip-suppressed" in js, (
        "Esc handler must use data-tooltip-suppressed (APG: keep focus on "
        "trigger), not blur() which sends focus to <body>"
    )
    assert ".blur()" not in js or "active.blur" not in js, (
        "Esc handler should NOT call blur() on the active skill-icon — "
        "use the data-tooltip-suppressed attribute pattern (WAI-ARIA APG)"
    )
    # Edge-shift transform must preserve translateY(0) so the shifted
    # tooltip stays at its CSS-defined revealed position (CSS rest-state
    # has translateY(4px); a translateX-only transform would mis-align).
    assert "translateY(0)" in js, (
        "edge-shift transform must include translateY(0) to preserve the "
        "CSS hover lift; otherwise shifted tooltip sits 4px below intended"
    )


def test_skills_tooltip_suppression_css_rule_present() -> None:
    """Issue #80: the data-tooltip-suppressed attribute set by the JS
    Esc handler must have a matching CSS rule that hides the tooltip
    while focus remains on the tile (APG pattern). Without this rule,
    setting the attribute does nothing — the tooltip stays visible."""
    css = STYLES_CSS.read_text(encoding="utf-8")
    assert "data-tooltip-suppressed" in css, (
        "styles.css missing the .skill-icon[data-tooltip-suppressed] CSS "
        "rule that hides the tooltip while focus remains on the trigger. "
        "The JS Esc handler depends on this — see #80."
    )
    # Sanity check that the rule actually hides (opacity: 0)
    m = re.search(
        r'\.skill-icon\[data-tooltip-suppressed\][^{]*\{[^}]*opacity\s*:\s*0',
        css,
        flags=re.S,
    )
    assert m, (
        "data-tooltip-suppressed rule must include opacity: 0 to actually "
        "hide the tooltip"
    )


def test_hero_picture_breakpoint_matches_layout() -> None:
    """Issue #79: the <source media> + preload imagesizes breakpoint
    must match the actual hero layout breakpoint in styles.css:307
    (@media max-width: 860px). An off-by-80px mismatch means viewports
    781-860px get the desktop variant served despite the layout being
    in mobile single-column mode at max-width:300px — wasted bytes."""
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = STYLES_CSS.read_text(encoding="utf-8")
    # Confirm the 860px hero layout breakpoint still exists in CSS.
    # Nested rules (`.hero { ... } .hero-grid { ... }`) make a single
    # regex over `[^}]*` unreliable, so check both invariants
    # separately: the @media rule + a `.hero-grid` 1-column rule.
    assert re.search(r'@media\s*\(\s*max-width:\s*860px\s*\)', css), (
        "expected @media (max-width: 860px) in styles.css for hero layout. "
        "If the breakpoint moved, update both this test AND the index.html "
        "<source media> + preload imagesizes to match."
    )
    assert re.search(r'\.hero-grid\s*\{\s*grid-template-columns:\s*1fr', css), (
        "expected `.hero-grid { grid-template-columns: 1fr` somewhere in "
        "styles.css (the mobile 1-column rule paired with the 860px breakpoint)"
    )
    # Picture <source> media must use the same 860px breakpoint
    source_match = re.search(
        r'<source\s+media="\(max-width:\s*860px\)"\s+srcset="static/originals/headshot-fullbody-800',
        html,
    )
    assert source_match, (
        "<picture> <source media> must be (max-width: 860px) to match the "
        "hero layout breakpoint. Found different value — re-check index.html "
        "+ styles.css alignment."
    )
    # Preload imagesizes must use the same 860px breakpoint
    preload_match = re.search(
        r'imagesizes="\(max-width:\s*860px\)\s+100vw,\s*1200px"',
        html,
    )
    assert preload_match, (
        "preload imagesizes must use (max-width: 860px) 100vw, 1200px to "
        "match the <source media> + layout breakpoint"
    )


def test_hero_img_has_width_and_height() -> None:
    """CLS=0 guard: the inner <img> in the hero <picture> must declare
    width + height attributes so the browser reserves space before the
    image loads. Removing these attributes silently regresses CLS."""
    html = INDEX_HTML.read_text(encoding="utf-8")
    start = html.find('<aside class="hero-visual"')
    assert start != -1, "hero-visual <aside> not found"
    end = html.find("</aside>", start)
    hero = html[start:end]
    img_match = re.search(r'<img\s+src="static/originals/headshot-fullbody\.jpg"[^>]*>', hero, flags=re.S)
    assert img_match, "hero <img> not found"
    img_tag = img_match.group(0)
    assert 'width="1200"' in img_tag, (
        "hero <img> must declare width=\"1200\" (CLS=0 guard)"
    )
    assert 'height="798"' in img_tag, (
        "hero <img> must declare height=\"798\" (CLS=0 guard)"
    )


def test_hero_img_has_lcp_attributes() -> None:
    """LCP guard: the inner <img> in the hero <picture> must carry
    fetchpriority=\"high\" + loading=\"eager\" + decoding=\"async\" so
    Chrome prioritizes the fetch and doesn't defer to layout. Each
    attribute is independently load-bearing for the LCP target."""
    html = INDEX_HTML.read_text(encoding="utf-8")
    start = html.find('<aside class="hero-visual"')
    assert start != -1, "hero-visual <aside> not found"
    end = html.find("</aside>", start)
    hero = html[start:end]
    img_match = re.search(r'<img\s+src="static/originals/headshot-fullbody\.jpg"[^>]*>', hero, flags=re.S)
    assert img_match, "hero <img> not found"
    img_tag = img_match.group(0)
    for attr in ('fetchpriority="high"', 'loading="eager"', 'decoding="async"'):
        assert attr in img_tag, (
            f"hero <img> missing {attr} — LCP target depends on this attribute"
        )


def test_hero_alt_text_includes_role() -> None:
    """The hero <img> alt text must identify Naren AND his role
    (Senior AI Platform Engineer), so screen-reader users get the
    same role-context that sighted users see in the adjacent <h1>
    + tagline. Per #69 spec + critique-agent B review."""
    html = INDEX_HTML.read_text(encoding="utf-8")
    start = html.find('<aside class="hero-visual"')
    end = html.find("</aside>", start)
    hero = html[start:end]
    alt_match = re.search(
        r'<img\s+src="static/originals/headshot-fullbody\.jpg"[^>]*alt="([^"]+)"',
        hero,
        flags=re.S,
    )
    assert alt_match, "hero <img> missing alt attribute"
    alt = alt_match.group(1)
    assert "Naren" in alt, f"hero alt must include the name: {alt!r}"
    assert "Engineer" in alt or "Engineering" in alt, (
        f"hero alt must include the role keyword (e.g. 'AI Platform "
        f"Engineer'); got {alt!r}"
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
    test_no_scrapped_exponenthr_outcomes_in_rendered_text,
    test_hero_uses_local_photo_not_external_cdn,
    test_hero_aside_no_data_reveal,
    test_hero_picture_has_mobile_variant,
    test_hero_preload_uses_imagesrcset,
    test_hero_picture_has_avif_and_webp_variants,
    test_no_inline_style_attribute_on_strips,
    test_jetbrains_mono_loaded,
    test_css_uses_tabular_nums,
    test_css_has_print_block,
    test_data_reveal_reduced_motion_fallback,
    test_css_mobile_breakpoint_at_600px,
    test_css_uses_warm_palette_tokens,
    test_repo_context_hooks_card_present,
    test_no_legacy_system_rail_in_systems_grid,
    test_all_ids_unique,
    # ----- Architecture & Write-Ups (issues #56 + #64) -----
    test_supply_chain_post_exists,
    test_supply_chain_post_has_required_sections,
    test_supply_chain_post_word_count_in_range,
    test_supply_chain_post_has_inline_svg_diagram,
    test_supply_chain_post_no_scrapped_outcomes,
    test_index_links_to_supply_chain_post,
    test_index_has_architecture_section,
    # ----- System diagrams (issue #58) -----
    test_index_has_two_system_diagrams,
    test_each_system_diagram_has_title_and_desc,
    test_each_system_diagram_uses_currentcolor,
    test_index_inline_system_diagram_byte_budget,
    # ----- Hover-preview primitive (issue #70) -----
    test_hover_preview_css_module_present,
    test_hover_preview_js_module_present,
    test_hover_preview_resume_triggers_count,
    test_hover_preview_contact_icons_annotated,
    test_hover_preview_total_triggers_count,
    test_hover_preview_assets_committed,
    test_hover_preview_every_linkedin_link_annotated,
    test_hover_preview_every_substack_link_annotated,
    test_hover_preview_linkedin_trigger_count,
    test_hover_preview_substack_trigger_count,
    test_hover_preview_resume_cache_bust_matches_sidecar,
    test_hover_preview_companion_attrs_present,
    test_hover_preview_no_role_dialog,
    test_hover_preview_pattern_doc_present,
    # ----- Substack live-feed mode (hover-preview v2 follow-up) -----
    test_substack_snapshot_pipeline_present,
    test_substack_snapshot_json_schema,
    test_substack_triggers_have_embed_attrs,
    test_app_js_has_substack_render_branch,
    test_styles_css_has_feed_list_module,
    # ----- Skills grid (issue #71) -----
    test_skills_section_present,
    test_skills_nav_link_present,
    test_skills_has_expected_category_count,
    test_skills_each_category_has_valid_icon_count,
    test_skills_every_icon_is_keyboard_focusable,
    test_skills_every_icon_has_visible_name,
    test_skills_every_icon_has_tooltip,
    test_skills_no_external_cdn_refs,
    test_skills_icon_files_present,
    test_skills_icon_byte_budgets,
    test_skills_pattern_doc_present,
    test_skills_tooltip_esc_and_overflow_polish_in_app_js,
    test_skills_tooltip_suppression_css_rule_present,
    test_hero_picture_breakpoint_matches_layout,
    test_hero_img_has_width_and_height,
    test_hero_img_has_lcp_attributes,
    test_hero_alt_text_includes_role,
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
