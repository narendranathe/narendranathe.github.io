# Portfolio Synthesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the portfolio homepage and supporting case-study pages into a hybrid synthesis that keeps the `system-map` visual shell while using the stronger recruiter-facing content, labels, and search-aligned positioning from `main` and `feat/ai-platform-portfolio-refresh`.

**Architecture:** The implementation keeps the current static-site structure: shared data in `config.js`, shell behavior in `app.js`, global styling in `styles.css`, and page content in raw HTML files. The homepage becomes the main narrative surface, with the case-study pages refined to match the same positioning and language system. Verification relies on deterministic content assertions plus a local browser check because the repo does not have an automated frontend test harness.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, GitHub Pages, PowerShell verification, local `python -m http.server`

---

## File Structure

### Files to Modify

- `config.js`
  - Shared identity, footer statement, and primary navigation labels.
- `index.html`
  - Homepage content, section order, hero copy, labels, system cards, new `How I work` section, refined experience/credibility/writing/connect sections.
- `styles.css`
  - Styling for updated hero proof list, abstract visual treatments, new `How I work` block, refined support cards, and expandable experience cards.
- `app.js`
  - Add support for expandable experience cards while preserving existing system-card expansion behavior.
- `exponenthr.html`
  - Tighten case-study language to match the homepage narrative and recruiter-facing wording.
- `autoapply-ai.html`
  - Align product/platform language, especially around workflow orchestration and system boundaries.
- `tailor-resume.html`
  - Reinforce the extracted-engine story and modular platform framing.

### Files to Verify But Not Modify Unless Necessary

- `robots.txt`
- `sitemap.xml`

### Files to Ignore

- `.claude-memory.md`
- `CLAUDE.md`
- `gen.py`

## Task 1: Update Shared Positioning And Navigation

**Files:**
- Modify: `config.js`
- Test: `config.js`

- [ ] **Step 1: Assert the current shared config still uses the old navigation and footer copy**

Run:

```powershell
$path = "C:\Users\naren\narendranathe.github.io\config.js"
$content = Get-Content -Path $path -Raw
if ($content -notmatch 'label: "Work"') { throw 'Expected old nav label Work' }
if ($content -notmatch 'label: "Writing"') { throw 'Expected old nav label Writing' }
if ($content -notmatch 'workflow products with measurable outcomes and clear system boundaries') { throw 'Expected old footer statement' }
'PASS: baseline config matches pre-synthesis wording'
```

Expected:

```text
PASS: baseline config matches pre-synthesis wording
```

- [ ] **Step 2: Update the shared identity copy and navigation labels**

Change `config.js` to this shape:

```js
window.PORTFOLIO_CONFIG = {
  identity: {
    name: "Narendranath Edara",
    role: "Senior AI Platform Engineer",
    headline:
      "Production-grade AI systems for retrieval, workflow automation, and reliable delivery.",
    summary:
      "I build enterprise AI platforms, AI-powered workflow products, and reusable backend engines with measurable impact across retrieval, inference, deployment, and product reliability.",
    footerStatement:
      "Senior AI platform engineering across retrieval, workflow automation, reusable engines, and production delivery."
  },
  links: {
    home: "index.html",
    resume:
      "https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf",
    linkedin: "https://www.linkedin.com/in/narendranathe/",
    github: "https://github.com/narendranathe",
    substack: "https://narendranathe.substack.com",
    email: "mailto:edara.narendranath@gmail.com",
    publication: "https://doi.org/10.1080/10495142.2025.2525123"
  },
  navigation: [
    { label: "Systems", href: "#systems" },
    { label: "How I Work", href: "#how-i-work" },
    { label: "Experience", href: "#experience" },
    { label: "Notes", href: "#notes" },
    { label: "Connect", href: "#connect" }
  ],
  caseStudies: [
    { label: "ExponentHR", href: "exponenthr.html" },
    { label: "AutoApply AI", href: "autoapply-ai.html" },
    { label: "tailor-resume", href: "tailor-resume.html" }
  ],
  contactLinks: [
    { label: "Email", href: "mailto:edara.narendranath@gmail.com" },
    { label: "LinkedIn", href: "https://www.linkedin.com/in/narendranathe/" },
    { label: "GitHub", href: "https://github.com/narendranathe" },
    { label: "Substack", href: "https://narendranathe.substack.com" },
    {
      label: "Resume",
      href:
        "https://github.com/narendranathe/resume2/releases/download/resume/Narendranath.pdf"
    }
  ]
};
```

