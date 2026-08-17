"""Find elements whose content is wider than the viewport, or whose own
box extends past it.

Run against a local server:  python -m http.server 8080
Then:                        python scripts/check-clipping.py
Exits non-zero on any finding. Requires Playwright, which is why this is a
separate script rather than an assertion inside the stdlib-only suite in
test-portfolio.py.

The existing QA compared document scrollWidth to clientWidth, which only
catches overflow that makes the PAGE scroll. An element inside an
overflow-x:auto or overflow:hidden ancestor is clipped without the page
ever growing, so that check passes while text is cut off. This one walks
every element and reports both conditions.
"""
import sys
from playwright.sync_api import sync_playwright
EXE = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
DEFAULT_PAGES = [
    "/index.html", "/autoapply-ai.html", "/tailor-resume.html",
    "/jobscout.html", "/portfolio-risk.html", "/fintune.html",
    "/fraud-detection.html",
    "/content/posts/repo-context-hooks-supply-chain.html",
]
PAGES = sys.argv[1:] or DEFAULT_PAGES
VIEWPORTS = [(320, 720), (390, 844), (768, 1024)]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=EXE)
    bad_total = 0
    for path in PAGES:
        for w, h in VIEWPORTS:
            ctx = b.new_context(viewport={"width": w, "height": h})
            ctx.route("**/*", lambda r: r.continue_() if "127.0.0.1" in r.request.url else r.abort())
            p = ctx.new_page()
            p.goto(f"http://127.0.0.1:8080{path}", wait_until="domcontentloaded")
            p.wait_for_timeout(900)
            p.add_style_tag(content="#splash-screen{display:none!important}"
                                    "[data-reveal]{opacity:1!important;transform:none!important}"
                                    "*{animation:none!important;transition:none!important}")
            p.wait_for_timeout(300)
            findings = p.evaluate("""(vw) => {
                const out = [];
                document.querySelectorAll('body *').forEach(e => {
                    const cs = getComputedStyle(e);
                    if (cs.display === 'none' || cs.visibility === 'hidden') return;
                    const r = e.getBoundingClientRect();
                    if (r.width === 0 || r.height === 0) return;
                    // Content wider than the element's own visible box: the
                    // element clips its own children.
                    const selfClip = e.scrollWidth - e.clientWidth;
                    // Element box extending beyond the viewport's right edge.
                    const past = Math.round(r.right - vw);
                    // The circular headshot frame crops a scaled-up photo
                    // on purpose; that is the whole point of the frame.
                    if (e.classList.contains('profile-frame')) return;
                    // A shell command or a YAML block must not be wrapped at
                    // an arbitrary column, so <pre>/<code> scrolling inside
                    // its own container is the correct treatment, not a bug.
                    if (e.closest('pre')) return;
                    if (selfClip > 2 || past > 2) {
                        const id = e.id ? '#' + e.id : '';
                        const cls = e.className && typeof e.className === 'string'
                            ? '.' + e.className.trim().split(/\\s+/).slice(0,2).join('.') : '';
                        out.push({tag: e.tagName.toLowerCase() + id + cls,
                                  clip: selfClip, past: past,
                                  ox: cs.overflowX,
                                  txt: (e.textContent||'').replace(/\\s+/g,' ').trim().slice(0,52)});
                    }
                });
                return out;
            }""", w)
            # An element that scrolls on purpose is fine only if nothing is
            # actually hidden; report anything clipped or off-viewport.
            if findings:
                print(f"\n{path} @ {w}x{h}: {len(findings)} finding(s)")
                for f in findings[:12]:
                    why = []
                    if f["clip"] > 2: why.append(f"clips {f['clip']}px (overflow-x:{f['ox']})")
                    if f["past"] > 2: why.append(f"{f['past']}px past right edge")
                    print(f"   {f['tag']:<34} {', '.join(why)}")
                    print(f"     {f['txt']!r}")
                bad_total += len(findings)
            else:
                print(f"{path} @ {w}x{h}: clean")
            ctx.close()
    b.close()
    print(f"\n{bad_total} total finding(s)")
    sys.exit(1 if bad_total else 0)
