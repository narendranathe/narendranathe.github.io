(function () {
  const config = window.PORTFOLIO_CONFIG;

  if (!config) {
    return;
  }

  function homeAwareHref(href, page) {
    if (!href.startsWith("#")) {
      return href;
    }

    return page === "home" ? href : `index.html${href}`;
  }

  function renderHeader() {
    const mount = document.querySelector("[data-site-header]");

    if (!mount) {
      return;
    }

    const page = document.body.dataset.page || "home";
    const active = document.body.dataset.nav || "";

    const navLinks = config.navigation
      .map((item) => {
        const href = homeAwareHref(item.href, page);
        const activeClass = active === item.label.toLowerCase() ? " is-active" : "";
        return `<a class="site-nav__link${activeClass}" href="${href}">${item.label}</a>`;
      })
      .join("");

    mount.innerHTML = `
      <div class="container site-header__inner">
        <a class="brand" href="${config.links.home}">
          <span class="brand__name">${config.identity.name}</span>
          <span class="brand__role">${config.identity.role}</span>
        </a>
        <button class="menu-toggle" type="button" aria-expanded="false" aria-label="Toggle navigation">
          <span></span>
        </button>
        <nav class="site-nav" aria-label="Primary navigation">
          <div class="site-nav__links">${navLinks}</div>
          <div class="site-nav__actions">
            <a class="button button--small button--ghost" href="${config.links.linkedin}" target="_blank" rel="noreferrer">LinkedIn -></a>
            <a class="button button--small button--primary" href="${config.links.resume}" target="_blank" rel="noreferrer">Resume -></a>
          </div>
        </nav>
      </div>
    `;
  }

  function renderFooter() {
    const mount = document.querySelector("[data-site-footer]");

    if (!mount) {
      return;
    }

    const links = config.contactLinks
      .map(
        (item) =>
          `<a class="text-link" href="${item.href}" ${
            item.href.startsWith("mailto:") ? "" : 'target="_blank" rel="noreferrer"'
          }>${item.label}${item.href.startsWith("mailto:") ? "" : " ->"}</a>`
      )
      .join("");

    mount.innerHTML = `
      <div class="container site-footer__inner">
        <p class="site-footer__copy">${config.identity.footerStatement}</p>
        <div class="site-footer__links">${links}</div>
      </div>
    `;
  }

  function setupMenu() {
    const toggle = document.querySelector(".menu-toggle");
    const nav = document.querySelector(".site-nav");
    const header = document.querySelector(".site-header__inner");

    if (!toggle || !nav || !header) {
      return;
    }

    function closeMenu() {
      toggle.setAttribute("aria-expanded", "false");
      nav.classList.remove("is-open");
    }

    toggle.addEventListener("click", function () {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      nav.classList.toggle("is-open", !isOpen);
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", function () {
        closeMenu();
      });
    });

    document.addEventListener("click", function (event) {
      if (!nav.classList.contains("is-open")) {
        return;
      }

      if (header.contains(event.target)) {
        return;
      }

      closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu();
      }
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 760) {
        closeMenu();
      }
    });
  }

  function setupExpansions() {
    document.querySelectorAll(".expand-toggle").forEach((button) => {
      button.addEventListener("click", function () {
        const card = button.closest(".system-card");

        if (!card) {
          return;
        }

        const isOpen = card.classList.toggle("is-open");
        button.setAttribute("aria-expanded", String(isOpen));
        button.textContent = isOpen ? "Collapse detail" : "Expand detail";
      });
    });
  }

  function setupReveals() {
    const items = document.querySelectorAll("[data-reveal]");

    if (!items.length || !("IntersectionObserver" in window)) {
      items.forEach((item) => item.classList.add("is-visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.15,
        rootMargin: "0px 0px -5% 0px"
      }
    );

    items.forEach((item) => observer.observe(item));
  }

  function setupMetricCounts() {
    const numbers = document.querySelectorAll("[data-count]");

    if (!numbers.length || !("IntersectionObserver" in window)) {
      return;
    }

    const animate = (el) => {
      const target = Number(el.dataset.count);

      if (!Number.isFinite(target)) {
        return;
      }

      const duration = 900;
      const start = performance.now();

      function frame(now) {
        const progress = Math.min((now - start) / duration, 1);
        el.textContent = Math.floor(progress * target).toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(frame);
        } else {
          el.textContent = target.toLocaleString();
        }
      }

      requestAnimationFrame(frame);
    };

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            animate(entry.target);
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.4 }
    );

    numbers.forEach((number) => observer.observe(number));
  }

  document.addEventListener("DOMContentLoaded", function () {
    renderHeader();
    renderFooter();
    setupMenu();
    setupExpansions();
    setupReveals();
    setupMetricCounts();
  });
})();