- [ ] **Step 3: Verify the updated shared config contains the new positioning**

Run:

```powershell
$path = "C:\Users\naren\narendranathe.github.io\config.js"
$content = Get-Content -Path $path -Raw
if ($content -notmatch 'Production-grade AI systems for retrieval, workflow automation, and reliable delivery') { throw 'Missing new headline' }
if ($content -notmatch 'label: "Systems"') { throw 'Missing Systems nav label' }
if ($content -notmatch 'label: "How I Work"') { throw 'Missing How I Work nav label' }
if ($content -notmatch 'label: "Connect"') { throw 'Missing Connect nav label' }
'PASS: shared config updated'
```

Expected:

```text
PASS: shared config updated
```

- [ ] **Step 4: Commit the shared config change**

Run:

```bash
git -C C:\Users\naren\narendranathe.github.io add config.js
git -C C:\Users\naren\narendranathe.github.io commit -m "refactor: align shared portfolio positioning"
```

## Task 2: Rewrite Homepage Narrative And Section Labels

**Files:**
- Modify: `index.html`
- Test: `index.html`

- [ ] **Step 1: Assert the homepage still contains the old weak labels before rewriting**

Run:

```powershell
$path = "C:\Users\naren\narendranathe.github.io\index.html"
$content = Get-Content -Path $path -Raw
if ($content -notmatch 'Proof frame') { throw 'Expected old label Proof frame' }
if ($content -notmatch 'Selected experience') { throw 'Expected old label Selected experience' }
if ($content -notmatch 'Supporting trust') { throw 'Expected old label Supporting trust' }
'PASS: homepage still has old synthesis labels'
```

Expected:

```text
PASS: homepage still has old synthesis labels
```

- [ ] **Step 2: Rewrite the hero using the approved recruiter-facing headline and proof bullets**

Update the homepage metadata and hero portion of `index.html` so the head and left hero column use this content:

```html
<meta name="description" content="Narendranath Edara is a Senior AI Platform Engineer building production-grade AI systems for retrieval, workflow automation, inference, and reliable delivery.">
<meta property="og:description" content="Production-grade AI systems across enterprise platforms, workflow products, and reusable engines with measurable impact.">
<meta name="twitter:description" content="Production-grade AI systems across enterprise platforms, workflow products, and reusable engines with measurable impact.">
<title>Narendranath Edara | Senior AI Platform Engineer</title>
```

Then update the left hero column to use this content:

```html
<span class="hero__eyebrow">Senior AI Platform Engineer</span>
<h1 class="hero__headline">Production-grade AI systems for retrieval, workflow automation, and reliable delivery.</h1>
<p class="hero__summary">
  I build enterprise AI platforms, AI-powered workflow products, and reusable backend engines with measurable impact across retrieval, inference, deployment, and product reliability.
</p>
<ul class="hero__proof-list">
  <li><strong>ExponentHR:</strong> architected a catalog-driven NL-to-SQL platform on Microsoft Fabric for 400 enterprise clients with FAISS retrieval, governed T-SQL generation, and semantic joins across HR domains.</li>
  <li><strong>AutoApply AI:</strong> built an end-to-end workflow platform for discover -> tailor -> apply -> track across FastAPI, Chrome MV3, retrieval-backed answers, model routing, and live deployments.</li>
  <li><strong>Modular engines:</strong> extracted the tailoring core into <strong>tailor-resume</strong> and the discovery layer into <strong>JobScout</strong> so the product could evolve as a platform instead of a pile of overlapping tools.</li>
</ul>
```

