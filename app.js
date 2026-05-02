/* ============================================================
   NARENDRANATH EDARA — portfolio app.js
   Nav glassmorphism · scroll reveal · count-up · expand/collapse
   ============================================================ */
(function () {
  'use strict';

  // Nav becomes opaque + blurred on scroll
  var hdr = document.getElementById('site-header');
  if (hdr) {
    window.addEventListener('scroll', function () {
      hdr.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }

  // Scroll reveal via IntersectionObserver
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('revealed'); obs.unobserve(e.target); }
      });
    }, { threshold: 0.07, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('[data-reveal]').forEach(function (el) { obs.observe(el); });
  } else {
    document.querySelectorAll('[data-reveal]').forEach(function (el) { el.classList.add('revealed'); });
  }

  // Count-up animation for [data-count] elements
  document.querySelectorAll('[data-count]').forEach(function (el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(target)) return;
    var started = false;
    function run() {
      if (started) return; started = true;
      var t0 = null, dur = 1400;
      requestAnimationFrame(function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min((ts - t0) / dur, 1), ease = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(ease * target);
        if (p < 1) requestAnimationFrame(step); else el.textContent = target;
      });
    }
    new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { run(); }
    }, { threshold: 0.4 }).observe(el);
  });

  // Expand / collapse architecture panels
  document.querySelectorAll('.expand-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      var body  = btn.closest('.system-body, .track-card, .support-card');
      if (!body) return;
      var panel = body.querySelector('.arch-expand');
      if (!panel) return;
      panel.hidden = expanded;
      btn.textContent = expanded ? (btn.getAttribute('data-label') || 'See architecture') : 'Collapse';
    });
  });

  // ML Pipeline accordion
  document.querySelectorAll('.accordion-trigger').forEach(function (trigger) {
    trigger.addEventListener('click', function () {
      var expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      var body = trigger.nextElementSibling;
      if (body) body.hidden = expanded;
    });
  });

  // Mobile nav
  var toggle = document.querySelector('.mobile-toggle');
  var mobileNav = document.querySelector('.mobile-nav');
  if (toggle && mobileNav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      mobileNav.setAttribute('aria-hidden', String(open));
      mobileNav.classList.toggle('is-open', !open);
      toggle.querySelector('i').className = open ? 'fas fa-bars' : 'fas fa-times';
    });
    mobileNav.querySelectorAll('.mobile-link').forEach(function (l) {
      l.addEventListener('click', function () {
        toggle.setAttribute('aria-expanded', 'false');
        mobileNav.setAttribute('aria-hidden', 'true');
        mobileNav.classList.remove('is-open');
        toggle.querySelector('i').className = 'fas fa-bars';
      });
    });
  }

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Splash screen — sessionStorage gate, 1.6 s ----
  (function () {
    var splash = document.getElementById('splash-screen');
    if (!splash) return;
    if (sessionStorage.getItem('splashSeen')) {
      splash.classList.add('splash-hidden');
      return;
    }
    document.body.classList.add('splash-active');
    setTimeout(function () {
      splash.classList.add('splash-hidden');
      document.body.classList.remove('splash-active');
      sessionStorage.setItem('splashSeen', '1');
    }, prefersReducedMotion ? 0 : 1600);
  }());



  // Footer year + scroll progress
  var yr = document.getElementById('footer-year');
  if (yr) yr.textContent = new Date().getFullYear();

  var prog = document.getElementById('scroll-progress');
  if (prog) {
    window.addEventListener('scroll', function () {
      var d = document.documentElement.scrollHeight - window.innerHeight;
      prog.style.width = (d > 0 ? (window.scrollY / d) * 100 : 0) + '%';
    }, { passive: true });
  }

  // -------------------------------------------------------------
  // Hover-preview primitive (#70). Drop-in for any link with
  // data-hover-preview / data-hover-title / data-hover-caption.
  // Uses native HTML Popover API (Chrome 114+, Safari 17+, FF 125+).
  // Touch devices skip entirely - see CSS @media (hover: none).
  // Pattern: docs/hover-preview-pattern.md
  // -------------------------------------------------------------
  (function () {
    var triggers = document.querySelectorAll('[data-hover-preview]');
    if (!triggers.length) return;

    var isTouch = window.matchMedia &&
      window.matchMedia('(hover: none) and (pointer: coarse)').matches;
    if (isTouch) return;

    if (!('showPopover' in HTMLElement.prototype)) return;

    var OPEN_DELAY  = 80;
    var CLOSE_GRACE = 250;

    // Closure-scoped so renderStatic() + renderSubstack() can swap them
    // in/out of the card's `inner` container as the render mode changes.
    var card, inner, thumb, textWrap, titleEl, captionEl;
    var lastTrigger = null;
    var openTimer = null;
    var closeTimer = null;

    function ensureCard() {
      if (card) return;
      card = document.createElement('div');
      card.className = 'hover-preview';
      card.id = 'hover-preview-card';
      card.setAttribute('popover', 'manual');

      inner = document.createElement('div');
      inner.className = 'hover-preview-card';

      thumb = document.createElement('img');
      thumb.className = 'hover-preview-thumb';
      thumb.setAttribute('alt', '');
      thumb.setAttribute('decoding', 'async');
      thumb.setAttribute('loading', 'lazy');
      thumb.setAttribute('width', '240');
      thumb.setAttribute('height', '320');
      inner.appendChild(thumb);

      textWrap = document.createElement('div');
      textWrap.className = 'hover-preview-text';
      titleEl = document.createElement('p');
      titleEl.className = 'hover-preview-title';
      captionEl = document.createElement('p');
      captionEl.className = 'hover-preview-caption';
      textWrap.appendChild(titleEl);
      textWrap.appendChild(captionEl);
      inner.appendChild(textWrap);

      card.appendChild(inner);
      document.body.appendChild(card);

      // Cursor on the card itself keeps it open (WCAG 1.4.13 hoverable).
      card.addEventListener('mouseenter', function () { clearTimeout(closeTimer); });
      card.addEventListener('mouseleave', scheduleClose);
    }

    function position(trigger) {
      var rt = trigger.getBoundingClientRect();
      var rc = card.getBoundingClientRect();
      var pad = 8;
      var top = rt.bottom + pad;
      var left = rt.left + rt.width / 2 - rc.width / 2;
      var maxLeft = window.innerWidth - rc.width - pad;
      var maxTop  = window.innerHeight - rc.height - pad;
      if (left < pad) left = pad;
      if (left > maxLeft) left = maxLeft;
      if (top + rc.height > window.innerHeight - pad) {
        // Try flipping above the trigger if there's room there.
        top = rt.top - rc.height - pad;
      }
      // Final clamp: keep popover inside the viewport even when the
      // trigger has scrolled partly off-screen (the scroll listener
      // re-calls this on every frame; without clamping, the popover
      // drifts off the visible area when the trigger does).
      if (top < pad) top = pad;
      if (top > maxTop) top = maxTop;
      card.style.top  = top  + 'px';
      card.style.left = left + 'px';
    }

    function clearChildren(el) {
      // Safe DOM clear without using innerHTML (avoids XSS-by-mistake
      // surface and pleases the repo's security lint hook).
      while (el.firstChild) el.removeChild(el.firstChild);
    }

    // ---- Render-mode branch (substack-live follow-up) ----
    // Static mode (default): reuses the cached thumb + title + caption
    // children. Substack-feed mode: replaces inner with the live-feed
    // list rendered from /static/substack-latest.json (snapshot built
    // hourly by .github/workflows/substack-snapshot.yml). Cached per
    // feed URL so the fetch only happens once per page load.
    var renderMode = null;  // 'static' | 'substack-feed'
    var feedCache = Object.create(null);
    var feedFetching = Object.create(null);

    function renderStatic(trigger) {
      if (renderMode !== 'static') {
        clearChildren(inner);
        inner.appendChild(thumb);
        inner.appendChild(textWrap);
        renderMode = 'static';
      }
      var src = trigger.getAttribute('data-hover-preview');
      if (thumb.getAttribute('src') !== src) thumb.setAttribute('src', src);
      titleEl.textContent   = trigger.getAttribute('data-hover-title')   || '';
      captionEl.textContent = trigger.getAttribute('data-hover-caption') || '';
    }

    function formatFeedDate(iso) {
      if (!iso) return '';
      var d = new Date(iso);
      if (isNaN(d.getTime())) return iso;
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }

    function selectPostsForTrigger(allPosts, triggerHref) {
      // Per-trigger pin: if the trigger's href is a specific post URL
      // (not the publication root), find that post in the JSON and
      // surface it FIRST, followed by the 2 next most recent posts
      // (excluding the pinned one). For root-URL triggers — or any
      // href that doesn't match a post — fall back to the top-3
      // most-recent default.
      if (!triggerHref) return allPosts.slice(0, 3);
      // Normalize: ignore trailing slash + url fragment for match
      var norm = function (u) { return (u || '').split('#')[0].replace(/\/$/, ''); };
      var target = norm(triggerHref);
      var pinned = null;
      for (var i = 0; i < allPosts.length; i++) {
        if (norm(allPosts[i].url) === target) {
          pinned = allPosts[i];
          break;
        }
      }
      if (!pinned) return allPosts.slice(0, 3);
      var others = allPosts.filter(function (p) { return p !== pinned; });
      return [pinned].concat(others.slice(0, 2));
    }

    function buildFeedDom(trigger, data) {
      var frag = document.createDocumentFragment();
      var header = document.createElement('p');
      header.className = 'hp-feed-header';
      header.textContent = (data && data.publication) ||
        trigger.getAttribute('data-hover-title') || 'Latest posts';
      frag.appendChild(header);

      var allPosts = (data && data.posts) || [];
      if (!allPosts.length) {
        var empty = document.createElement('p');
        empty.className = 'hp-feed-empty';
        empty.textContent = (data === null) ? 'Could not load latest posts.' : 'No posts yet.';
        frag.appendChild(empty);
        return frag;
      }
      var posts = selectPostsForTrigger(allPosts, trigger.getAttribute('href'));

      var list = document.createElement('ul');
      list.className = 'hp-feed-list';
      posts.forEach(function (post) {
        var item = document.createElement('a');
        item.className = 'hp-feed-item';
        item.href = post.url;
        item.target = '_blank';
        item.rel = 'noreferrer';

        var title = document.createElement('p');
        title.className = 'hp-feed-title';
        title.textContent = post.title;
        item.appendChild(title);

        var meta = document.createElement('p');
        meta.className = 'hp-feed-meta';
        meta.textContent = formatFeedDate(post.published_at);
        item.appendChild(meta);

        var li = document.createElement('li');
        li.appendChild(item);
        list.appendChild(li);
      });
      frag.appendChild(list);
      return frag;
    }

    function renderSubstack(trigger) {
      clearChildren(inner);
      renderMode = 'substack-feed';
      var feedUrl = trigger.getAttribute('data-hover-feed') || '/static/substack-latest.json';

      if (feedCache[feedUrl] !== undefined) {
        inner.appendChild(buildFeedDom(trigger, feedCache[feedUrl]));
        return;
      }

      // Loading placeholder shown while the JSON is in-flight.
      var loading = document.createElement('p');
      loading.className = 'hp-feed-empty';
      loading.textContent = 'Loading latest posts...';
      inner.appendChild(loading);

      if (!feedFetching[feedUrl]) {
        feedFetching[feedUrl] = true;
        fetch(feedUrl, { cache: 'default' })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (data) {
            feedCache[feedUrl] = data;
            // Re-render if the same trigger is still showing.
            if (lastTrigger && lastTrigger.getAttribute('data-hover-feed') === feedUrl &&
                card.matches(':popover-open')) {
              clearChildren(inner);
              inner.appendChild(buildFeedDom(lastTrigger, data));
              requestAnimationFrame(function () { position(lastTrigger); });
            }
          })
          .catch(function () {
            feedCache[feedUrl] = null;
            // Fallback: degrade to the static thumbnail render path.
            if (lastTrigger === trigger) renderStatic(trigger);
          });
      }
    }

    function open(trigger) {
      ensureCard();
      var embedType = trigger.getAttribute('data-hover-embed');
      if (embedType === 'substack-feed') {
        renderSubstack(trigger);
      } else {
        renderStatic(trigger);
      }
      if (!card.matches(':popover-open')) {
        try { card.showPopover(); } catch (_) { /* noop */ }
      }
      requestAnimationFrame(function () { position(trigger); });
      lastTrigger = trigger;
    }

    function close() {
      if (card && card.matches(':popover-open')) {
        try { card.hidePopover(); } catch (_) { /* noop */ }
      }
    }

    function scheduleOpen(trigger) {
      clearTimeout(closeTimer);
      clearTimeout(openTimer);
      openTimer = setTimeout(function () { open(trigger); }, OPEN_DELAY);
    }
    function scheduleClose() {
      clearTimeout(openTimer);
      clearTimeout(closeTimer);
      closeTimer = setTimeout(close, CLOSE_GRACE);
    }

    function attach(trigger) {
      trigger.addEventListener('mouseenter', function () { scheduleOpen(trigger); });
      trigger.addEventListener('mouseleave', scheduleClose);
      trigger.addEventListener('focus', function () {
        clearTimeout(closeTimer);
        clearTimeout(openTimer);
        open(trigger);
      });
      // Deliberately NO close-on-blur. Keyboard users need persistent card
      // content (WCAG 1.4.13 hoverable for keyboard). The card has no
      // focusable children, so Tab from the trigger leaves focus entirely;
      // closing the card on that blur would give the keyboard user a
      // 0-frame glimpse. Closes via:
      //   - Esc (document keydown handler below)
      //   - mouse leaving both trigger and card (mouseleave + grace timer)
      //   - focus moving to another [data-hover-preview] trigger, whose
      //     own focus handler re-uses the shared card and replaces content
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && card && card.matches(':popover-open')) {
        close();
        if (lastTrigger) lastTrigger.focus();
      }
    });

    // Scroll-aware positioning: the popover is `position: fixed` and
    // `position(trigger)` previously ran ONCE on open, leaving the
    // card frozen at its original viewport coordinates while the
    // trigger drifted away during scroll. Re-call position() on every
    // scroll/resize while the card is open, throttled via rAF so
    // momentum-scroll doesn't fire 120 times/second. Capture phase
    // catches scroll events from internal scrollable containers
    // (some don't bubble to window).
    var rafScroll = null;
    function onScrollOrResize() {
      if (rafScroll || !card || !card.matches(':popover-open') || !lastTrigger) return;
      rafScroll = requestAnimationFrame(function () {
        position(lastTrigger);
        rafScroll = null;
      });
    }
    window.addEventListener('scroll', onScrollOrResize, { passive: true, capture: true });
    window.addEventListener('resize', onScrollOrResize, { passive: true });

    Array.prototype.forEach.call(triggers, attach);
  }());


  // ===== Skills grid tooltip polish (#80) =====
  // 1. Esc-to-dismiss: WAI-ARIA APG tooltip pattern says Esc should
  //    HIDE the tooltip while keeping focus on the trigger. We mark
  //    the tile with data-tooltip-suppressed and a CSS rule hides
  //    the tooltip; suppression clears on next focus/mouseenter so
  //    the tile remains a working tooltip trigger.
  // 2. Edge-tile overflow: rightmost tiles had their tooltip overflow
  //    the viewport on narrow desktop widths and at 200% zoom (WCAG
  //    1.4.10 reflow). Measures the tooltip rect on focus/mouseenter
  //    and translates horizontally to stay inside the viewport. The
  //    JS-set transform preserves translateY(0) so the tooltip stays
  //    at its CSS-defined revealed position (CSS rest-state has
  //    translateY(4px); a translateX-only transform would drop the
  //    lift and visibly mis-align the shifted tooltip by 4px).
  // CSS-only edge detection is unreliable under auto-fill grids
  // (column count varies with viewport), so this lives in JS but
  // only runs on focus/mouseenter — zero cost when idle.
  (function () {
    var grid = document.querySelector('.skills-grid');
    if (!grid) return;

    // EDGE_MARGIN scales with the user's root font-size so 200% text
    // zoom (Firefox text-only zoom) doesn't shrink the breathing room.
    var rootFontPx = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
    var EDGE_MARGIN = Math.round(rootFontPx * 0.75); // ~12px at default

    function clearSuppression(tile) {
      tile.removeAttribute('data-tooltip-suppressed');
    }

    function shiftTooltipIfNeeded(tile) {
      var tooltip = tile.querySelector('.skill-tooltip');
      if (!tooltip) return;
      tooltip.style.transform = ''; // reset before measuring
      var rect = tooltip.getBoundingClientRect();
      var vw = window.innerWidth;
      var overshootRight = rect.right - (vw - EDGE_MARGIN);
      var overshootLeft = EDGE_MARGIN - rect.left;
      if (overshootRight > 0) {
        tooltip.style.transform = 'translateX(calc(-50% - ' + overshootRight + 'px)) translateY(0)';
      } else if (overshootLeft > 0) {
        tooltip.style.transform = 'translateX(calc(-50% + ' + overshootLeft + 'px)) translateY(0)';
      }
    }

    function clearShift(tile) {
      var tooltip = tile.querySelector('.skill-tooltip');
      if (tooltip) tooltip.style.transform = '';
    }

    Array.prototype.forEach.call(grid.querySelectorAll('.skill-icon'), function (tile) {
      tile.addEventListener('mouseenter', function () {
        clearSuppression(tile);
        shiftTooltipIfNeeded(tile);
      });
      tile.addEventListener('focus', function () {
        clearSuppression(tile);
        shiftTooltipIfNeeded(tile);
      });
      tile.addEventListener('mouseleave', function () { clearShift(tile); });
      tile.addEventListener('blur', function () {
        clearShift(tile);
        clearSuppression(tile);
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var active = document.activeElement;
      if (active && active.classList && active.classList.contains('skill-icon')) {
        // APG tooltip pattern: hide tooltip, keep focus on trigger.
        active.setAttribute('data-tooltip-suppressed', '');
      }
    });
  }());

})();
