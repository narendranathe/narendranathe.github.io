# Portfolio Rebuild Design

## Goal

Rebuild the portfolio as a minimal, architectural, recruiter-friendly site that communicates in under 10 seconds:

- Narendranath Edara builds production AI systems.
- The work spans enterprise AI platforms, workflow products, and reusable engines.
- The strongest proof is ExponentHR, AutoApply AI, and tailor-resume.
- The site should feel calm, precise, modern, and senior rather than flashy or generic.

## What Is Wrong With The Current Order

The current order is not fundamentally wrong. It is a normal portfolio structure:

`about -> experience -> credentials -> projects -> social -> contact`

The problem is that it behaves more like a resume page than a high-conviction product surface.

For recruiters:

- it delays the strongest proof
- it makes "who I am" arrive before "why I am different"
- it asks the visitor to read before they can scan

For engineering leaders:

- it delays architecture depth and measurable system ownership
- it makes case studies compete with supporting material like certifications or recommendations
- it does not create a fast path from outcome -> system -> artifact

The better ordering for this portfolio is:

`thesis -> proof -> flagship systems -> deeper case studies -> supporting trust -> contact`

That does not remove "about" or "experience." It reframes them as support for the work, not as the main event.

## Audience

Primary:

- recruiters
- hiring managers

Secondary:

- engineering leaders
- senior ICs evaluating technical depth

The first screen must answer:

1. What does this person build?
2. Is the work real and production-grade?
3. Where can I inspect the strongest proof?

## Core Story

The site should tell one narrow story:

**I build production AI systems with measurable outcomes, strong system boundaries, and reusable product surfaces.**

That story should be expressed through three headline proofs:

1. **ExponentHR**
   Enterprise AI platform proof. Catalog-driven NL-to-SQL, retrieval, semantic joins, governed SQL generation, and hot-reload onboarding at enterprise scale.

2. **AutoApply AI**
   Flagship workflow product proof. Discover -> tailor -> apply -> track across Chrome MV3, FastAPI, PostgreSQL, Redis, model routing, and live deployments.

3. **tailor-resume**
   Reusable engine proof. Extracted tailoring core shipped across CLI, Streamlit, MCP, PyPI, and hosted API surfaces with strong test coverage.

Supporting proof:

- **JobScout** as discovery, ranking, and alerts engine
- **fraud-detection-ml-platform** as ML infra and observability proof
- **portfolio-risk-analysis** as secondary systems demo

## Design Direction

### Tone

- minimal
- architectural
- premium without luxury cliches
- technical without looking like a dashboard
- serious and calm rather than loud

### Visual Principles

- use large, disciplined spacing
- create strong grid logic
- use contrast through density and scale, not excessive decoration
- let the typography and layout carry authority
- use motion only for orientation, emphasis, and expansion

### Avoid

- generic startup gradients
- purple-on-white AI aesthetic
- crowded card grids
- oversized badge walls
- too many unrelated sections on the homepage
- repeating the same proof in hero, achievements, and projects

## Color System

Use a quiet architectural palette.

### Core Colors

- Background: `#F6F4EF`
- Surface: `#FBF9F5`
- Elevated surface: `#FFFFFF`
- Primary text: `#171614`
- Secondary text: `#5C5A54`
- Muted text: `#8E8A82`
- Hairline border: `#DDD8CF`

### Accent Colors

- Forest primary: `#1F4D43`
- Forest hover: `#2C6659`
- Warm stone accent: `#B78A58`
- Soft moss wash: `#E8EFEA`
- Case-study ink blue: `#21344A`

### Usage Rules

- Use forest for main calls to action and key highlights.
- Use warm stone sparingly for metrics, labels, and small moments of contrast.
- Use moss wash as a background tint for selected architectural blocks.
- Use blue only inside technical proof contexts like diagrams or architecture labels.

## Typography

Typography should feel editorial-technical rather than SaaS-generic.

- Display: elegant serif or high-character display face
- Body: highly readable sans-serif
- Mono: reserved for metrics, commands, and architecture labels

