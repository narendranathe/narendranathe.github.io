/* ============================================================
   NARENDRANATH EDARA — portfolio app.js
   Nav glassmorphism · scroll reveal · count-up · expand/collapse
   ============================================================ */
(function () {
  'use strict';

  function forEachNode(nodes, fn) {
    Array.prototype.forEach.call(nodes || [], fn);
  }

  function makeEl(tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  }

  function clearChildren(el) {
    while (el.firstChild) el.removeChild(el.firstChild);
  }

  // Rewrite the compressed Azure support card into the visible SSIS_LoadPrep
  // narrative without touching unsafe HTML strings. index.html keeps the
  // base markup; this layer upgrades the card at runtime for hiring-manager
  // readability until the static section is permanently restructured.
  (function enhanceSSISLoadPrepCard() {
    var title = document.getElementById('card-azure');
    if (!title) return;

    var card = title.closest('.support-card');
    if (!card) return;
    card.style.gridColumn = '1 / -1';

    var label = card.querySelector('.section-label');
    if (label) label.textContent = 'Enterprise Data Platform Automation';

    title.id = 'card-ssis-loadprep';
    title.textContent = 'SSIS_LoadPrep';

    var strip = card.querySelector('.impact-strip');
    if (strip) {
      strip.setAttribute('aria-labelledby', 'card-ssis-loadprep');
      clearChildren(strip);

      [
        {
          value: '~1hr',
          label: 'saved per AAG copy-down',
          sr: ' — one-click Azure DevOps orchestration removes about an hour of manual restore, security, CDC, and listener validation work per request.'
        },
        {
          value: '20+',
          label: 'daily refresh requests',
          sr: ' — multi-client batching and deterministic execution cover more than twenty payroll-critical copy-down requests per day.'
        },
        {
          value: '-67%',
          label: 'CDC ETL compute',
          sr: ' — incremental merge-upserts replaced full-table reload behavior in the CDC ETL path.'
        },
        {
          value: '3mo→14d',
          label: 'deployment cycle',
          sr: ' — Azure DevOps ownership compressed the release path from three months to fourteen days.'
        }
      ].forEach(function (stat) {
        var row = makeEl('div', 'impact-stat');
        row.appendChild(makeEl('dt', 'impact-value', stat.value));
        var dd = makeEl('dd', 'impact-label', stat.label);
        dd.appendChild(makeEl('span', 'sr-only', stat.sr));
        row.appendChild(dd);
        strip.appendChild(row);
      });
    }

    forEachNode(Array.prototype.slice.call(card.children), function (child) {
      if (child.tagName === 'P' || child.classList.contains('support-chips')) {
        card.removeChild(child);
      }
    });

    var p1 = makeEl('p', null,
      'SSIS_LoadPrep started as an operations bottleneck: payroll-critical database refreshes needed repeatable copy-downs, CDC ETL had to keep its watermarks sane, and every manual Always-On Availability Group step created room for production-impacting drift. I turned that into deterministic Azure DevOps orchestration that builds, deploys, validates, and executes refreshes across client databases instead of relying on ad-hoc DBA handoffs.'
    );

    var p2 = makeEl('p', null,
      'The hard part was not the restore; it was correctness. The pipeline checks whether a target is safe before it runs, blocks LIVE servers with a hard FINDSTRING gate, detects CDC state, cleans orphaned capture jobs from msdb.sysjobs after database drops, and resets the right incremental path so downstream SSIS packages do not inherit broken LSN metadata.'
    );

    var details = makeEl('ul', 'track-bullets');
    [
      'Dual-path CDC cleanup: handles normal cdc_enabled metadata and orphaned msdb job patterns when dropped databases no longer appear in sys.databases.',
      'AAG state machine: restore, security sync, CDC validation, listener checks, and copy-down execution are orchestrated as explicit pipeline stages.',
      'Safety and observability: LIVE-environment hard stop, structured per-step logging, email notifications, and rerunnable idempotent design.'
    ].forEach(function (text) {
      details.appendChild(makeEl('li', null, text));
    });

    var chips = makeEl('div', 'support-chips');
    [
      'Azure DevOps', 'SSIS', 'SQL Server CDC', 'Always-On AAG',
      'T-SQL', 'Idempotent pipelines', 'Payroll data'
    ].forEach(function (chipText) {
      chips.appendChild(makeEl('span', 'chip', chipText));
    });

    function diagramFigure(src, w, h, alt, caption) {
      var fig = makeEl('figure', 'system-diagram-figure');
      var img = makeEl('img', 'system-diagram');
      img.src = src;
      img.width = w;
      img.height = h;
      img.loading = 'lazy';
      img.decoding = 'async';
      img.alt = alt;
      fig.appendChild(img);
      fig.appendChild(makeEl('figcaption', 'post-figcaption', caption));
      return fig;
    }

    var execFig = diagramFigure(
      'assets/diagrams/ssis-loadprep-executive-view.svg', 1600, 950,
      'Executive view of SSIS_LoadPrep: a before/after for IT leaders showing manual handoffs becoming a governed control plane, with about an hour saved per copy-down, 67% less CDC ETL compute, and a deployment cycle compressed from three months to fourteen days.',
      'Executive view — manual copy-down coordination becomes a governed control plane: it validates the target is safe before restore, runs the copy-down as explicit stages, repairs CDC state, and logs, notifies, and reruns safely.'
    );

    var techFig = diagramFigure(
      'assets/diagrams/ssis-loadprep-technical-architecture.svg', 1800, 1100,
      'SSIS_LoadPrep technical architecture: a four-layer state machine covering orchestration, a LIVE-server FINDSTRING guard with safe restore and AAG readiness checks, CDC cleanup of sys.databases and orphaned msdb.sysjobs with LSN reset, and an observe-and-rerun feedback loop.',
      'Technical architecture — a LIVE-server FINDSTRING guard blocks before restore; CDC cleanup detects sys.databases and msdb.sysjobs and resets watermarks before downstream SSIS ETL; every stage feeds an idempotent log, notify, and rerun loop.'
    );

    var actions = makeEl('div', 'card-actions');
    var walkthrough = makeEl('a', 'cs-btn', 'Architecture walkthrough');
    walkthrough.href = 'https://github.com/narendranathe/narendranathe.github.io/blob/main/docs/ssis-loadprep-architecture.md';
    walkthrough.target = '_blank';
    walkthrough.rel = 'noreferrer';
    actions.appendChild(walkthrough);
    var fullDiagram = makeEl('a', 'text-link');
    fullDiagram.href = 'assets/diagrams/ssis-loadprep-technical-architecture.svg';
    fullDiagram.target = '_blank';
    fullDiagram.rel = 'noreferrer';
    fullDiagram.appendChild(makeEl('i', 'fas fa-sitemap'));
    fullDiagram.appendChild(document.createTextNode(' Full technical diagram'));
    actions.appendChild(fullDiagram);

    card.appendChild(execFig);
    card.appendChild(p1);
    card.appendChild(p2);
    card.appendChild(techFig);
    card.appendChild(details);
    card.appendChild(actions);
    card.appendChild(chips);
  }());

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
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.07, rootMargin: '0px 0px -40px 0px' });
    forEachNode(document.querySelectorAll('[data-reveal]'), function (el) { obs.observe(el); });
  } else {
    forEachNode(document.querySelectorAll('[data-reveal]'), function (el) { el.classList.add('revealed'); });
  }

  // Count-up animation for [data-count] elements
  forEachNode(document.querySelectorAll('[data-count]'), function (el) {
    var target = parseInt(el.getAttribute('data-count'), 10);
    if (isNaN(target)) return;
    var started = false;

    function run() {
      if (started) return;
      started = true;
      var t0 = null;
      var dur = 1400;
      requestAnimationFrame(function step(ts) {
        if (!t0) t0 = ts;
        var p = Math.min((ts - t0) / dur, 1);
        var ease = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(ease * target);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target;
      });
    }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries, observer) {
        if (entries[0].isIntersecting) {
          run();
          observer.disconnect();
        }
      }, { threshold: 0.4 }).observe(el);
    } else {
      run();
    }
  });

  // Expand / collapse architecture panels
  forEachNode(document.querySelectorAll('.expand-btn'), function (btn) {
    btn.addEventListener('click', function () {
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!expanded));
      var body = btn.closest('.system-body, .track-card, .support-card');
      if (!body) return;
      var panel = body.querySelector('.arch-expand');
      if (!panel) return;
      panel.hidden = expanded;
      btn.textContent = expanded ? (btn.getAttribute('data-label') || 'See architecture') : 'Collapse';
    });
  });

  // ML Pipeline accordion
  forEachNode(document.querySelectorAll('.accordion-trigger'), function (trigger) {
    trigger.addEventListener('click', function () {
      var expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      var body = trigger.nextElementSibling;
      if (body) body.hidden = expanded;
    });
  });

  // Mobile nav
  (function setupMobileNav() {
    var toggle = document.querySelector('.mobile-toggle');
    var mobileNav = document.querySelector('.mobile-nav');
    if (!toggle || !mobileNav) return;

    function closeNav() {
      toggle.setAttribute('aria-expanded', 'false');
      mobileNav.setAttribute('aria-hidden', 'true');
      mobileNav.classList.remove('is-open');
      var icon = toggle.querySelector('i');
      if (icon) icon.className = 'fas fa-bars';
    }

    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      mobileNav.setAttribute('aria-hidden', String(open));
      mobileNav.classList.toggle('is-open', !open);
      var icon = toggle.querySelector('i');
      if (icon) icon.className = open ? 'fas fa-bars' : 'fas fa-times';
    });

    forEachNode(mobileNav.querySelectorAll('.mobile-link'), function (link) {
      link.addEventListener('click', closeNav);
    });
  }());

  var prefersReducedMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Splash screen — sessionStorage gate, 1.6 s
  (function setupSplash() {
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

  // Hover-preview primitive for resume, LinkedIn, GitHub, and Substack links.
  (function setupHoverPreview() {
    var triggers = document.querySelectorAll('[data-hover-preview]');
    if (!triggers.length) return;

    var isTouch = window.matchMedia &&
      window.matchMedia('(hover: none) and (pointer: coarse)').matches;
    if (isTouch || !('showPopover' in HTMLElement.prototype)) return;

    var OPEN_DELAY = 80;
    var CLOSE_GRACE = 250;
    var card, inner, thumb, textWrap, titleEl, captionEl;
    var lastTrigger = null;
    var openTimer = null;
    var closeTimer = null;
    var renderMode = null;
    var feedCache = Object.create(null);
    var feedFetching = Object.create(null);

    function ensureCard() {
      if (card) return;
      card = makeEl('div', 'hover-preview');
      card.id = 'hover-preview-card';
      card.setAttribute('popover', 'manual');

      inner = makeEl('div', 'hover-preview-card');
      thumb = makeEl('img', 'hover-preview-thumb');
      thumb.setAttribute('alt', '');
      thumb.setAttribute('decoding', 'async');
      thumb.setAttribute('loading', 'lazy');
      thumb.setAttribute('width', '240');
      thumb.setAttribute('height', '320');

      textWrap = makeEl('div', 'hover-preview-text');
      titleEl = makeEl('p', 'hover-preview-title');
      captionEl = makeEl('p', 'hover-preview-caption');
      textWrap.appendChild(titleEl);
      textWrap.appendChild(captionEl);
      inner.appendChild(thumb);
      inner.appendChild(textWrap);
      card.appendChild(inner);
      document.body.appendChild(card);

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
      var maxTop = window.innerHeight - rc.height - pad;
      if (left < pad) left = pad;
      if (left > maxLeft) left = maxLeft;
      if (top + rc.height > window.innerHeight - pad) top = rt.top - rc.height - pad;
      if (top < pad) top = pad;
      if (top > maxTop) top = maxTop;
      card.style.top = top + 'px';
      card.style.left = left + 'px';
    }

    function renderStatic(trigger) {
      if (renderMode !== 'static') {
        clearChildren(inner);
        inner.appendChild(thumb);
        inner.appendChild(textWrap);
        renderMode = 'static';
      }
      var src = trigger.getAttribute('data-hover-preview');
      if (thumb.getAttribute('src') !== src) thumb.setAttribute('src', src);
      titleEl.textContent = trigger.getAttribute('data-hover-title') || '';
      captionEl.textContent = trigger.getAttribute('data-hover-caption') || '';
    }

    function formatFeedDate(iso) {
      if (!iso) return '';
      var d = new Date(iso);
      if (isNaN(d.getTime())) return iso;
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }

    function normalizeUrl(url) {
      return (url || '').split('#')[0].replace(/\/$/, '');
    }

    function selectPostsForTrigger(allPosts, triggerHref) {
      if (!triggerHref) return allPosts.slice(0, 3);
      var target = normalizeUrl(triggerHref);
      var pinned = null;
      for (var i = 0; i < allPosts.length; i++) {
        if (normalizeUrl(allPosts[i].url) === target) {
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
      frag.appendChild(makeEl('p', 'hp-feed-header',
        (data && data.publication) || trigger.getAttribute('data-hover-title') || 'Latest posts'));

      var allPosts = (data && data.posts) || [];
      if (!allPosts.length) {
        frag.appendChild(makeEl('p', 'hp-feed-empty', data === null ? 'Could not load latest posts.' : 'No posts yet.'));
        return frag;
      }

      var list = makeEl('ul', 'hp-feed-list');
      selectPostsForTrigger(allPosts, trigger.getAttribute('href')).forEach(function (post) {
        var item = makeEl('a', 'hp-feed-item');
        item.href = post.url;
        item.target = '_blank';
        item.rel = 'noreferrer';
        item.appendChild(makeEl('p', 'hp-feed-title', post.title));
        item.appendChild(makeEl('p', 'hp-feed-meta', formatFeedDate(post.published_at)));
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

      inner.appendChild(makeEl('p', 'hp-feed-empty', 'Loading latest posts...'));
      if (!feedFetching[feedUrl]) {
        feedFetching[feedUrl] = true;
        fetch(feedUrl, { cache: 'default' })
          .then(function (r) { return r.ok ? r.json() : null; })
          .then(function (data) {
            feedCache[feedUrl] = data;
            if (lastTrigger && lastTrigger.getAttribute('data-hover-feed') === feedUrl &&
                card.matches(':popover-open')) {
              clearChildren(inner);
              inner.appendChild(buildFeedDom(lastTrigger, data));
              requestAnimationFrame(function () { position(lastTrigger); });
            }
          })
          .catch(function () {
            feedCache[feedUrl] = null;
            if (lastTrigger === trigger) renderStatic(trigger);
          });
      }
    }

    function open(trigger) {
      ensureCard();
      if (trigger.getAttribute('data-hover-embed') === 'substack-feed') renderSubstack(trigger);
      else renderStatic(trigger);
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
    }

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && card && card.matches(':popover-open')) {
        close();
        if (lastTrigger) lastTrigger.focus();
      }
    });

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
    forEachNode(triggers, attach);
  }());

  // Skills grid tooltip polish (#80)
  (function setupSkillTooltips() {
    var grid = document.querySelector('.skills-grid');
    if (!grid) return;

    var rootFontPx = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
    var EDGE_MARGIN = Math.round(rootFontPx * 0.75);

    function clearSuppression(tile) {
      tile.removeAttribute('data-tooltip-suppressed');
    }

    function shiftTooltipIfNeeded(tile) {
      var tooltip = tile.querySelector('.skill-tooltip');
      if (!tooltip) return;
      tooltip.style.transform = '';
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

    forEachNode(grid.querySelectorAll('.skill-icon'), function (tile) {
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
        active.setAttribute('data-tooltip-suppressed', '');
      }
    });
  }());
}());