Update the hero right panel header and metrics to this:

```html
<div class="proof-panel__header">
  <span>Measured impact</span>
  <span>Enterprise platform + workflow product + reusable engine</span>
</div>
<div class="proof-strip">
  <span class="proof-strip__metric" data-count="400">400</span>
  <span class="proof-strip__label">enterprise clients on ExponentHR's governed analytics platform</span>
</div>
<div class="proof-strip">
  <span class="proof-strip__metric" data-count="6000">6000</span>
  <span class="proof-strip__label">HR catalog columns mapped into reusable domains for secure query planning</span>
</div>
<div class="proof-strip">
  <span class="proof-strip__metric">11 + 6</span>
  <span class="proof-strip__label">ATS adapters and model providers inside AutoApply AI's workflow platform</span>
</div>
<div class="proof-strip">
  <span class="proof-strip__metric" data-count="190">190</span>
  <span class="proof-strip__label">tests around the extracted tailoring engine shipped across multiple surfaces</span>
</div>
```

- [ ] **Step 3: Rewrite the split proof block and section labels**

Replace the old section framing with these exact labels:

```html
<h2 class="proof-column__title">Measured impact</h2>
```

and

```html
<h2 class="proof-column__title">Architecture signals</h2>
```

Use these exact list items in the proof lists:

```html
<li>
  <span class="proof-list__kicker">ExponentHR</span>
  <span>400 clients supported through a governed NL-to-SQL platform built on Microsoft Fabric with retrieval, semantic joins, and secure query execution.</span>
</li>
<li>
  <span class="proof-list__kicker">Deployment speed</span>
  <span>New domains onboard in about 2 days through hot-reload catalog patterns instead of fresh engineering work.</span>
</li>
<li>
  <span class="proof-list__kicker">Workflow platform</span>
  <span>AutoApply AI combines discovery, tailoring, application automation, and tracking behind one coherent product surface.</span>
</li>
```

and

```html
<li>
  <span class="proof-list__kicker">Retrieval and inference</span>
  <span>FAISS retrieval, governed SQL generation, and semantic graph joins drive ExponentHR's enterprise query flow.</span>
</li>
<li>
  <span class="proof-list__kicker">Workflow orchestration</span>
  <span>Chrome MV3, FastAPI, PostgreSQL, and Redis coordinate stateful discover -> tailor -> apply -> track behavior.</span>
</li>
<li>
  <span class="proof-list__kicker">Reusable engine surfaces</span>
  <span>CLI, Streamlit, MCP, PyPI, and hosted APIs make tailor-resume inspectable as a real engine instead of a one-off tool.</span>
</li>
```

- [ ] **Step 4: Rewrite the system section and insert the `How I work` section**

Use these exact labels on the homepage:

```html
<span class="section-label">Selected systems</span>
```

```html
<span class="section-label">Supporting system</span>
```

```html
<span class="section-label">Additional systems</span>
```

Add a new section after the system grid and before experience:

```html
<section class="section" id="how-i-work">
  <div class="container">
    <div class="section-heading" data-reveal>
      <span class="section-label">How I work</span>
      <h2>Architecture decisions, production reliability, and systems with clear boundaries.</h2>
      <p>
        I optimize for safe, reliable AI systems that can be operated, inspected, and extended over time. The through-line across the portfolio is platform ownership: retrieval, APIs, storage, deployment, workflow state, and measurable operational outcomes.
      </p>
    </div>
    <div class="how-grid">
      <article class="how-card" data-reveal>
        <h3>Architecture design decisions</h3>
        <p>I separate retrieval, planning, execution, and product surfaces so systems stay debuggable and reusable instead of collapsing into AI-flavored glue code.</p>
      </article>
      <article class="how-card" data-reveal>
        <h3>Reliable delivery</h3>
        <p>I treat deployment, monitoring, state handling, and fallback behavior as part of the product, not cleanup work after the model call.</p>
      </article>
      <article class="how-card" data-reveal>
        <h3>Measured outcomes</h3>
        <p>The strongest proof is operational: clients served, systems modularized, onboarding speed improved, and workflows that behave like products in production.</p>
      </article>
    </div>
  </div>
</section>
```

