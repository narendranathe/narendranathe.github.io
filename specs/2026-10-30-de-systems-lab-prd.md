# PRD: Data Engineering Systems Lab

**Status:** Implemented as reviewable MVP on \`feat/de-systems-lab\`
**Date:** 2026-10-30
**Product owner:** Portfolio owner
**Proposed URL:** https://narendranathe.github.io/de-lab/
**Source inspiration:** https://dhruvtechbytes.com/ (information architecture and interactive teaching pattern; original branding, text, UI assets, and implementations)

## 1. Problem statement
A static resume or project list shows outcomes but does not demonstrate the decisions, trade-offs, failure handling, or correctness thinking behind dependable data systems. Engineering hiring managers need to see both shipped results and how the builder reasons under failure.

## 2. Job to be done
When evaluating a data/platform engineer, a visitor can interact with miniature, transparent simulations of operational failure modes, understand a bounded real-world outcome, and navigate back to full project evidence in less than three minutes.

## 3. Personas and intended actions
- **Engineering recruiter:** Understand the role and verified impact quickly; open the existing portfolio.
- **Data platform engineer:** Test failure modes; see incremental-versus-full trade-offs; examine data contracts.
- **Hiring manager:** Distinguish production outcomes from educational simulations; follow a project case study.

## 4. Goals and non-goals
**Goals:** Independent path without breaking root portfolio; mobile-responsive experience; no backend or secret keys; usable keyboard navigation; two working simulations; no unsupported commercial offers or endorsements; deterministic unit tests and deployment instructions.

**Non-goals:** Cloning another creator's text, imagery, prices or course/mentor identity; collecting user data; running real CDC, Spark, or cloud infrastructure; promising courses/recordings; modifying the existing main-site homepage.

## 5. MVP features
| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| F01 | P0 | Self-contained static page at \`/de-lab/\` | Browser serves HTML and local assets without build or package install |
| F02 | P0 | Distinctive narrative and architecture visualization | Hero, pipeline diagram, measurable outcomes, systems map, evidence and CTA |
| F03 | P0 | CDC simulation | Controls for mode, input volume, disruption; metrics and step trace update coherently |
| F04 | P0 | Data quality simulation | Clean, duplicate-grain and sentinel-value datasets; explicit data contract failures |
| F05 | P0 | Truthfulness | All simulator metrics identified as synthetic; actual career metrics identified as reported outcomes |
| F06 | P0 | Navigation | Skip link, anchored sections, accessible focus styles, mobile nav; no dead CTAs |
| F07 | P0 | Isolation | Root \`index.html\`, CSS and JS are not modified |
| F08 | P0 | Core tests | \`node --test de-lab/tests/core.test.cjs\` passes |
| F09 | P1 | Curriculum-style systems map | Six learning modules, accessible native accordion details |
| F10 | P1 | Search and share metadata | Unique title, canonical URL, OG description and image (existing site image) |

## 6. Product hypotheses and success measures
**Hypothesis:** An interactive system demonstration is more persuasive than an additional generic project card.

Track only after explicit analytics design/review: visits to /de-lab/, simulator start and completion rates, clickthrough to portfolio/case studies, mobile engagement and user-reported comprehension. No collection or claims in MVP. Initial target: meaningful demonstration in under 3 minutes; all ten core test cases pass; zero broken internal links.

## 7. Experience map
Top announcement -> sticky navigation -> hero with pipeline diagram -> real outcome strip -> why observability/correctness matters -> interactive CDC + data quality labs -> design systems map -> project evidence -> FAQs -> strong portfolio CTA.

Visual direction: dark midnight canvas, off-white typography, electric lime accent, monospaced technical labels, deep cards and system diagrams. The page is an original interpretation of the reference's high-contrast, product-led, interactive educational approach.

## 8. Architecture and decisions
- **ADR-01 / Static hosting:** Keep HTML + CSS + vanilla JavaScript to match the repository and GitHub Pages deployment. No extra repo, build system, framework or server.
- **ADR-02 / Simulation engine:** Place deterministic, pure simulation logic in \`de-lab/core.js\`. UI consumes a browser global; Node's native test runner consumes CommonJS, avoiding npm.
- **ADR-03 / Safety and privacy:** All data is synthetic, local and client-side. No forms, signups, telemetry, third-party API calls or storage of visitor inputs.
- **ADR-04 / Deployment:** Create PR for review. Existing \`.github/workflows/deploy.yml\` publishes the repository root on \`main\`, including \`de-lab/\`; merge is required before public Pages deployment.
- **ADR-05 / Product differentiation:** No third-party trademarks as branding, no misrepresentation of instructor/course ownership, no reused logos or creative assets.

## 9. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Reference copyrighted content | Recreate design patterns with original copy and UI, not one-to-one code or asset copying |
| Synthetic numbers mistaken for production | Label simulations at module, panel and result level |
| Broken GitHub Pages relative paths | Use relative \`./\` assets, \`../\` portfolio links and explicit canonical URL |
| Portfolio outage from release | Work in separate directory on feature branch; deploy after PR merge |
| Accessibility regressions | Native buttons, labels, details, skip link, status regions and reduced-motion support |

## 10. Test and release plan
1. Run \`node --test de-lab/tests/core.test.cjs\` (native Node, no dependencies).
2. Validate page anchors, script/style references, responsive viewports and keyboard controls in a browser.
3. Review security (no secrets, no visitor data capture, no innerHTML from untrusted inputs).
4. Merge PR only after visual and mobile review.
5. Verify \`https://narendranathe.github.io/de-lab/\` after the existing Pages workflow completes.

## 11. Future product increments
- Phase 2: Interactive lineage graph and replayable incident scenarios with shareable state.
- Phase 3: Accessible editor for SQL/data contracts with local-only checks.
- Phase 4: Optional original articles, real GitHub project evidence and analytics with consent-aware measurement.

**Definition of done:** Two useful deterministic simulators, responsive DE narrative, clear actual-versus-synthetic labels, passing Node unit tests, and a reviewable PR that touches no existing homepage files.