Recommended pairing:

- Display: `Playfair Display` or another refined serif already in use
- Body: `Source Sans 3`
- Mono: `JetBrains Mono`

Rules:

- large, assertive hero headline
- shorter paragraphs
- section intros should be 1-2 sentences max
- use mono for command snippets, system labels, and metrics

## Information Architecture

The portfolio should be rebuilt as a **hybrid homepage + deep-dive case study system**.

### Homepage Order

1. Hero
2. Split proof section
3. System map / flagship systems
4. Selected experience
5. Supporting trust signals
6. Writing
7. Contact / footer

### Deep-Dive Pages

Create dedicated pages or routed sections for:

- ExponentHR
- AutoApply AI
- tailor-resume

Optional later:

- JobScout
- fraud-detection-ml-platform

## Section-By-Section Layout

### 1. Hero

Purpose:

- establish your thesis immediately
- create a single path into case studies

Layout:

- two-column on desktop
- stacked on mobile
- left side contains headline, short supporting paragraph, and two CTAs
- right side contains a structured "proof frame" rather than a random image

Content:

- Eyebrow:
  `Senior AI Platform Engineer`
- Headline:
  `Production AI systems that teams can run, govern, and trust.`
- Supporting copy:
  `I design enterprise AI platforms, retrieval-backed workflow products, and reusable backend engines with measurable business outcomes.`
- Primary CTA:
  `Read case studies`
- Secondary CTA:
  `View resume`

Right-side proof frame should contain three compact strips:

- `400 enterprise clients served`
- `11 ATS adapters + 6 LLM providers`
- `190 tests in the tailoring core`

No headshot in the hero. The proof frame should feel like a system panel, not a profile card.

### 2. Split Proof Section

Purpose:

- let recruiters see business impact
- let engineering leaders see architecture credibility

Layout:

- two side-by-side vertical panels on desktop
- stacked on mobile

Left panel title:

- `Business impact`

Left panel items:

- `400 clients supported through ExponentHR's governed NL-to-SQL platform`
- `6K+ HR catalog columns mapped into semantic analytics domains`
- `2-day onboarding for new domains without code changes`
- `0s cold start on Fly.io for AutoApply AI`

Right panel title:

- `System design`

Right panel items:

- `FAISS retrieval + Claude Sonnet SQL generation + semantic graph joins`
- `Chrome MV3 + FastAPI + PostgreSQL + Redis workflow orchestration`
- `CLI, Streamlit, MCP, PyPI, and API surfaces for tailor-resume`
- `Kafka, MLflow, Prometheus, and Grafana in supporting ML systems`

### 3. System Map / Flagship Systems

Purpose:

- present the strongest systems as the site's true center

Layout:

- 3 primary expandable system cards
- 1 supporting row below for JobScout and Additional Systems

Cards:

#### Card 1: ExponentHR

Label:

- `Enterprise AI Platform`

Metric anchor:

- `400`
- caption: `clients served`

Body:

- `Catalog-driven NL-to-SQL platform on Microsoft Fabric with FAISS retrieval, semantic joins, governed SQL generation, and hot-reload domain onboarding.`

Actions:

- `View case study`
- `See architecture`

#### Card 2: AutoApply AI

Label:

- `Flagship Workflow Product`

Metric anchor:

- `11 + 6`
- caption: `ATS adapters + LLM providers`

Body:

- `End-to-end workflow platform for discover -> tailor -> apply -> track across Chrome MV3, FastAPI, retrieval-backed answers, and live deployments.`

Actions:

- `View case study`
- `Open repo`

#### Card 3: tailor-resume

Label:

- `Reusable Engine`

Metric anchor:

- `190`
- caption: `tests in the tailoring core`

Body:

- `Extracted tailoring engine shipped through CLI, Streamlit, MCP, PyPI, and hosted APIs to make the broader system modular and distribution-ready.`

Actions:

- `View case study`
- `Open repo`

Supporting row:

- JobScout as the discovery engine
- Additional Systems as a compact link-out block