- [ ] **Step 5: Verify the homepage now contains the approved labels and no longer contains the rejected ones**

Run:

```powershell
$path = "C:\Users\naren\narendranathe.github.io\index.html"
$content = Get-Content -Path $path -Raw
$forbidden = @('Proof frame', 'Selected experience', 'Supporting trust')
foreach ($item in $forbidden) {
  if ($content -match [regex]::Escape($item)) { throw "Forbidden legacy label remains: $item" }
}
$required = @(
  'Measured impact',
  'Selected systems',
  'How I work',
  'Experience highlights',
  'Credibility signals',
  'Engineering notes',
  'Connect'
)
foreach ($item in $required) {
  if ($content -notmatch [regex]::Escape($item)) { throw "Missing required label: $item" }
}
'PASS: homepage labels rewritten'
```

Expected:

```text
PASS: homepage labels rewritten
```

- [ ] **Step 6: Commit the homepage narrative rewrite**

Run:

```bash
git -C C:\Users\naren\narendranathe.github.io add index.html
git -C C:\Users\naren\narendranathe.github.io commit -m "feat: rewrite portfolio homepage narrative"
```

## Task 3: Add Styling And Interaction For The New Homepage Structure

**Files:**
- Modify: `styles.css`
- Modify: `app.js`
- Test: `styles.css`, `app.js`

- [ ] **Step 1: Assert the current stylesheet does not yet define the new `How I work` or experience expansion styles**

Run:

```powershell
$css = Get-Content -Path "C:\Users\naren\narendranathe.github.io\styles.css" -Raw
if ($css -match '\.how-grid') { throw 'Unexpected existing .how-grid styles' }
if ($css -match '\.experience-card\.is-open') { throw 'Unexpected existing experience expansion styles' }
'PASS: new section styles not present yet'
```

Expected:

```text
PASS: new section styles not present yet
```

- [ ] **Step 2: Add styles for the new proof list, `How I work` cards, abstract visual treatments, and expanded experience details**

Add these CSS blocks to `styles.css`:

```css
.hero__proof-list {
  display: grid;
  gap: 0.85rem;
  margin: 1.5rem 0 0;
  padding: 0;
  list-style: none;
}

.hero__proof-list li {
  padding: 0.95rem 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.72);
  color: var(--text-secondary);
}

.how-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.25rem;
}

.how-card {
  padding: 1.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: linear-gradient(180deg, rgba(232, 239, 234, 0.75), rgba(255, 255, 255, 0.94));
  box-shadow: var(--shadow-card);
}

.experience-card__summary {
  display: grid;
  gap: 0.8rem;
}

.experience-card__details {
  display: none;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.experience-card.is-open .experience-card__details {
  display: block;
}
```

- [ ] **Step 3: Extend `app.js` to support experience-card expansion without breaking system-card expansion**

Add a second setup helper in `app.js`:

```js
function setupExperienceExpansions() {
  document.querySelectorAll(".experience-toggle").forEach((button) => {
    button.addEventListener("click", function () {
      const card = button.closest(".experience-card");

      if (!card) {
        return;
      }

      const isOpen = card.classList.toggle("is-open");
      button.setAttribute("aria-expanded", String(isOpen));
      button.textContent = isOpen ? "Collapse detail" : "Expand detail";
    });
  });
}
```

Then invoke it inside `DOMContentLoaded`:

```js
document.addEventListener("DOMContentLoaded", function () {
  renderHeader();
  renderFooter();
  setupMenu();
  setupExpansions();
  setupExperienceExpansions();
  setupReveals();
  setupMetricCounts();
});
```

- [ ] **Step 4: Verify the stylesheet and script include the new selectors and helper**

Run:

