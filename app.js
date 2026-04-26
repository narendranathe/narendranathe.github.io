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

})();