### 4. Selected Experience

Purpose:

- show real employment history without making the page resume-shaped

Layout:

- one strong timeline or stacked list
- only relevant roles emphasized

Order:

1. ExponentHR
2. Udaan / business systems impact
3. selected earlier roles if needed

Rules:

- 2-4 bullets per role max
- each bullet must include ownership or measurable change
- avoid generic job-description language

### 5. Supporting Trust Signals

Purpose:

- reassure without derailing the story

Layout:

- compact three-column band or stacked blocks on mobile

Include:

- publication
- certification
- selected recommendations

This section should feel quiet and secondary.

### 6. Writing

Purpose:

- reinforce seniority through articulation and system thinking

Layout:

- 3 recent article cards max
- strong titles
- short, idea-driven summaries

Lead with:

- Chrome extension specialization post
- multi-LLM cascade post
- production lessons post

### 7. Contact / Footer

Purpose:

- make connection simple without performing "open to work"

Include:

- email
- LinkedIn
- GitHub
- Substack
- resume

Tone:

- no explicit "looking for roles"
- communicate seriousness and availability through the quality of the work and contact clarity

## Mobile Behavior

The mobile site must not be a squeezed desktop layout.

Rules:

- hero stacks with CTAs high
- proof frame becomes vertical and scannable
- split proof becomes accordion or stacked cards
- flagship system cards expand inline with clear tap targets
- nav becomes simple and anchored to: `Work`, `Writing`, `Resume`, `Contact`
- avoid long side-by-side metrics on narrow screens

## Motion

Keep motion light and purposeful.

- hero fade and rise on load
- metric counters can animate once
- expandable system cards should have smooth height transition
- section reveals should be staggered and subtle
- do not use floating gimmicks or constant motion

## Content References

Use only real content and real proof.

### ExponentHR

Use:

- 400 enterprise clients
- 6K+ catalog columns
- 15-minute freshness / refresh context where accurate
- 2-day onboarding for new domains without code changes
- FAISS retrieval
- Claude Sonnet SQL generation
- semantic graph joins
- row-level and column-level security

Keep sanitized:

- no confidential schema names
- no sensitive customer details
- no internal-only implementation details

### AutoApply AI

Use:

- discover -> tailor -> apply -> track workflow
- Chrome MV3 extension
- FastAPI backend
- PostgreSQL
- Redis
- Clerk
- GitHub Vault
- 11 ATS adapters
- 6 LLM providers
- live deployment proof

### tailor-resume

Use:

- CLI
- Streamlit
- MCP
- PyPI
- API surfaces
- 190 tests
- ATS-aware tailoring
- honest claim discipline

### JobScout

Use:

- 130+ companies
- 6 ATS platforms
- alerts
- ranking engine
- preference matching
- zero-cost operating model where appropriate

### Supporting Systems

For fraud-detection-ml-platform:

- 100+ TPS
- sub-ms P99 prediction latency
- MLflow
- Prometheus
- Grafana
- Kafka

For portfolio-risk-analysis:

- Kafka throughput
- Spark latency
- VaR / risk pipeline context

## SEO Direction

Homepage title direction:

- `Narendranath Edara | Senior AI Platform Engineer`

Homepage meta description direction:

- `Senior AI Platform Engineer building production LLM systems, retrieval pipelines, workflow platforms, and governed AI-enabled data products.`

Homepage copy should naturally include:

- AI platform engineer
- applied AI
- backend AI
- retrieval
- workflow platform
- NL-to-SQL
- FastAPI
- Microsoft Fabric
- FAISS
- Chrome extension

## Lovable Build Strategy

Lovable works better when prompted by component rather than asking for the whole app in a single shot. The recommended flow is:

1. give Lovable the master prompt below in Plan mode
2. let it ask clarifying questions
3. build the homepage shell first
4. then prompt each section one by one
5. then build case-study pages

## Lovable Master Prompt