```powershell
$css = Get-Content -Path "C:\Users\naren\narendranathe.github.io\styles.css" -Raw
$js = Get-Content -Path "C:\Users\naren\narendranathe.github.io\app.js" -Raw
if ($css -notmatch '\.hero__proof-list') { throw 'Missing hero proof list styles' }
if ($css -notmatch '\.how-grid') { throw 'Missing how-grid styles' }
if ($css -notmatch '\.experience-card\.is-open \.experience-card__details') { throw 'Missing experience expansion styles' }
if ($js -notmatch 'function setupExperienceExpansions') { throw 'Missing experience expansion helper' }
if ($js -notmatch 'setupExperienceExpansions\(\);') { throw 'Missing experience expansion init call' }
'PASS: interaction and style hooks added'
```

Expected:

```text
PASS: interaction and style hooks added
```

- [ ] **Step 5: Commit the style and interaction changes**

Run:

```bash
git -C C:\Users\naren\narendranathe.github.io add styles.css app.js
git -C C:\Users\naren\narendranathe.github.io commit -m "feat: add synthesis layout styling and interactions"
```

## Task 4: Deepen Experience And Refine Supporting Sections

**Files:**
- Modify: `index.html`
- Test: `index.html`

- [ ] **Step 1: Replace the experience cards with expandable recruiter-depth cards**

Use this structure for each experience card in `index.html`:

```html
<article class="experience-card" data-reveal>
  <div class="experience-card__summary">
    <div class="experience-card__meta">
      <h3 class="experience-card__company">ExponentHR</h3>
      <span class="experience-card__role">Data Engineer | AI Platform / Applied AI</span>
      <span class="experience-card__time">Jul 2024 - Present</span>
    </div>
    <p class="experience-card__scope">
      Architecting a governed enterprise NL-to-SQL platform on Microsoft Fabric with retrieval, semantic joins, and secure query execution for 400 clients.
    </p>
    <ul class="experience-card__bullets">
      <li>Architecture: catalog-driven retrieval, semantic join planning, and governed T-SQL generation.</li>
      <li>Scale: 400 enterprise clients and 6K+ HR catalog columns across multiple domains.</li>
      <li>Impact: domain onboarding moved toward days instead of long engineering cycles.</li>
    </ul>
    <button class="expand-toggle experience-toggle" type="button" aria-expanded="false">Expand detail</button>
  </div>
  <div class="experience-card__details">
    <p><strong>System boundary:</strong> retrieval, planning, security-aware execution, and hot-reload domain onboarding.</p>
    <p><strong>Key decisions:</strong> separate semantic lookup, join resolution, and SQL execution so governance and reliability remain explicit.</p>
    <p><strong>Production outcome:</strong> an enterprise AI platform story that demonstrates real ownership rather than isolated model integration.</p>
  </div>
</article>
```

Use these exact companion structures for the other experience cards:

```html
<article class="experience-card" data-reveal>
  <div class="experience-card__summary">
    <div class="experience-card__meta">
      <h3 class="experience-card__company">Missouri S&amp;T</h3>
      <span class="experience-card__role">Data Engineer / ML Systems Builder</span>
      <span class="experience-card__time">Graduate studies</span>
    </div>
    <p class="experience-card__scope">
      Built anomaly-detection, AKS, and NLP systems that strengthened platform reliability, observability, and applied ML delivery.
    </p>
    <ul class="experience-card__bullets">
      <li>Architecture: Azure anomaly detection pipelines, AKS migration work, and production-focused ML system design.</li>
      <li>Scale: university and lab systems with deployable cloud infrastructure, not isolated notebooks.</li>
      <li>Impact: improved alert quality, raised utilization, lowered spend, and produced peer-reviewed NLP research.</li>
    </ul>
    <button class="expand-toggle experience-toggle" type="button" aria-expanded="false">Expand detail</button>
  </div>
  <div class="experience-card__details">
    <p><strong>System boundary:</strong> monitoring, anomaly detection, ML deployment, and container orchestration.</p>
    <p><strong>Key decisions:</strong> move work toward repeatable platform behavior instead of one-off analysis.</p>
    <p><strong>Production outcome:</strong> stronger signal quality and more realistic operating experience for AI and data systems.</p>
  </div>
</article>
```

