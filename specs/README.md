# Project Design Decisions

This file is the persistent log of project-level design decisions for this repo. Append new decisions after each session so the reasoning behind the site stays visible over time.

## 2026-04-11

### Systems-first portfolio structure

- The portfolio should read like a senior engineer systems portfolio, not a resume dump.
- The homepage should prioritize recruiter scan speed before deep technical exploration.
- The top header should stay visible while scrolling and keep the identity surface minimal: name, role, and high-value navigation.
- Large typography should do the primary visual work instead of heavy decoration.
- Project storytelling should use rectangular proof blocks, visible architecture framing, and dedicated case-study pages for deeper reading.

## 2026-04-12

### Hybrid synthesis direction

- The merge-candidate portfolio should combine the strongest parts of `main`, `feat/ai-platform-portfolio-refresh`, and `feat/portfolio-rebuild-system-map`.
- The visual shell should stay calm, premium, and technical, using the stronger typography and sticky header from the `system-map` branch.
- Homepage copy should be proof-heavy and recruiter-readable, using the stronger project content from `main` instead of vague abstract labels.
- The hero should stay portfolio-first while still making role fit obvious for Senior AI Platform Engineer, Applied AI, and Backend AI roles.
- A concise current-focus strip should make active work visible without turning the page into an `open to work` banner.
- Green and gold accents should highlight the resume path and key proof points without overpowering the page.
- The homepage should foreground three flagship systems: ExponentHR, AutoApply AI, and `tailor-resume`.
- Experience sections should go deeper than resume bullets by adding expandable technical context for recruiters and hiring managers who want more detail.
- Section names should sound credible and direct; vague labels such as `Supporting trust` or `Selected experience` should be replaced with explicit recruiter-facing language.

### Visual proof integration

- Real local visuals should be used when they strengthen recognition and credibility, especially for flagship products and prior employers.
- The homepage now uses the AutoApply AI product graphic as system proof instead of leaving that project text-only.
- Missouri S&T and Zomato marks should appear in the experience section so prior work history is easier to scan visually.
- ExponentHR should stay text-and-architecture-led until a safe company-approved visual is available; do not invent fake product screenshots.
- A resume screenshot should not be used as the top hero image in place of a real portrait or headshot.

### Above-the-fold visual credibility

- The hero should not rely on text alone to prove seniority; it should show at least one flagship product visual and recognizable work-history marks near the top of the page.
- The right-side proof rail now mixes product imagery, employer context, and measured outcomes so recruiters can form trust before they start reading deeper sections.
- Case-study pages should reuse safe visual assets when available so the homepage, experience section, and deep-dive pages reinforce the same system story.

## Repo Index

<!-- AUTO:REPO_INDEX_START -->
### What this repo does

- Personal portfolio site for Narendranath Edara, a Senior AI Platform Engineer focused on production LLM systems, retrieval pipelines, governed analytics, and backend AI infrastructure. This repository is the public source for my portfolio and career positioning. It is intentionally aligned to the roles I am targeting:

### Ubiquitous language

- Primary glossary file: `UBIQUITOUS_LANGUAGE.md`
- Keep repo terms stable across specs, implementation, and recruiter-facing copy.
<!-- AUTO:REPO_INDEX_END -->


## Session Checkpoints

### 2026-04-13 08:21 - post-compact

- Branch: `feat/portfolio-synthesis-v3`
- Last commit: `chore(specs): localize superpowers docs`
- Working changes: pp.js, autoapply-ai.html, config.js, exponenthr.html, index.html, specs/README.md, styles.css, tailor-resume.html

### 2026-04-13 08:22 - session-end

- Branch: `feat/portfolio-synthesis-v3`
- Last commit: `chore(specs): localize superpowers docs`
- Working changes: pp.js, autoapply-ai.html, config.js, exponenthr.html, index.html, specs/README.md, styles.css, tailor-resume.html

### 2026-04-13 08:22 - session-end

- Branch: `feat/portfolio-synthesis-v3`
- Last commit: `chore(specs): localize superpowers docs`
- Working changes: app.js, autoapply-ai.html, config.js, exponenthr.html, index.html, specs/README.md, styles.css, tailor-resume.html

### 2026-04-13 08:30 - session-end

- Branch: `feat/portfolio-synthesis-v3`
- Last commit: `chore(specs): localize superpowers docs`
- Working changes: app.js, autoapply-ai.html, config.js, exponenthr.html, index.html, specs/README.md, styles.css, tailor-resume.html