```text
Build a premium personal portfolio website for Narendranath Edara, a Senior AI Platform Engineer. This is not a generic developer portfolio and it must not look like a startup landing page template. The site should feel minimal, architectural, editorial, and highly intentional. The audience is primarily recruiters and hiring managers, with engineering leaders as the secondary audience.

The portfolio must communicate in under 10 seconds that this person builds production AI systems with measurable outcomes, strong system boundaries, and reusable product surfaces.

The visual tone should be calm, precise, modern, and high-trust. Avoid purple AI gradients, generic SaaS cards, over-decorated dashboards, or trendy visual noise. Use a disciplined grid, strong spacing, premium typography, quiet surfaces, and subtle motion. The site should feel like an operating map of important systems rather than a collection of random projects.

Use this color system:
- background #F6F4EF
- main surface #FBF9F5
- elevated cards #FFFFFF
- primary text #171614
- secondary text #5C5A54
- muted text #8E8A82
- border #DDD8CF
- primary accent forest #1F4D43
- hover accent forest #2C6659
- warm accent #B78A58
- soft moss wash #E8EFEA
- technical ink blue #21344A

Typography should feel editorial and technical:
- refined serif for large display headlines
- readable sans-serif for body copy
- monospace only for metrics, system labels, or command-like accents

The site architecture should be a hybrid homepage plus dedicated case-study pages. The homepage must be optimized for scanning. The primary action should always be reading case studies. Resume and contact are secondary actions, not the main focus.

Create the homepage in this exact order:

1. Hero
2. Split proof section
3. Flagship systems map
4. Selected experience
5. Supporting trust signals
6. Writing
7. Contact/footer

Hero section:
- two-column layout on desktop, stacked on mobile
- left side: eyebrow, headline, supporting paragraph, 2 CTAs
- right side: a structured proof frame with 3 compact proof strips
- no headshot in the hero

Hero content:
- eyebrow: Senior AI Platform Engineer
- headline: Production AI systems that teams can run, govern, and trust.
- supporting paragraph: I design enterprise AI platforms, retrieval-backed workflow products, and reusable backend engines with measurable business outcomes.
- primary CTA: Read case studies
- secondary CTA: View resume

Hero proof frame should include these three compact proof strips:
- 400 enterprise clients served
- 11 ATS adapters + 6 LLM providers
- 190 tests in the tailoring core

The section immediately below the hero should be a split proof section with two vertical panels:
- left panel title: Business impact
- right panel title: System design

Business impact panel content:
- 400 clients supported through ExponentHR's governed NL-to-SQL platform
- 6K+ HR catalog columns mapped into semantic analytics domains
- 2-day onboarding for new domains without code changes
- 0s cold start on Fly.io for AutoApply AI

System design panel content:
- FAISS retrieval + Claude Sonnet SQL generation + semantic graph joins
- Chrome MV3 + FastAPI + PostgreSQL + Redis workflow orchestration
- CLI, Streamlit, MCP, PyPI, and API surfaces for tailor-resume
- Kafka, MLflow, Prometheus, and Grafana in supporting ML systems

The next section should be the core of the site: a flagship systems map with 3 primary system cards and one supporting row. These are not generic project cards. They should feel like serious product or platform briefs with expandable details.

Card 1:
- label: Enterprise AI Platform
- large metric: 400
- caption: clients served
- title: ExponentHR
- description: Catalog-driven NL-to-SQL platform on Microsoft Fabric with FAISS retrieval, semantic joins, governed SQL generation, and hot-reload domain onboarding.
- actions: View case study, See architecture

Card 2:
- label: Flagship Workflow Product
- large metric: 11 + 6
- caption: ATS adapters + LLM providers
- title: AutoApply AI
- description: End-to-end workflow platform for discover -> tailor -> apply -> track across Chrome MV3, FastAPI, retrieval-backed answers, and live deployments.
- actions: View case study, Open repo

Card 3:
- label: Reusable Engine
- large metric: 190
- caption: tests in the tailoring core
- title: tailor-resume
- description: Extracted tailoring engine shipped through CLI, Streamlit, MCP, PyPI, and hosted APIs to make the broader system modular and distribution-ready.
- actions: View case study, Open repo

Below the 3 main cards, add a supporting row with:
- JobScout as the discovery engine
- Additional Systems as a compact list linking to fraud-detection-ml-platform and portfolio-risk-analysis

Then create a Selected Experience section, but keep it concise. It should not feel like a resume dump. Show only the most relevant roles and rewrite them around ownership, scale, and system outcomes. ExponentHR should lead clearly.

Then create Supporting Trust Signals as a quiet, compact section containing:
- publication
- certification
- selected recommendation snippets

Then create a Writing section with 3 article cards max. It should feel like proof of thoughtfulness and system design communication.

Then create a clean Contact/Footer section with:
- email
- LinkedIn
- GitHub
- Substack
- resume

Do not explicitly say the person is looking for a job. Convey seriousness and readiness through clarity, polish, and proof.

Create 3 dedicated case-study pages or routes:

1. ExponentHR case study
- sanitized enterprise architecture
- problem, system design, governance/security, measurable outcomes
- keep confidential details abstracted

2. AutoApply AI case study
- full workflow from discover to tailor to apply to track
- emphasize product architecture and orchestration

3. tailor-resume case study
- extracted engine story
- interfaces, test coverage, packaging, and why modularization mattered

Use real content only. Do not generate lorem ipsum or fake metrics. Use the following content references exactly and consistently:

ExponentHR:
- 400 enterprise clients
- 6K+ catalog columns
- FAISS retrieval
- Claude Sonnet SQL generation
- semantic graph joins
- governed SQL generation
- row-level and column-level security
- zero-code or no-code onboarding in about 2 days for new domains

AutoApply AI:
- discover -> tailor -> apply -> track
- Chrome MV3
- FastAPI
- PostgreSQL
- Redis
- Clerk
- GitHub Vault
- 11 ATS adapters
- 6 LLM providers

tailor-resume:
- CLI
- Streamlit
- MCP
- PyPI
- API surfaces
- 190 tests
- ATS-aware tailoring

JobScout:
- 130+ companies
- 6 ATS platforms
- alerts
- ranking engine
- preference matching

Additional systems:
- fraud-detection-ml-platform: 100+ TPS, sub-ms P99, MLflow, Prometheus, Grafana, Kafka
- portfolio-risk-analysis: Kafka, Spark, VaR pipeline

Mobile behavior is critical:
- do not simply shrink the desktop layout
- stack hero cleanly
- make proof frame vertical and readable
- make split proof section stack into elegant cards
- make system cards expandable with comfortable tap targets
- keep navigation simple: Work, Writing, Resume, Contact

Use subtle animations only:
- fade/rise hero entrance
- smooth card expansion
- slight staggered reveals
- no constant floating or gimmicky motion

Important:
- ask clarifying questions before writing code if any part of the information architecture or route strategy is unclear
- build by component, not by generating the entire site in one pass
- use semantic HTML structure and production-grade responsive design
- prioritize hierarchy, readability, and trust over visual effects
```

## Recommended Follow-Up Prompt Sequence For Lovable

After the master prompt, use these prompts in order:

1. `Build the homepage shell and nav only. Do not build all sections yet.`
2. `Build the hero and split proof section using the provided content exactly.`
3. `Build the flagship systems map with expandable cards for ExponentHR, AutoApply AI, and tailor-resume.`
4. `Build the Selected Experience and Supporting Trust Signals sections in a quieter style.`
5. `Build the Writing section and Contact/Footer with strong mobile behavior.`
6. `Create the ExponentHR case study page with sanitized architecture visuals.`
7. `Create the AutoApply AI case study page.`
8. `Create the tailor-resume case study page.`
9. `Refine mobile layout, spacing, and section transitions without changing the content hierarchy.`

## Decision

Recommended direction:

- keep the strongest work at the top
- keep the homepage tighter than the current version
- preserve breadth through deeper routes and supporting sections
- make the site feel more like a serious systems portfolio than a conventional personal website