```html
<article class="experience-card" data-reveal>
  <div class="experience-card__summary">
    <div class="experience-card__meta">
      <h3 class="experience-card__company">Zomato</h3>
      <span class="experience-card__role">Analytics and Search Systems</span>
      <span class="experience-card__time">Earlier foundation</span>
    </div>
    <p class="experience-card__scope">
      Built analytics and search-adjacent systems that improved pricing insight, information access, and operational decision support.
    </p>
    <ul class="experience-card__bullets">
      <li>Architecture: real-time competitor analytics and internal search tooling.</li>
      <li>Scale: production business workflows and search-heavy operational environments.</li>
      <li>Impact: informed pricing decisions, reduced support load, and built the platform instincts that show up in later AI systems work.</li>
    </ul>
    <button class="expand-toggle experience-toggle" type="button" aria-expanded="false">Expand detail</button>
  </div>
  <div class="experience-card__details">
    <p><strong>System boundary:</strong> analytics pipelines, search tooling, and decision-support surfaces.</p>
    <p><strong>Key decisions:</strong> keep business-facing tools inspectable, fast, and useful in day-to-day operations.</p>
    <p><strong>Production outcome:</strong> a stronger foundation in search, analytics, and backend system behavior.</p>
  </div>
</article>
```

- [ ] **Step 2: Refine the supporting sections with the approved labels**

Update the lower sections of `index.html` to use these exact headings:

```html
<span class="section-label">Credibility signals</span>
<h2>Quiet proof that supports the systems story.</h2>
```

```html
<span class="section-label">Engineering notes</span>
<h2>Architecture notes and production lessons.</h2>
```

```html
<span class="section-label">Connect</span>
<h2>Inspect the work, then reach out.</h2>
```

Use these exact supporting paragraphs:

```html
<!-- credibility signals intro -->
<p>
  Publication, certification, and peer feedback matter most after the systems have made their case. This section stays short and supports the work instead of trying to replace it.
</p>

<!-- publication card -->
<p>
  Published in Taylor &amp; Francis in 2025 on sentiment analysis for visitor feedback and insight extraction.
</p>

<!-- certification card -->
<p>
  Microsoft Certified: DP-700 Data Engineer, aligned with the data, platform, and governed analytics side of production AI systems.
</p>

<!-- recommendation card -->
<blockquote>
  "Quick and humble learner that loves researching new business areas and turning problems into tangible systems."
</blockquote>

<!-- engineering notes intro -->
<p>
  The writing section shows how I think about system boundaries, failure modes, provider strategy, and the choices behind production AI workflows.
</p>

<!-- connect intro -->
<p>
  The fastest way to evaluate fit is to inspect the systems and case studies first. If the work aligns with what your team needs, the contact paths are straightforward.
</p>
```

- [ ] **Step 3: Verify that the homepage now includes expandable experience detail and the new supporting labels**

Run:

```powershell
$html = Get-Content -Path "C:\Users\naren\narendranathe.github.io\index.html" -Raw
if ($html -notmatch 'experience-toggle') { throw 'Missing experience toggle button' }
if ($html -notmatch 'experience-card__details') { throw 'Missing experience details block' }
if ($html -notmatch 'Credibility signals') { throw 'Missing Credibility signals section' }
if ($html -notmatch 'Engineering notes') { throw 'Missing Engineering notes section' }
if ($html -notmatch 'Connect') { throw 'Missing Connect section' }
'PASS: homepage support sections and experience detail updated'
```

Expected:

```text
PASS: homepage support sections and experience detail updated
```

- [ ] **Step 4: Commit the experience and support-section rewrite**

Run:

```bash
git -C C:\Users\naren\narendranathe.github.io add index.html
git -C C:\Users\naren\narendranathe.github.io commit -m "feat: deepen portfolio experience and support sections"
```

## Task 5: Align Case Studies And Run End-To-End Verification

