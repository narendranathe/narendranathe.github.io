/**
 * app.js - Portfolio site for Narendranath Edara
 * Vanilla ES6+, no frameworks. Works with window.PORTFOLIO_CONFIG from config.js.
 *
 * Security note: all innerHTML assignments in this file use exclusively
 * developer-controlled static strings (no user input, no external data).
 * Content is hardcoded or comes from the trusted PORTFOLIO_CONFIG object
 * authored by the site owner. No sanitization library is required.
 */
(function () {
  'use strict';

  const CONFIG = window.PORTFOLIO_CONFIG || {};
  const RESUME_URL =
    'https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf';
  const LINKEDIN_URL = 'https://www.linkedin.com/in/narendranathe/';

  /** Escape a string for safe use inside an HTML attribute value. */
  function escAttr(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  /** Escape a string for safe use as HTML text content. */
  function escText(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  // ---------------------------------------------------------------------------
  // renderHeader
  // ---------------------------------------------------------------------------
  /**
   * Renders the site header into [data-site-header].
   * Nav links come from CONFIG.navigation; falls back to hardcoded defaults.
   */
  function renderHeader() {
    const root = document.querySelector('[data-site-header]');
    if (!root) return;

    const navLinks = CONFIG.navigation || [
      { label: 'Systems', href: '#systems' },
      { label: 'Experience', href: '#experience' },
      { label: 'Notes', href: '#notes' },
      { label: 'Connect', href: '#connect' },
    ];

    // Build nav link HTML from trusted config values (escaped for safety)
    const linkHTML = navLinks
      .map(
        ({ label, href }) =>
          `<a class="site-nav__link" href="${escAttr(href)}">${escText(label)}</a>`
      )
      .join('\n      ');

    // All URLs and text below are developer-controlled static values
    root.innerHTML = `
<div class="container site-header__inner">
  <a class="brand" href="/">
    <span class="brand__name">Narendranath Edara</span>
    <span class="brand__role">Senior AI Platform Engineer</span>
  </a>
  <button class="menu-toggle" type="button" aria-expanded="false" aria-label="Toggle navigation">
    <span></span>
  </button>
  <nav class="site-nav" aria-label="Primary navigation">
    <div class="site-nav__links">
      ${linkHTML}
    </div>
    <div class="site-nav__actions">
      <a class="button--small button--ghost" href="${escAttr(LINKEDIN_URL)}" target="_blank" rel="noreferrer">LinkedIn -&gt;</a>
      <a class="button--small button--resume" href="${escAttr(RESUME_URL)}" target="_blank" rel="noreferrer">Resume -&gt;</a>
    </div>
  </nav>
</div>`;
  }

  // ---------------------------------------------------------------------------
  // renderFooter
  // ---------------------------------------------------------------------------
  /**
   * Renders the site footer into [data-site-footer].
   * All content is static and developer-controlled.
   */
  function renderFooter() {
    const root = document.querySelector('[data-site-footer]');
    if (!root) return;

    // Static developer-controlled markup - no user input involved
    root.innerHTML = `
<div class="container site-footer__inner">
  <p class="site-footer__copy">Senior AI platform engineering across retrieval, workflow automation, reusable engines, and production delivery.</p>
  <div class="site-footer__links">
    <a class="text-link" href="mailto:edara.narendranath@gmail.com">Email</a>
    <a class="text-link" href="${escAttr(LINKEDIN_URL)}" target="_blank" rel="noreferrer">LinkedIn -&gt;</a>
    <a class="text-link" href="https://github.com/narendranathe" target="_blank" rel="noreferrer">GitHub -&gt;</a>
    <a class="text-link" href="https://narendranathe.substack.com" target="_blank" rel="noreferrer">Substack -&gt;</a>
  </div>
</div>`;
  }

  // ---------------------------------------------------------------------------
  // setupMobileMenu
  // ---------------------------------------------------------------------------
  /**
   * Wires the mobile hamburger toggle.
   * Closes on ESC, outside click, nav link click, and window resize > 760px.
   */
  function setupMobileMenu() {
    const toggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('.site-nav');
    if (!toggle || !nav) return;

    function openMenu() {
      nav.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
    }

    function closeMenu() {
      nav.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', () => {
      nav.classList.contains('is-open') ? closeMenu() : openMenu();
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeMenu();
    });

    document.addEventListener('click', (e) => {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) closeMenu();
    });

    nav.querySelectorAll('.site-nav__link').forEach((link) => {
      link.addEventListener('click', closeMenu);
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 760) closeMenu();
    });
  }

  // ---------------------------------------------------------------------------
  // setupExpansions
  // ---------------------------------------------------------------------------
  /**
   * Handles expand/collapse for .system-card and .track-card via .expand-btn.
   * System card button text: "See architecture" <-> "Hide architecture"
   * Track card button text:  "Read the deep dive" <-> "Close deep dive"
   */
  function setupExpansions() {
    document.querySelectorAll('.expand-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const systemCard = btn.closest('.system-card');
        const trackCard = btn.closest('.track-card');
        const card = systemCard || trackCard;
        if (!card) return;

        const isOpen = card.classList.toggle('is-open');
        btn.setAttribute('aria-expanded', String(isOpen));

        if (systemCard) {
          btn.textContent = isOpen ? 'Hide architecture' : 'See architecture';
        } else {
          btn.textContent = isOpen ? 'Close deep dive' : 'Read the deep dive';
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // setupReveals
  // ---------------------------------------------------------------------------
  /**
   * IntersectionObserver-based scroll reveal for all [data-reveal] elements.
   * Adds .is-visible on entry; falls back to immediate add if IO unavailable.
   * rootMargin: "0px 0px -5% 0px", threshold: 0.12.
   */
  function setupReveals() {
    const elements = document.querySelectorAll('[data-reveal]');
    if (!elements.length) return;

    if (!('IntersectionObserver' in window)) {
      elements.forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -5% 0px' }
    );

    elements.forEach((el) => observer.observe(el));
  }

  // ---------------------------------------------------------------------------
  // setupMetricCounts
  // ---------------------------------------------------------------------------
  /**
   * Animates [data-count] elements from 0 to their numeric target over 900ms.
   * Uses ease-out cubic easing. Triggered once per element via IntersectionObserver
   * at threshold 0.4.
   */
  function setupMetricCounts() {
    const elements = document.querySelectorAll('[data-count]');
    if (!elements.length) return;

    function animateCount(el) {
      const target = parseFloat(el.dataset.count);
      const duration = 900;
      const start = performance.now();

      function tick(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        el.textContent = Math.round(eased * target).toLocaleString();
        if (progress < 1) requestAnimationFrame(tick);
      }

      requestAnimationFrame(tick);
    }

    if (!('IntersectionObserver' in window)) {
      elements.forEach(animateCount);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );

    elements.forEach((el) => observer.observe(el));
  }

  // ---------------------------------------------------------------------------
  // setupScrollProgress
  // ---------------------------------------------------------------------------
  /**
   * Injects a fixed top progress bar (#scroll-progress) that fills 0-100%
   * as the user scrolls. Green-to-gold gradient, 3px tall. RAF-throttled.
   */
  function setupScrollProgress() {
    const bar = document.createElement('div');
    bar.id = 'scroll-progress';
    Object.assign(bar.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '0%',
      height: '3px',
      background: 'linear-gradient(90deg, #22c55e, #eab308)',
      zIndex: '9999',
      pointerEvents: 'none',
      transition: 'width 0.1s linear',
    });
    document.body.prepend(bar);

    let ticking = false;

    function updateBar() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      const docHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width = pct.toFixed(2) + '%';
      ticking = false;
    }

    window.addEventListener(
      'scroll',
      () => {
        if (!ticking) {
          requestAnimationFrame(updateBar);
          ticking = true;
        }
      },
      { passive: true }
    );
  }

  // ---------------------------------------------------------------------------
  // setupActiveNavHighlight
  // ---------------------------------------------------------------------------
  /**
   * Watches section visibility and toggles .is-active on matching nav links.
   * Tracks: #systems, #experience, #notes, #connect at threshold 0.3.
   */
  function setupActiveNavHighlight() {
    const sectionIds = ['systems', 'experience', 'notes', 'connect'];
    const sections = sectionIds
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (!sections.length) return;

    const navLinks = document.querySelectorAll('.site-nav__link');

    function setActive(id) {
      navLinks.forEach((link) => {
        link.classList.toggle('is-active', link.getAttribute('href') === '#' + id);
      });
    }

    if (!('IntersectionObserver' in window)) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActive(entry.target.id);
          }
        });
      },
      { threshold: 0.3 }
    );

    sections.forEach((section) => observer.observe(section));
  }

  // ---------------------------------------------------------------------------
  // Boot
  // ---------------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    renderHeader();
    renderFooter();
    setupMobileMenu();
    setupExpansions();
    setupReveals();
    setupMetricCounts();
    setupScrollProgress();
    setupActiveNavHighlight();
  });
})();
