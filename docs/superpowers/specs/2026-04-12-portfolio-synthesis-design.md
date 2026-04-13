# Portfolio Synthesis Design

## Goal

Create a third portfolio branch that combines the strongest parts of:

- `feat/portfolio-rebuild-system-map`
- `feat/ai-platform-portfolio-refresh`
- `main`

The result should feel like a senior engineer portfolio, not a resume dump and not a design experiment. It should improve recruiter scan speed, technical credibility, and search discoverability for high-paying US roles in:

- senior AI platform engineering
- applied AI engineering
- backend AI systems
- AI infrastructure
- AI product engineering with strong platform ownership

## Branch Strategy

Build this hybrid on a dedicated branch from `main`.

This branch is the merge candidate that should eventually go back to `main`, not another side experiment layered on top of the earlier redesign branches.

## Primary Outcome

The homepage should communicate in under 10 seconds:

1. Narendranath Edara builds production AI systems.
2. The work spans enterprise AI platforms, AI-powered workflow products, and reusable engines.
3. The strongest proof is ExponentHR, AutoApply AI, and tailor-resume.
4. The visitor can immediately inspect deeper technical proof through expandable sections and case-study pages.

## Audience

Primary:

- recruiters
- hiring managers

Secondary:

- engineering leaders
- senior ICs evaluating technical depth

The site should optimize for recruiter scan speed first, then technical depth through progressive disclosure.

## Hiring Signal Mode

Use a balanced hiring mode.

That means:

- the site should stay portfolio-first, not job-board-first
- the hero should not read like an `open to work` banner
- the current-focus strip and supporting proof should still make target role fit obvious

Role fit should be implied through precise system language and current-focus copy rather than explicit pleading for attention.

## Core Positioning

The site should tell one narrow story:

**I build production-grade LLM applications, retrieval-backed workflow products, and safe, reliable AI systems with strong platform, data, and deployment foundations.**

This phrasing should be reflected in:

- the page title
- the visible hero headline
- the hero supporting copy
- section labels
- system descriptions

Avoid generic marketing phrases like:

- cutting-edge AI solutions
- passionate about AI
- innovative problem solver
- results-driven
- end-to-end solutions

## Branch Synthesis Decision

Use a **hybrid synthesis**.

### Keep From `feat/portfolio-rebuild-system-map`

- sticky minimal top header with name and role
- typography system
- strong spacing and architectural layout
- rectangular proof and system cards
- expandable system detail pattern
- dedicated case-study page structure

### Keep From `feat/ai-platform-portfolio-refresh`

- stronger recruiter-facing narrative
- current-focus proof bullets in the hero
- green and gold accent direction
- clearer `Selected Systems` framing
- stronger modular story around AutoApply AI, tailor-resume, and JobScout
- compact icon-led proof lines that make the page feel active and current

### Keep From `main`

- the strongest concrete system descriptions
- the most credible impact statements
- keyword-rich but still human-readable technical wording
- the clearest explanation of ExponentHR, AutoApply AI, JobScout, and tailor-resume

## Visual Direction

The design should remain:

- minimal
- calm
- technical
- premium without luxury cliches
- bold through typography and composition rather than decoration
- resume-forward through accent use and placement without becoming visually loud

### Keep

- sticky top header
- serif display + clean sans body + mono support font
- forest green and warm gold accent palette
- rectangular blocks and split sections
- resume CTA kept persistently visible in the header with green/gold emphasis

### Avoid

- vague decorative labels
- fragile or broken stats widgets
- weak screenshots that do not prove real work
- repeating the same proof three different ways on the homepage

## Visual Proof Strategy

Do not force screenshots where they are weak or unavailable.

### System Treatments

- `ExponentHR`: abstract system visual or architecture-style treatment
- `AutoApply AI`: abstract system visual plus product/logo treatment
- `tailor-resume`: abstract or light badge/logo treatment
- `JobScout`: supporting abstract treatment only

### Rationale

Current repo-adjacent assets do not provide strong, credible screenshot proof for all systems. The homepage should use polished abstract system visuals instead of weak dashboard crops or hotlinked assets that may break.

## Information Architecture

### Homepage Order

1. Hero
2. Measured impact
3. Selected systems
4. How I build
5. Experience
6. Credentials and signals
7. Engineering notes
8. Contact

Use these exact homepage labels:

- `Measured impact`
- `Selected systems`
- `How I build`
- `Experience`
- `Credentials and signals`
- `Engineering notes`
- `Contact`

### Deep-Dive Pages

Keep and refine:

- `exponenthr.html`
- `autoapply-ai.html`
- `tailor-resume.html`

JobScout should stay as supporting system proof on the homepage unless a dedicated page is added later.

## Section Design

### 1. Hero

Purpose:

- establish role fit immediately
- match high-signal current AI platform hiring language
- create a fast path into systems proof

Layout:

- use the `system-map` branch shell and sticky header
- retain large typography
- keep a right-side structured panel

Content direction:

- Eyebrow:
  `Senior AI Platform Engineer`
- Recommended headline:
  `Production-grade AI systems for retrieval, workflow automation, and reliable delivery.`
- Recommended supporting copy:
  `I build enterprise AI platforms, AI-powered workflow products, and reusable backend engines with measurable impact across retrieval, inference, secure data access, deployment, and product reliability.`
- Include a compact current-focus strip derived from refresh with three short icon-led lines:
  - `ExponentHR`: catalog-driven NL-to-SQL platform on Microsoft Fabric for 400 enterprise clients
  - `AutoApply AI`: discover -> tailor -> apply -> track workflow product across FastAPI and Chrome MV3
  - `Modular engines`: tailoring core and discovery engine extracted so the product could evolve like a platform