**Files:**
- Modify: `exponenthr.html`
- Modify: `autoapply-ai.html`
- Modify: `tailor-resume.html`
- Test: `index.html`, `exponenthr.html`, `autoapply-ai.html`, `tailor-resume.html`

- [ ] **Step 1: Tighten the case-study page ledes so they match the homepage story**

Use these lead paragraphs:

For `exponenthr.html`:

```html
<p>
  Sanitized case study for a catalog-driven NL-to-SQL platform on Microsoft Fabric with FAISS retrieval, governed T-SQL generation, semantic joins, and hot-reload domain onboarding for enterprise analytics at scale.
</p>
```

For `autoapply-ai.html`:

```html
<p>
  A production AI workflow platform for discover -> tailor -> apply -> track across Chrome MV3, FastAPI, retrieval-backed answers, provider routing, and persistent workflow state.
</p>
```

For `tailor-resume.html`:

```html
<p>
  The extracted tailoring engine behind the broader workflow platform, shipped through CLI, Streamlit, MCP, PyPI, and hosted APIs with strong automated test coverage.
</p>
```

- [ ] **Step 2: Align the case-study proof language with the homepage vocabulary**

Ensure the case-study pages include these exact phrases:

```html
<!-- exponenthr.html -->
<li>Governed query execution and semantic join planning are treated as platform concerns, not post-processing.</li>

<!-- autoapply-ai.html -->
<li>Provider routing, workflow state, and ATS execution make the system read as product engineering plus AI infrastructure.</li>

<!-- tailor-resume.html -->
<li>The extracted engine proves modularization, distribution thinking, and quality discipline through multi-surface delivery.</li>
```

- [ ] **Step 3: Run deterministic content verification across homepage and case-study pages**

Run:

```powershell
$files = @(
  "C:\Users\naren\narendranathe.github.io\index.html",
  "C:\Users\naren\narendranathe.github.io\exponenthr.html",
  "C:\Users\naren\narendranathe.github.io\autoapply-ai.html",
  "C:\Users\naren\narendranathe.github.io\tailor-resume.html"
)
foreach ($file in $files) {
  $content = Get-Content -Path $file -Raw
  if ($content -notmatch 'Narendranath') { throw "Expected portfolio identity missing in $file" }
}
$index = Get-Content -Path "C:\Users\naren\narendranathe.github.io\index.html" -Raw
foreach ($href in @('exponenthr.html', 'autoapply-ai.html', 'tailor-resume.html')) {
  if ($index -notmatch [regex]::Escape($href)) { throw "Missing homepage case-study link: $href" }
}
'PASS: case-study content and links verified'
```

Expected:

```text
PASS: case-study content and links verified
```

- [ ] **Step 4: Run a local browser preview**

Run in one terminal:

```bash
cd C:\Users\naren\narendranathe.github.io
python -m http.server 4173
```

Then verify in a browser:

- homepage loads at `http://localhost:4173/index.html`
- sticky header remains visible during scroll
- navigation anchors work
- system-card expansion works
- experience-card expansion works
- case-study pages load without missing stylesheet or script errors

- [ ] **Step 5: Commit the case-study alignment and homepage verification**

Run:

```bash
git -C C:\Users\naren\narendranathe.github.io add index.html exponenthr.html autoapply-ai.html tailor-resume.html
git -C C:\Users\naren\narendranathe.github.io commit -m "feat: align portfolio case studies with synthesis narrative"
```

## Self-Review Checklist

- [ ] The homepage uses the exact approved labels:
  - `Measured impact`
  - `Selected systems`
  - `How I work`
  - `Experience highlights`
  - `Credibility signals`
  - `Engineering notes`
  - `Connect`
- [ ] The hero headline and summary match the approved positioning from the design spec.
- [ ] JobScout stays supporting proof rather than becoming a fourth flagship card.
- [ ] No broken GitHub stats widgets or badge walls are reintroduced.
- [ ] The three case-study pages still load from the homepage and carry the same hiring narrative.
- [ ] `.claude-memory.md`, `CLAUDE.md`, and `gen.py` remain untracked.
