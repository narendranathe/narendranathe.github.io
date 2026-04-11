# Portfolio Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the portfolio into a cleaner multi-page static site with a systems-first homepage and three deep-dive case studies.

**Architecture:** Replace the current single large `index.html` with a small static site system: shared CSS, shared JavaScript, a data/config layer, one rebuilt homepage, and three case-study pages. Preserve GitHub Pages simplicity while making the codebase easier to evolve.

**Tech Stack:** HTML, CSS, vanilla JavaScript, GitHub Pages, agent-browser for visual verification

---

### Task 1: Establish The New Static Site Structure

**Files:**
- Create: `C:/Users/naren/narendranathe.github.io/styles.css`
- Create: `C:/Users/naren/narendranathe.github.io/app.js`
- Modify: `C:/Users/naren/narendranathe.github.io/config.js`
- Modify: `C:/Users/naren/narendranathe.github.io/index.html`

- [ ] **Step 1: Replace the current config with focused content for the new IA**
- [ ] **Step 2: Create a shared stylesheet for layout, typography, cards, and responsive rules**
- [ ] **Step 3: Create a shared JavaScript file for nav, expandable cards, and lightweight motion**
- [ ] **Step 4: Replace the homepage shell with the new section order**
- [ ] **Step 5: Commit**

### Task 2: Build The Homepage Sections

**Files:**
- Modify: `C:/Users/naren/narendranathe.github.io/index.html`
- Modify: `C:/Users/naren/narendranathe.github.io/styles.css`
- Modify: `C:/Users/naren/narendranathe.github.io/app.js`

- [ ] **Step 1: Build the hero and proof frame**
- [ ] **Step 2: Build the split proof section**
- [ ] **Step 3: Build the flagship systems map**
- [ ] **Step 4: Build selected experience, trust signals, writing, and footer**
- [ ] **Step 5: Commit**

### Task 3: Add Dedicated Case Study Pages

**Files:**
- Create: `C:/Users/naren/narendranathe.github.io/exponenthr.html`
- Create: `C:/Users/naren/narendranathe.github.io/autoapply-ai.html`
- Create: `C:/Users/naren/narendranathe.github.io/tailor-resume.html`
- Modify: `C:/Users/naren/narendranathe.github.io/styles.css`
- Modify: `C:/Users/naren/narendranathe.github.io/app.js`

- [ ] **Step 1: Create a reusable case-study page structure**
- [ ] **Step 2: Build ExponentHR with sanitized architecture and enterprise proof**
- [ ] **Step 3: Build AutoApply AI with workflow and orchestration detail**
- [ ] **Step 4: Build tailor-resume with extracted-engine framing**
- [ ] **Step 5: Commit**

### Task 4: Polish Navigation, SEO, And GitHub Pages Fit

**Files:**
- Modify: `C:/Users/naren/narendranathe.github.io/index.html`
- Modify: `C:/Users/naren/narendranathe.github.io/exponenthr.html`
- Modify: `C:/Users/naren/narendranathe.github.io/autoapply-ai.html`
- Modify: `C:/Users/naren/narendranathe.github.io/tailor-resume.html`
- Modify: `C:/Users/naren/narendranathe.github.io/README.md`
- Modify: `C:/Users/naren/narendranathe.github.io/sitemap.xml`

- [ ] **Step 1: Make nav and footer links consistent across all pages**
- [ ] **Step 2: Update metadata and titles**
- [ ] **Step 3: Update sitemap for new routes**
- [ ] **Step 4: Commit**

### Task 5: Verify Desktop And Mobile

**Files:**
- Verify: `C:/Users/naren/narendranathe.github.io/index.html`
- Verify: `C:/Users/naren/narendranathe.github.io/exponenthr.html`
- Verify: `C:/Users/naren/narendranathe.github.io/autoapply-ai.html`
- Verify: `C:/Users/naren/narendranathe.github.io/tailor-resume.html`

- [ ] **Step 1: Start a local static server**
- [ ] **Step 2: Verify homepage on desktop**
- [ ] **Step 3: Verify homepage on mobile**
- [ ] **Step 4: Verify case-study pages on desktop and mobile**
- [ ] **Step 5: Fix issues and re-run verification**
- [ ] **Step 6: Final commit**

## Self-Review

- Spec coverage: homepage IA, case-study routes, mobile behavior, design tone, content references, and SEO are represented in tasks above.
- Placeholder scan: there are no deferred `TODO` or `TBD` markers.
- Scope check: the work is one coherent static portfolio rebuild and can be implemented in this branch without separate sub-projects.

## Execution Handoff

Proceed with **Inline Execution** in this session using this plan as the implementation backbone.