The hero copy should use the stronger proof style from `main`, not the weaker abstract phrasing from `feat/portfolio-rebuild-system-map`.

### 2. Right-Side Hero Panel

Replace `Proof frame` with a recruiter-safe label.

Recommended label:

- `Measured impact`

This panel is part of the hero, not a separate homepage section.

Panel structure:

- `400 enterprise clients`
- `6K+ HR catalog columns`
- `11 ATS adapters + 6 model providers`
- `190 tests in tailoring core`

This should read like operational proof, not self-promotion.

Do not use phrases like:

- `proof frame`
- `true ownership`
- `supporting trust`
- `inspect the work, then reach out`

### 3. Measured Impact

Keep the split rectangular structure from `system-map`.

Left column:

- business outcomes
- onboarding speed
- runtime or operational outcomes

Right column:

- retrieval and inference architecture
- workflow platform architecture
- reusable engine distribution surfaces

This section should preserve the visual design from `system-map` but use the sharper content and metrics from `main`.

### 4. Selected Systems

Use this as the main homepage section title.

Top three anchor systems:

1. ExponentHR
2. AutoApply AI
3. tailor-resume

Supporting system:

- JobScout

Card structure:

- left rail with one clear system category and one metric
- short description with high-signal platform language
- skill/tag row
- expandable detail
- case-study link
- repo link where appropriate

JobScout should be presented as a supporting system beneath the primary three, not as an equal flagship system.

### 5. How I Build

Rename this section to:

- `How I build`

Add a compact section or subsection that describes operating style instead of generic biography.

Themes:

- architecture design decisions
- safe, reliable AI systems
- measurable outcomes
- platform ownership across retrieval, APIs, storage, deployment, and product behavior

This replaces softer "about me" framing with recruiter-relevant engineering identity.

### 6. Experience

Keep this section on the homepage, but make it more useful.

Collapsed card:

- role
- company
- dates
- one-line scope statement
- 3 proof bullets: architecture, scale, impact

Expanded card:

- system boundary
- major technical choices and tradeoffs
- measurable production outcome
- tightly scoped stack tags

This section should assume the recruiter has already seen the resume and wants deeper context, not repeated bullet spam.

Recommended rule:

- homepage card should go deeper than the resume, but only one level deeper
- detailed architecture lives on the system cards and case-study pages
- experience cards should explain the role context behind the strongest systems

### 7. Credentials and Signals

Replace `Supporting trust` with:

- `Credentials and signals`

Keep it short and calm.

Include:

- Taylor & Francis publication
- key certification(s)
- one recommendation if it reads senior and specific

This section should support the systems story rather than compete with it.

### 8. Engineering Notes

Keep the writing section, but rename it:

- `Engineering notes`

Reason:

- sounds more serious and more relevant to hiring managers than simply `Writing`

Focus the three note cards on:

- browser automation / ATS architecture
- multi-model or provider strategy
- production lessons from AI workflows

### 9. Contact

Keep the final section label as:

- `Contact`

Reason:

- this is faster for recruiter scanning than a softer label

Keep it simple and compact.

Email, LinkedIn, GitHub, and Substack are enough.

Resume should remain visible both:

- in the sticky header
- in the final contact block

## Content Sourcing Rules

### ExponentHR

Use the strongest language from `main` and refresh:

- catalog-driven NL-to-SQL
- Microsoft Fabric
- FAISS retrieval
- governed T-SQL generation
- semantic joins
- 400 enterprise clients

### AutoApply AI

Use the stronger refresh framing:

- discover -> tailor -> apply -> track
- FastAPI
- Chrome MV3
- retrieval-backed answers
- model routing
- live deployments

### tailor-resume

Emphasize extracted engine identity:

- reusable tailoring core
- CLI, Streamlit, MCP, PyPI, hosted APIs
- test coverage as quality proof

### JobScout

Frame as:

- discovery and ranking engine feeding the broader workflow platform

## Media Rules

Use real screenshots or short motion only when they improve credibility.

Preferred order:

1. real product screenshot or short clip if it is clean and obviously yours
2. architecture-style visual that explains the system
3. abstract visual treatment

Do not add filler media just to make a card look richer.

## SEO And Discoverability

Use current Google guidance:

- keep a concise, descriptive, unique page title
- ensure H1 closely matches the title
- keep visible page text aligned with title and metadata
- avoid keyword stuffing
- preserve crawlable anchor links
- keep sitemap and robots in place

Title direction:

- `Narendranath Edara | Senior AI Platform Engineer`

The homepage content should include real role language such as:

- production-grade LLM applications
- AI-powered workflows
- retrieval
- inference
- evaluation
- reliability
- observability
- secure data access
- architecture design decisions
- measurable impact

## Non-Goals

Do not:

- add badge walls or noisy decorative proof
- add broken GitHub stats widgets
- add shallow screenshots for the sake of visuals
- make the homepage feel like a resume clone
- overload the hero with too many competing claims

## Implementation Scope

Primary files likely affected:

- `index.html`
- `config.js`
- `styles.css`
- `app.js`

Possible refinement targets after homepage:

- `exponenthr.html`
- `autoapply-ai.html`
- `tailor-resume.html`

## Success Criteria

The new homepage is successful if:

1. the top screen immediately communicates role fit for senior AI platform roles
2. the strongest systems are obvious without scrolling through resume-like content
3. section labels sound credible and deliberate
4. the visual system remains distinctive and premium
5. the copy is stronger for recruiters without losing technical honesty
6. search-facing title and homepage language are aligned and clear
