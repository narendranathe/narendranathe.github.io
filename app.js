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

    var card, thumb, titleEl, captionEl;
    var lastTrigger = null;
    var openTimer = null;
    var closeTimer = null;

    function ensureCard() {
      if (card) return;
      card = document.createElement('div');
      card.className = 'hover-preview';
      card.id = 'hover-preview-card';
      card.setAttribute('popover', 'manual');

      var inner = document.createElement('div');
      inner.className = 'hover-preview-card';

      thumb = document.createElement('img');
      thumb.className = 'hover-preview-thumb';
      thumb.setAttribute('alt', '');
      thumb.setAttribute('decoding', 'async');
      thumb.setAttribute('loading', 'lazy');
      thumb.setAttribute('width', '240');
      thumb.setAttribute('height', '320');
      inner.appendChild(thumb);

      var textWrap = document.createElement('div');
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
      if (left < pad) left = pad;
      if (left > maxLeft) left = maxLeft;
      if (top + rc.height > window.innerHeight - pad) {
        top = rt.top - rc.height - pad;
      }
      card.style.top  = top  + 'px';
      card.style.left = left + 'px';
    }

    function open(trigger) {
      ensureCard();
      var src = trigger.getAttribute('data-hover-preview');
      if (thumb.getAttribute('src') !== src) thumb.setAttribute('src', src);
      titleEl.textContent   = trigger.getAttribute('data-hover-title')   || '';
      captionEl.textContent = trigger.getAttribute('data-hover-caption') || '';
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

    Array.prototype.forEach.call(triggers, attach);
  }());

})();
