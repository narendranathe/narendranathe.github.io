# Backlog Critique-Loop Prompts

Self-contained, copy-pasteable prompts for driving the remaining backlog issues through the same critique loop used to ship #50 (favicon), #52 (canonical resume URL), and #57 (impact strips). Each prompt assumes a fresh session with zero prior context — paste it as the first message of a new conversation, optionally swap the model, and the loop runs.

The loop:

```
3 parallel pre-critique agents (distinct lenses)
        ↓
synthesize convergent + divergent findings
        ↓
implementation v1 (with structural / smoke tests)
        ↓
5 parallel post-critique agents (distinct lenses)
        ↓
refine to v2/v3 based on consensus
        ↓
commit + push + status comment on the GitHub issue
```

The framing across all five issues: **build for global adoption.** Every developer faces the same pain. The solution lives in this repo as a reference implementation and a copy-pasteable pattern (CSS module, doc, test runner) that any portfolio can adopt.

---

## Order of execution (recommended)

1. **#62 warm-referral campaign** — already scheduled. Lowest latency to interview loops.
2. **#64 first HN-eligible blog post** — pick *one* topic, ship it, cross-post to HN/Lobsters/dev.to. One front-page hit is the highest leverage move.
3. **#56 first architecture write-up** — overlaps with #64; the same post can satisfy both if framed right.
4. **#58 system diagrams** — feeds #56 and #64 (visual evidence inside the posts).
5. **#63 OSS PRs** — pursue *after* the blog post lands so the PR has a published context to link to.

---

## Shared context (paste into every session)

Every prompt below assumes the agent will load this context first:

- **Repo:** `narendranathe/narendranathe.github.io` (vanilla HTML/CSS/JS portfolio on GitHub Pages)
- **Branch:** `feat/portfolio-ui-upgrade-2026` (off `feat/portfolio-apex`)
- **PRD:** `specs/2026-04-28-portfolio-ui-upgrade-PRD.md` (v3 trimmed scope)
- **Already shipped on this branch:**
  - #50 — photo favicon (monogram tab + photo Apple-touch + OG image), commit `636ce1c`
  - #52 — `/static/resume.pdf` canonical URL + `/.well-known/resume.json` sidecar, commit `ae61f7f`
  - #57 — impact-strip ledger pattern on 5 flagship cards, commit `030e1c6`
- **Reference patterns to study before writing new ones:**
  - [`docs/impact-strip-pattern.md`](impact-strip-pattern.md) — drop-in pattern shape
  - [`scripts/snap-favicon.py`](../scripts/snap-favicon.py), [`snap-resume.py`](../scripts/snap-resume.py), [`test-portfolio.py`](../scripts/test-portfolio.py) — reproducibility + smoke-test conventions
  - `.github/workflows/resume-self-test.yml` — CI gate
- **Naren's targeting:** Senior+ AI/ML/Data Platform roles at H1B-sponsoring companies. Currently in Dallas TX. ExponentHR NL-to-SQL Architecture 4 was scrapped — DO NOT cite "400 enterprise clients", "40% support ticket reduction", "12s → 4s query response", "FAISS retrieval", or "catalog-driven NL-to-SQL" anywhere.
- **Recurring lessons from prior critique loops:**
  - Scope-creep is the default failure. Every "global adoption" doc/test is over-built before any external user exists.
  - Defensibility > AC compliance. If a stat / claim / link can't survive a 10-second follow-up question, cut it.
  - Visual hierarchy + palette consistency matter more than features. Two competing chip styles, off-brand colors, and competing typographic systems cost more recruiter trust than missing features.
  - Privacy: full ISO 8601 timestamps, PDF metadata, source-photo masters, and cumulative counters all leak signals. Round to dates, strip metadata, gitignore masters.

---

# Issue #62 — Warm-referral campaign

**Type:** Career-leverage move (not code). Highest priority by latency-to-interview.
**Already in flight:** scheduled remote agent fires the Day 1 briefing every weekday at 8 AM CDT.
**Goal:** 50 personalized notes to LinkedIn 2nd-degree contacts at 24 dream companies over 10 days. Target: 3-7 booked calls.

## Prompt to paste into a fresh session

```
You are continuing work on the narendranathe/narendranathe.github.io portfolio
branch feat/portfolio-ui-upgrade-2026. Read this whole prompt before doing anything.

Context (load before acting):
1. Read docs/backlog-critique-prompts.md "Shared context" section.
2. Read career-materials/warm-referral-tracker.md and warm-referral-templates.md
   on the local filesystem at ~/projects/career-materials/.
3. View GitHub issue #62 for the spec.

Your job: drive issue #62 (warm-referral campaign) through the critique loop.

PHASE 1 — 3 parallel pre-critique agents on the planned approach.
Pre-critique lenses (one agent per lens, dispatched in PARALLEL via three Agent
tool calls in a single message):

  Agent A (outreach-strategy): Will the proposed 5-per-day-for-10-days cadence
  produce 3-7 booked calls? What's the realistic reply rate at this volume for
  Senior+ AI roles at H1B-sponsoring firms? Is the 24-company list the right
  segment, or are there segments missing (Snowflake, NVIDIA mid-tier, AI
  startups Series B+, quant firms beyond the 6 named)?

  Agent B (list-quality + signal): For each of the 24 dream companies, what's
  the realistic 2nd-degree connection density Naren has on LinkedIn given his
  current network (Missouri S&T alumni + ExponentHR colleagues + HEC alumni +
  Substack readers)? Which 5 companies will he struggle to find a 2nd-degree
  contact at? What signals (recent posts, OSS commits, paper authorship)
  should he prioritize to identify high-quality targets?

  Agent C (message craft): The 5 templates (T1 mutual / T2 recent post / T3
  OSS / T4 company news / T5 conference) — are they distinct enough that
  recruiters who've read multiple of them won't pattern-match a template?
  What's the actual response-rate delta between a high-craft personalized
  note and a slightly-templated one?

PHASE 2 — synthesize convergence + divergence into an action plan v1.

PHASE 3 — execute Day 1 yourself: actually identify 5 target individuals,
draft 5 personalized notes using the templates, and update the tracker.
The tracker rows must have: company, target_person, LinkedIn URL, mutual
connection, strongest signal, template choice, draft message text. Write
the drafts to a NEW file career-materials/day-1-drafts.md — do not send.

PHASE 4 — 5 parallel post-critique agents on the 5 drafted messages:
  Agent D (response-rate realism): grade each of 5 messages 1-10 on
  likelihood-to-reply. What's wrong with the lowest-graded one?
  Agent E (scaling): if Days 2-10 follow this pattern, will Naren run out
  of strong signals by day 4? What's the contingency for "no good 2nd-degree
  contact at company X"?
  Agent F (follow-up discipline): the templates have one 7-day follow-up;
  is that enough? Too much? What's the right follow-up cadence for
  Anthropic-tier targets vs Citadel-tier vs JPM-tier?
  Agent G (sponsorship segment): for H1B-sponsoring vs visa-rigid companies,
  should the message text differ? Should H1B status be mentioned in the
  first message or held until the call?
  Agent H (energy budget): rejection-tolerance is the rate-limiter on this
  campaign. What's the realistic emotional cost of 5 cold messages per day
  for 10 days, and what discipline patterns prevent burnout by day 6?

PHASE 5 — refine the 5 drafts based on convergent post-critique findings.
Save final drafts to career-materials/day-1-drafts-v2.md.

PHASE 6 — commit career-materials/* changes (no PR, no push of personal
data; commit locally only and report the diff to the user).

Constraints:
- Naren's emotional/time budget is real. Limit phase 3 to 5 message drafts,
  not 50.
- Privacy: do NOT publish the warm-referral-tracker or any drafted messages
  to a public branch. They live in career-materials/ which is local-only.
- Do not contact any actual recruiter; only draft messages for human review.
- Defensibility: every reference to a specific person's recent post / OSS
  commit must be verifiable (link to the source). No fabricated context.

Output: a status comment on issue #62 summarizing pre-critique consensus,
post-critique consensus, and "Day 1 ready — Naren reviews and sends today."
```

---

# Issue #56 — Architecture & Write-Ups (1-2 deep technical posts)

**Type:** Content. Highest senior-signal item per strategist.
**Goal:** Ship 1 long-form post (1500-2500 words) cross-posted to HN/Lobsters/dev.to/Substack. Each post follows Problem → Constraints → Design → Tradeoffs → Outcome.

## Prompt to paste into a fresh session

```
You are continuing work on the narendranathe/narendranathe.github.io portfolio
branch feat/portfolio-ui-upgrade-2026. Read this whole prompt before doing anything.

Context (load before acting):
1. Read docs/backlog-critique-prompts.md "Shared context" section.
2. View GitHub issue #56 for the spec.
3. Read C:\Users\naren\.claude\projects\c--Users-naren-projects\memory\
   resume_master_profile.md and project_autoapply_qa_phase7.md to ground in
   the actual production work.

Your job: drive issue #56 (1-2 architecture write-ups) through the critique
loop. THIS PR ships ONE post (the second is a follow-up issue if time
remains). Pick the strongest topic between:

  (1) "AutoApply AI: provider-fallback architecture" — multi-LLM cascade,
      Chrome MV3 Shadow DOM, RAG with pgvector + TF-IDF, category-routed
      model selection, prompt-cache hit rates, 11 ATS adapters
  (2) "repo-context-hooks: supply-chain hardening for Claude Code skills" —
      Sigstore signing + CodeQL + Dependabot, OIDC PyPI publishing, telemetry
      hot paths under property tests, the 5-critic agent review workflow
  (3) "Real-time portfolio risk: Kafka producer + Spark consumer split" —
      ingest topology, p95 latency, dashboard backpressure, multi-process
      Streamlit deployment

PHASE 1 — 3 parallel pre-critique agents.
Lenses:
  Agent A (technical rigor): which of (1)/(2)/(3) has the deepest defensible
  technical content? Where's the "tradeoffs" section going to land — what
  did Naren actually try that didn't work? If a topic has no honest "what
  didn't work", it's a tutorial not a write-up; flag it.

  Agent B (narrative arc): which topic has the strongest 5-line abstract
  for a recruiter who reads the first 200 chars and decides? Score each
  topic's "lede" potential.

  Agent C (HN front-page readiness): for each of (1)/(2)/(3), what's the
  HN title that gets it to the front page? What's the contrarian angle
  (not just "we built X" but "we tried Y and it failed because Z")? Score
  each topic 1-10 on HN-front-page-likelihood given current AI-engineering
  zeitgeist.

PHASE 2 — synthesize. Pick the winning topic with reasoning.

PHASE 3 — write the post v1 to content/posts/<slug>.html (~1500-2500
words). Structure: Problem → Constraints → Design → Tradeoffs → Outcome.
Include 1-2 inline SVG diagrams (these will become the F-SD/#58 deliverable
later or can be added in this PR). Cross-link the post from index.html
in a new "Architecture & Write-Ups" section between Systems and Writing.
Add structural test in scripts/test-portfolio.py asserting the post exists
+ has all 5 sections + word count >= 1500.

PHASE 4 — 5 parallel post-critique agents on the drafted post:
  Agent D (technical correctness): every claim, line of code, citation —
  pressure-test as if interviewing the author. What's hand-wavy?
  Agent E (narrative arc): pacing, readability, lede strength. Where does
  a tired recruiter bounce?
  Agent F (HN-frontpage realism): score 1-10 on HN front-page likelihood.
  What's the title that would land it? What's the optimal submission day/time?
  Agent G (ego / honest tradeoffs): does the "Tradeoffs" section honestly
  show what failed? Or is it victory-lap hand-waving? Senior engineers
  notice immediately if the tradeoffs are sanitized.
  Agent H (opportunity-cost): given this is 8-12 hours of writing, did the
  topic choice maximize career leverage vs alternatives? Should the post
  have been on a different topic that recruiters at Anthropic actually
  search for?

PHASE 5 — refine to v2 based on consensus. Aim for "would I share this
on Twitter under my real name?" quality.

PHASE 6 — commit + push. Submit the post to HN with the agreed title at
the optimal time, cross-post to Lobsters / dev.to / Substack. Track HN
karma + cross-post views in the issue thread for 7 days.

Constraints:
- 1 post in this PR. Second post is a follow-up issue.
- Word budget: 1500-2500. Anything over 2500 must be cut.
- Tradeoffs section is mandatory and honest. No "we considered X but
  chose Y because..." hand-waves. Real tradeoffs only.
- DO NOT reference ExponentHR NL-to-SQL Architecture 4 in any form.
- Inline SVG diagrams MUST follow the impact-strip-pattern conventions
  (warm token palette, dark-mode + print blocks, accessible <title>/<desc>).

Output: status comment on issue #56 summarizing pre-critique winning-topic
choice, post-critique consensus, HN submission link + karma at hour 6,
hour 24, hour 72.
```

---

# Issue #58 — System Diagrams (AutoApply AI + Portfolio-Risk inline SVG)

**Type:** Visual asset that compounds. Diagrams feed write-ups + interviews + recruiter screenshare.
**Goal:** Two inline SVG architecture diagrams, accessible, dark/light/print-aware.

## Prompt to paste into a fresh session

```
You are continuing work on the narendranathe/narendranathe.github.io portfolio
branch feat/portfolio-ui-upgrade-2026. Read this whole prompt before doing anything.

Context (load before acting):
1. Read docs/backlog-critique-prompts.md "Shared context" section.
2. View GitHub issue #58 for the spec.
3. Read docs/impact-strip-pattern.md to understand the established pattern
   conventions (warm tokens, dark-mode + print blocks, accessibility).

Your job: drive issue #58 (system diagrams) through the critique loop.

The diagrams (two required):
  (D1) AutoApply AI architecture — Chrome MV3 Floating Panel + Sidepanel →
       FastAPI backend → multi-LLM provider cascade → Supabase pgvector →
       GitHub Vault
  (D2) Portfolio-Risk Real-time topology — Kafka producer → Spark consumer →
       FastAPI API → Streamlit dashboard

PHASE 1 — 3 parallel pre-critique agents.
Lenses:
  Agent A (SVG craft): inline SVG vs external file vs <object>? Hand-rolled
  vs Excalidraw export + svgo + manual cleanup? What's the right size
  budget per diagram (current target: ~10-20KB inline)?

  Agent B (a11y): each diagram needs <title>, <desc>, role="img", and a
  visually-hidden text alternative for screen readers. What's the right
  level of <desc> detail? Diagrams must respect prefers-color-scheme
  (currentColor for fills/strokes) and print stylesheet (no bg color
  loss). What's the SR-friendly equivalent of "arrow A → B"?

  Agent C (system-correctness): both topologies must be technically accurate
  and defensible under interview pressure. For AutoApply AI: is the actual
  ATS Score path through pgvector RAG real? Is "GitHub Vault" the canonical
  name for the resume-storage repo or marketing? For Portfolio-Risk: are the
  Kafka partition counts / Spark consumer parallelism / Streamlit deployment
  details accurate to what's actually in the repo, or simplified for
  diagram clarity?

PHASE 2 — synthesize, lock the technical facts before drawing.

PHASE 3 — implement.
- Author each diagram as inline <svg> placed in:
  * content/posts/<slug>.html (the architecture write-up that links to it)
  * AND the home index.html project card (linked + embedded thumbnail)
- Use currentColor / CSS custom properties for stroke + fill so dark mode
  + print work without a separate copy.
- Add a reusable .system-diagram CSS class to styles.css covering: svg
  responsiveness, accessibility focus indicator, text typography.
- Author docs/system-diagram-pattern.md (~150 lines) — drop-in convention
  for any portfolio: HTML + CSS + accessibility + dark/print blocks.
- Add 4 structural assertions to scripts/test-portfolio.py:
  * inline <svg> present in both target locations
  * each <svg> has <title> + <desc>
  * each <svg> uses currentColor (no hardcoded #hex on fills/strokes)
  * total inline SVG byte budget per page <= 30KB

PHASE 4 — 5 parallel post-critique agents on the implementation:
  Agent D (visual taste): are the diagrams Stripe/Linear-tier (clean
  geometric shapes, consistent stroke weights, balanced whitespace) or
  do they read as Excalidraw exports?
  Agent E (a11y): pressure-test the SR experience. What does NVDA / VoiceOver
  announce on each diagram? Is the SR alternative-text equivalent in
  information density to a sighted user reading the diagram?
  Agent F (technical accuracy): re-pressure-test the topology claims.
  Anything subtly wrong? Anything an interviewer at Databricks would
  call hand-wavy?
  Agent G (portability for adopters): can a Hugo / Astro / Next.js dev
  copy the .system-diagram CSS + inline <svg> template into their
  portfolio with under 10 minutes of work? What friction is in the way?
  Agent H (scope check): did the implementation creep beyond #58? Are
  the structural tests proportionate or padded? Are 4 assertions the
  right count?

PHASE 5 — refine to v2 based on consensus.

PHASE 6 — commit + push + status comment on #58.

Constraints:
- Two diagrams, no more (Naren has limited diagram-time budget).
- Inline SVG only (no <img>, no PNG fallback for the diagram body).
- Both diagrams MUST validate against the existing impact-strip palette
  (--accent-warm for highlights, --fg/--fg-muted for typography).
- Diagrams must look clean printed in B&W (test with browser print preview).
- DO NOT include the scrapped ExponentHR NL-to-SQL diagram.

Output: status comment on issue #58 with screenshots of both diagrams +
test count + post-critique consensus + size-budget actuals.
```

---

# Issue #63 — 2 OSS PRs to dream-company-adjacent repos

**Type:** Career-leverage move. Durable indexed signal in commit graphs.
**Goal:** 2 substantive PRs opened (not necessarily merged) on anthropic-cookbook / pgvector / mlflow / streamlit / databricks/dbrx. Maintainer engagement is the success signal.

## Prompt to paste into a fresh session

```
You are continuing work on the narendranathe/narendranathe.github.io portfolio
branch feat/portfolio-ui-upgrade-2026. Read this whole prompt before doing
anything.

Context (load before acting):
1. Read docs/backlog-critique-prompts.md "Shared context" section.
2. View GitHub issue #63 for the spec.
3. Read C:\Users\naren\.claude\projects\c--Users-naren-projects\memory\
   project_autoapply_qa_phase7.md to ground in real production AI work.

Your job: drive issue #63 (2 OSS PRs) through the critique loop. ONE PR
shipped in this PR; second PR is follow-up if energy remains.

Target repository priority (filed for analysis, will be re-ranked by critics):
  (R1) anthropics/anthropic-cookbook — direct dream company contribution
  (R2) anthropics/courses — same
  (R3) pgvector/pgvector — Naren has hands-on RAG experience; well-known maintainer
  (R4) mlflow/mlflow — Databricks-adjacent
  (R5) streamlit/streamlit — Naren ships Streamlit apps
  (R6) databricks/dbrx — Databricks ML community

PHASE 1 — 3 parallel pre-critique agents.
Lenses:
  Agent A (maintainer-receptivity): for each of R1-R6, browse the Issues +
  Pull Requests + recent merges. Who's actively reviewing? What's the
  current "good first issue" / "help wanted" backlog? Which repos have
  maintainers who merge community PRs within 2 weeks vs sit on them for
  months? Score each repo 1-10 on PR-merge-likelihood.

  Agent B (PR scope): given Naren's actual production work (AutoApply AI,
  tailor-resume, repo-context-hooks), what's the most credible PR scope
  per repo? Cookbook: prompt-caching benchmarks across long-context
  workloads using AutoApply AI as the workload? pgvector: RAG benchmark
  / docs improvement based on his pgvector usage in autoapply-ai? Pick
  the 2 highest-leverage scopes.

  Agent C (signal vs noise): a 5-line documentation typo PR is durable
  signal but low-effort. A 500-line feature PR is high-effort but
  probably won't merge. What's the right scope for "maximum signal per
  hour"? Score each prospective PR scope on signal-density.

PHASE 2 — synthesize. Pick the winning repo + PR scope. Lock the scope
to a 5-15 hour effort (not weeks).

PHASE 3 — open the PR. Steps:
- Fork the repo into Naren's GitHub account.
- Read CONTRIBUTING.md cover-to-cover.
- Open a GitHub Discussion or Issue first describing the proposal —
  confirm maintainer interest before investing PR time.
- Once green-lit, open the PR with: clear motivation, before/after
  benchmarks (if perf), tests, doc updates.
- LinkedIn post announcing the PR (signal amplification, costs nothing).

PHASE 4 — 5 parallel post-critique agents on the PR draft:
  Agent D (technical quality): pressure-test the PR as if you're the
  maintainer doing code review. What's wrong, what's hand-wavy, what
  needs a test?
  Agent E (merge-likelihood): what's the realistic probability this PR
  merges within 4 weeks? What blocks it? Is there a contingency PR scope
  that's smaller and more likely to merge?
  Agent F (dream-company routing): does this PR meaningfully signal at
  Anthropic / Databricks / Stripe specifically? Or is it generic OSS
  contribution noise that won't surface to a hiring manager's attention?
  Agent G (public amplification): is the LinkedIn announcement the only
  amplification surface? What about a blog post connecting the PR to
  Naren's prior work? Cross-pollinate with #56 (write-ups)?
  Agent H (time budget): the original scope was 5-15 hours; what's the
  realistic actual hours given the maintainer-feedback loop? Should
  Naren cap at 20 hours and bail if no merge signal by then?

PHASE 5 — refine the PR description / code per consensus, push to
the upstream PR.

PHASE 6 — comment on issue #63 with PR URL + maintainer-response status
+ next-step plan.

Constraints:
- 1 PR opened in this PR (issue). 2nd PR is follow-up issue.
- Effort cap: 15 hours per PR. Bail if no review signal within 2 weeks.
- Open a Discussion / Issue FIRST. Do NOT open a PR cold without
  maintainer pre-engagement on a non-trivial scope.
- DO NOT reference ExponentHR NL-to-SQL.
- The PR description should link to relevant Naren artifacts: tailor-
  resume PyPI page, AutoApply AI live URL, repo-context-hooks if a
  supply-chain PR. Bidirectional context = recruiters who land on the
  PR can find Naren's work.

Output: status comment on #63 with: chosen repo + scope rationale,
PR URL, maintainer first-response timing, next steps for PR #2.
```

---

# Issue #64 — 3 HN-eligible blog posts cross-posted to Lobsters / dev.to

**Type:** Content. Compounds over time via SEO long-tail + indexed inbound.
**Goal:** 1 long-form post (1500-2500 words) shipped + cross-posted in this PR. 2 more in follow-up issues.

## Prompt to paste into a fresh session

```
You are continuing work on the narendranathe/narendranathe.github.io portfolio
branch feat/portfolio-ui-upgrade-2026. Read this whole prompt before doing
anything.

Context (load before acting):
1. Read docs/backlog-critique-prompts.md "Shared context" section.
2. View GitHub issue #64 for the spec.
3. If issue #56 (architecture write-ups) is also open, decide whether
   THIS PR's post can satisfy both #56 AND #64 — typically yes, since
   the architecture write-up IS the HN-eligible post.

Your job: drive issue #64 (3 HN-eligible posts) through the critique
loop. ONE post shipped in this PR; 2 are follow-up issues.

Topic priority (will be re-ranked by critics):
  (T1) "Why we cascade Claude → GPT-4o → Kimi → Ollama (and what it costs)"
       — multi-LLM provider routing in Chrome MV3, with real cost +
         latency numbers
  (T2) "Supply-chain hardening for Claude Code skills: Sigstore + CodeQL +
       Trusted Publisher" — repo-context-hooks v1.0 launch post, fresh
       and novel
  (T3) "Field-detection in a Chrome MV3 extension: Strategy C vs TriObserver"
       — already partly written in /field-detection-audit skill output;
         lowest-effort
  (T4) "Catalog-driven retrieval for HR analytics" — DROPPED, this
       referenced ExponentHR NL-to-SQL which is scrapped

PHASE 1 — 3 parallel pre-critique agents.
Lenses:
  Agent A (title craft + HN front-page strategy): for each of T1/T2/T3,
  draft 3 candidate titles. Score each on HN-frontpage-likelihood given
  the current AI engineering zeitgeist (Q2 2026). Best titles are
  contrarian, specific, numerical. "How prompt-caching saved 73% on
  a multi-LLM autoapply loop" beats "AutoApply AI architecture deep dive."

  Agent B (content novelty): is the topic genuinely new contribution, or
  recapitulation of existing posts? Search HN, Lobsters, dev.to for
  recent (last 90 days) posts on similar topics. Where's the gap?

  Agent C (submission timing + audience match): for each topic, who's
  the ideal HN audience? What's the optimal submission day/time? What
  cross-posts amplify (Lobsters? r/MachineLearning? dev.to? Substack
  via Naren's existing audience)?

PHASE 2 — synthesize. Pick the winning topic + title + submission strategy.

PHASE 3 — write the post v1 to content/posts/<slug>.html (1500-2500 words)
following the same Problem → Constraints → Design → Tradeoffs → Outcome
template as #56. Include real numbers (latency, cost, throughput) with
defensible source attribution. Embed inline SVG diagrams if relevant
(reuses #58 work). Cross-link from the home index.html "Architecture &
Write-Ups" section.

PHASE 4 — 5 parallel post-critique agents:
  Agent D (writing quality): pacing, voice, paragraph structure, code-block
  formatting. Where does the post drag? Where does it lose a tired reader?
  Agent E (HN-frontpage realism): score 1-10 on front-page likelihood with
  the chosen title and timing. What 2 factors would push it from 5/10 to
  8/10?
  Agent F (cross-post strategy): is "submit to HN at 9am EST Monday"
  the optimal play, or is "Lobsters first, then HN if it gains traction"
  better? Should there be a delay between platforms? Should Naren post
  it as a comment-thread starter on r/MachineLearning?
  Agent G (SEO long-tail): what queries does this post rank for in 6
  months? Are the title keywords correctly optimized for inbound search
  traffic from recruiters? Are there missed long-tail opportunities?
  Agent H (reputation risk): is there ANYTHING in this post that could
  damage Naren's reputation if it goes viral? Hot-take that he'll regret?
  Misattributed credit? Comparison that punches at a person rather than
  a system?

PHASE 5 — refine to v2 based on consensus.

PHASE 6 — submit:
  1. Cross-post to dev.to + Lobsters + Substack (if Naren has one) at
     non-conflicting times.
  2. Submit to HN with the chosen title at the chosen time.
  3. LinkedIn post linking the HN submission.
  4. Track karma at hour 6, hour 24, hour 72 in the issue thread.

PHASE 7 — commit + push + status comment on #64.

Constraints:
- 1 post in this PR. 2 more posts are follow-up issues.
- Word budget: 1500-2500. Real numbers required.
- Tradeoffs section MUST include what didn't work, not just what shipped.
- DO NOT reference ExponentHR NL-to-SQL.
- The post must be cross-postable (no platform-specific markup that
  breaks on dev.to or Lobsters).

Output: status comment on #64 with: chosen topic + title rationale,
HN submission URL + karma timeline, dev.to / Lobsters / LinkedIn links,
post-critique consensus.
```

---

# Wave 2 — Flow Enhancements (PRD #66, child issues #67–#71)

After the user reviewed the live preview of #50 / #52 / #56 / #57 / #58, three new feature requests + one bug fix were filed as PRD #66 and decomposed into 5 vertical-slice issues:

- **#67** — M2 tracer bullet: resume page-1 preview asset pipeline (S, blocks #70)
- **#68** — M4: ExponentHR claim scrub + DOM-aware test guard (S, parallel-safe)
- **#69** — M3: full-body hero photo swap (M, parallel-safe)
- **#70** — M1: hover-preview primitive on resume + key links (L, blocked by #67, blocks #71)
- **#71** — M5: skills image grid with hover tooltips (L, blocked by #70)

Recommended order: **#67 → #68 + #69 (parallel) → #70 → #71**.

Each prompt below is self-contained for a fresh session in the repo root.

---

## Prompt 6 — Issue #67 (M2 tracer bullet — resume preview asset)

> Smallest end-to-end change. Proves the asset-generation pipeline. ≤ 1 hour.

```
---BEGIN PROMPT---
You are working on the narendranathe/narendranathe.github.io portfolio,
branch feat/portfolio-ui-upgrade-2026. Working directory is the repo root.

Drive GitHub issue #67 (M2 — resume page-1 preview asset pipeline,
TRACER BULLET) through the critique loop documented in this file.

Steps:
1. Read docs/backlog-critique-prompts.md "Shared context" + the
   "Issue #67" full spec via `gh issue view 67`.
2. Three pre-critique agents in PARALLEL (one Agent tool call message
   with three sub-calls):
   Agent A (rendering toolchain): pikepdf vs pdf2image vs Pillow's
   built-in. Which is cross-platform-stable on Windows + Linux + macOS
   without poppler bundled? What's the determinism property of each
   (same PDF bytes -> identical PNG bytes)?
   Agent B (asset-format choice): is 320x240 PNG the right shape for
   a hover-preview thumbnail, or does a portrait 240x320 (matching
   resume aspect ratio) read better in a hover popover? Should it be
   AVIF / WebP for size, or PNG for compatibility?
   Agent C (cache-bust + reproducibility): the resume sidecar already
   has version_hash from #52. Should the preview filename embed the
   hash (resume-page1-preview.<hash>.png) or be a stable name with
   ?v=<hash> in markup? What's the simpler maintenance path?
3. Synthesize convergent findings.
4. Implement: extend scripts/snap-resume.py with a render_page1_preview
   function. Output static/resume-page1-preview.png (target <=30KB).
   Self-test extended: assert preview exists, byte size, dimensions.
5. 5 post-critique agents in PARALLEL:
   Agent D (deterministic encoding): is the PNG output byte-stable
   across runs? What encoder flags are needed?
   Agent E (cross-platform): does it work on a fresh Windows clone
   without poppler? On a CI Linux runner?
   Agent F (size budget): 30KB target — actuals?
   Agent G (a11y for downstream M1): what alt text / aria-label should
   the eventual hover-preview-card use? Is the image decorative or
   semantically meaningful (deserves description)?
   Agent H (scope discipline): did the implementation stay scoped to
   "render + write PNG", or did it accidentally creep into M1 hover-
   preview UI work that belongs in #70?
6. Refine + commit + push + status comment on #67.

Constraints:
- ≤ 1 hr realistic effort. Bail if pikepdf rendering doesn't work and
  pdf2image needs system binaries — document the fallback in the issue
  comment and ship a manually-rendered PNG as committed artifact.
- Self-test must run with stdlib only (no poppler dep at test time).
- Output PNG must NOT contain PDF metadata leakage (use the
  metadata-stripped resume.pdf as input, not the raw source).

You have authorization to: read all files, run gh CLI, dispatch
parallel Agent tool calls, modify scripts/snap-resume.py and
scripts/requirements.txt, commit + push.
---END PROMPT---
```

---

## Prompt 7 — Issue #68 (M4 — ExponentHR scrub + DOM-aware test guard)

> Smallest scope. Removes one HTML block + adds ~30 LOC test helper. ≤ 1 hour.

```
---BEGIN PROMPT---
You are working on the narendranathe/narendranathe.github.io portfolio,
branch feat/portfolio-ui-upgrade-2026. Working directory is the repo root.

Drive GitHub issue #68 (M4 — ExponentHR claim scrub + DOM-aware test
guard) through the critique loop documented in this file.

Background: line 144 of index.html has
  <span class="metric-num" data-count="400">400</span>
  <span class="metric-lbl">enterprise clients</span>
which is the scrapped ExponentHR NL-to-SQL claim. The current test
guard greps the raw HTML for "400 enterprise client" but never matches
because the words live in adjacent spans. Fix the leak AND fix the
guard.

Steps:
1. Read docs/backlog-critique-prompts.md "Shared context" + `gh issue
   view 68` for the full spec.
2. Three pre-critique agents in PARALLEL:
   Agent A (DOM-walker correctness): the proposed extract_visible_text
   helper subclasses html.parser.HTMLParser. What edge cases will trip
   it? <script>/<style> inline content, HTML entities (&amp;, &rarr;),
   self-closing tags, CDATA?
   Agent B (forbidden phrase list completeness): the PRD lists 6
   phrases. Are there others ("400 client", "40% reduction", "4 second
   query") that should be in the guard? What's the right inclusion
   bar?
   Agent C (false-positive risk): could the substring search trigger
   on legitimate text — e.g., "400 milliseconds" in a different
   context? How to scope the assertion to avoid false positives?
3. Synthesize.
4. Implement:
   - Remove the <div class="metric-item"> for "400 enterprise clients"
     (lines 142-146 of index.html).
   - Add extract_visible_text() helper to scripts/test-portfolio.py.
   - Add new test test_no_scrapped_exponenthr_outcomes_in_rendered_text.
   - Verify all 28+ existing assertions still pass.
5. 5 post-critique agents in PARALLEL:
   Agent D (regression prevention): plant 3 deliberate violations in
   a fixture HTML and confirm the new test catches all 3.
   Agent E (whitespace handling): does multi-space / newline-split
   text get normalized correctly?
   Agent F (test runtime): the helper walks the entire index.html
   tree on every CI run. Is the perf cost acceptable (<500ms)?
   Agent G (false-positive sweep): run the new guard against the
   live HTML — does it flag anything legitimate that needs an
   exception?
   Agent H (defense-in-depth): should the existing raw-HTML regex
   guard stay (additive) or be removed (replaced)?
6. Refine + commit + push + status comment on #68.

Constraints:
- No new runtime deps (use stdlib html.parser only).
- The new test must complete in <500ms on CI.
- Existing scrapped-phrase list stays a module constant for easy
  future additions.

You have authorization to: read all files, run gh CLI, dispatch
parallel Agent tool calls, modify index.html and scripts/test-
portfolio.py, commit + push.
---END PROMPT---
```

---

## Prompt 8 — Issue #69 (M3 — hero photo swap)

> Image swap + CSS layout integration. ~2 hours.

```
---BEGIN PROMPT---
You are working on the narendranathe/narendranathe.github.io portfolio,
branch feat/portfolio-ui-upgrade-2026. Working directory is the repo root.

Drive GitHub issue #69 (M3 — replace hero close-up with full-body shot,
Yerradouani-style integration) through the critique loop.

Steps:
1. Read docs/backlog-critique-prompts.md "Shared context" + `gh issue
   view 69` for the full spec.
2. Three pre-critique agents in PARALLEL:
   Agent A (layout integration): full-body shot is 1200px tall, hero
   column is constrained. Best layout: bottom-anchor + object-fit
   cover + soft top-fade mask, OR a separate "wraps the hero text"
   composition? Reference the Yerradouani site at yerradouani.me for
   visual cue.
   Agent B (mobile UX): on 320px viewport, does the full-body shot
   crowd the hero text + metric-grid + CTA buttons? Should mobile
   hide the photo entirely, or scale it down + reposition?
   Agent C (image weight + LCP): static/originals/headshot-fullbody.jpg
   is 66KB at 1200px long-edge. Will inlining as the hero LCP element
   regress the Lighthouse LCP score (target <1.8s on Slow 4G)?
   Should we generate a lower-resolution variant for mobile?
3. Synthesize.
4. Implement:
   - Modify index.html lines 130-141: replace external GitHub-asset
     URLs with local static/originals/headshot-fullbody.jpg.
   - Possibly remove the hero-photo-inset entry (designer's call).
   - Modify styles.css .hero-photo-stack: bottom-anchor + soft top-
     fade mask via mask-image.
   - Add mobile breakpoint <=780px adjustments.
   - Add loading="eager" + width/height attributes for CLS=0.
5. 5 post-critique agents in PARALLEL:
   Agent D (visual taste): does the new hero look "polished, intentional"
   or "trying too hard"? Compare to current state.
   Agent E (mobile rendering): test at 320px / 375px / 412px / 768px;
   does the photo break any layout?
   Agent F (CLS): with declared dims + eager-loaded image, is CLS=0?
   Run Lighthouse, confirm.
   Agent G (a11y): is alt text descriptive without being verbose?
   Does the photo block any keyboard focus path?
   Agent H (scope discipline): did the implementation only touch
   hero CSS, or did it accidentally cascade into other layout breakage?
6. Refine + commit + push + status comment on #69.

Constraints:
- Image MUST come from static/originals/ (no external CDN refs).
- LCP delta <=200ms; if it regresses more, generate a lower-res
  variant.
- Mobile must not horizontal-scroll.

You have authorization to: read all files, run gh CLI, dispatch
parallel Agent tool calls, modify index.html and styles.css,
generate a lower-res image variant if needed (via Pillow in a
one-off script), commit + push.
---END PROMPT---
```

---

## Prompt 9 — Issue #70 (M1 — hover-preview primitive)

> Reusable popover state machine + ARIA + mobile fallback. ~6 hours. Run AFTER #67 ships.

```
---BEGIN PROMPT---
You are working on the narendranathe/narendranathe.github.io portfolio,
branch feat/portfolio-ui-upgrade-2026. Working directory is the repo root.

PRECONDITION: issue #67 must be closed and static/resume-page1-preview.png
must exist on the branch. If not, drive #67 first.

Drive GitHub issue #70 (M1 — hover-preview primitive) through the
critique loop.

Steps:
1. Read docs/backlog-critique-prompts.md "Shared context" + `gh issue
   view 70` for the full spec.
2. Three pre-critique agents in PARALLEL:
   Agent A (state machine design): hover-intent timing (150ms open,
   200ms grace), focus tracking across DOM siblings, single shared
   card vs per-trigger cards. Vanilla JS or use the native HTML
   <dialog> element + popover API (Chrome 114+, Safari 17+, Firefox
   125+)? What's the cross-browser support story for the popover API
   in 2026?
   Agent B (popover ARIA pattern): the spec says role="dialog" +
   aria-modal="false" + aria-haspopup="dialog". Is "dialog" the right
   pattern, or should it be "tooltip" (lighter), or the new HTML
   "popover" (declarative)? What does NVDA/VoiceOver actually
   announce for each?
   Agent C (mobile UX): tap-to-toggle vs always-visible vs long-press.
   Tap-then-tap-again-to-download is non-standard and may confuse;
   would a mobile-only "Preview" button next to the link be cleaner?
3. Synthesize.
4. Implement:
   - Create docs/hover-preview-pattern.md (~150 LOC).
   - Append CSS module to styles.css (~80 LOC).
   - Append JS state machine to app.js (~120 LOC).
   - Annotate 4 resume link sites + 2 contact icons (GitHub, LinkedIn)
     in index.html with data-hover-preview / data-hover-title /
     data-hover-caption attributes.
   - Generate static/preview-github.png and static/preview-linkedin.png
     (~30KB each, manually captured screenshots).
   - Extend scripts/test-portfolio.py with new structural assertions.
5. 5 post-critique agents in PARALLEL:
   Agent D (a11y): full WCAG 1.4.13 pressure-test (dismissible,
   hoverable, persistent). Keyboard navigation end-to-end.
   Agent E (mobile UX): tap-to-preview + tap-card-to-download
   pattern actually intuitive on iPhone Safari + Android Chrome?
   Agent F (cross-browser): test on latest 2 versions of Chrome /
   Safari / Firefox / Edge. Any popover quirks?
   Agent G (scope creep): did the implementation stay scoped to the
   primitive + 6 link sites, or did it bleed into M5 skills tooltip
   work?
   Agent H (test coverage): are the new structural assertions
   sufficient, or are there gaps (e.g., asserting card lazy-loads,
   asserting Esc key handling)?
6. Refine + commit + push + status comment on #70.

Constraints:
- No new runtime JS deps. Vanilla DOM APIs only.
- Pattern must be drop-in for adopters (CSS custom property override
  surface).
- Reduced-motion users get snap-open / snap-close (no fade).

You have authorization to: read all files, run gh CLI, dispatch
parallel Agent tool calls, modify index.html / styles.css / app.js /
scripts/test-portfolio.py / docs/, generate static/preview-*.png,
commit + push.
---END PROMPT---
```

---

## Prompt 10 — Issue #71 (M5 — skills image grid)

> New section + 25-30 logos + tooltip pattern. ~6 hours. Run AFTER #70 ships.

```
---BEGIN PROMPT---
You are working on the narendranathe/narendranathe.github.io portfolio,
branch feat/portfolio-ui-upgrade-2026. Working directory is the repo root.

PRECONDITION: issue #70 must be closed and the hover-preview primitive
must be available in app.js + styles.css. If not, drive #70 first.

Drive GitHub issue #71 (M5 — skills image grid) through the critique
loop.

Steps:
1. Read docs/backlog-critique-prompts.md "Shared context" + `gh issue
   view 71` for the full spec.
2. Three pre-critique agents in PARALLEL:
   Agent A (logo sourcing + licensing): devicons.dev (OFL) covers
   most. What's the right approach for Anthropic Claude logo (brand
   guidelines)? Microsoft Fabric? Should ambiguous-license logos
   become text-monogram glyphs? Is monochrome (currentColor) rendering
   the right tradeoff for visual cohesion?
   Agent B (category structure): 5 categories x 4-6 logos. Is the
   category split ideal (Languages / Data Platforms / LLM Stack /
   Infra / Observability), or do "LLM Stack" and "Data Platforms"
   overlap awkwardly (FAISS, pgvector)? Should there be a "Tools /
   IDEs" category?
   Agent C (tooltip pattern reuse): M1 hover-preview is heavyweight
   (popover dialog). For 25-30 small icons, would a simpler
   aria-describedby + visually-hidden span be better, OR does
   reusing M1 give visual consistency? Tradeoff: code-reuse vs
   weight.
3. Synthesize.
4. Implement:
   - Source 25-30 logo SVGs (devicons.dev preferred), SVGO-minimize.
   - Create static/skills/<name>.svg files.
   - Insert <section id="skills"> in index.html between Track Record
     and What Shipped.
   - Append .skills-grid CSS module to styles.css.
   - Add nav link "Stack" between "Experience" and "Projects".
   - Create docs/skills-grid-pattern.md (~150 LOC).
   - Extend scripts/test-portfolio.py with structural assertions
     (section presence, icon count per category, byte budget per
     icon, no external CDN refs).
5. 5 post-critique agents in PARALLEL:
   Agent D (visual taste): does the grid read as "elegant + intentional"
   or "CV gimmick"? If gimmick, switch to monochrome.
   Agent E (a11y): every icon keyboard-focusable with aria-label?
   Tooltip announces correctly via NVDA / VoiceOver?
   Agent F (page weight): total byte delta <= 60KB? (Aim for ~2KB
   per icon after SVGO.)
   Agent G (mobile rendering): grid wraps cleanly on 320px? Tooltips
   show inline (not as popover)?
   Agent H (brand consistency): does the new section integrate with
   the rest of the portfolio's warm-palette + JetBrains-mono +
   Playfair aesthetic, or does it stand out as a foreign component?
6. Refine + commit + push + status comment on #71.

Constraints:
- All icons LOCAL (no external CDN refs in skills section).
- SVG icons must use currentColor for fills/strokes (dark-mode
  compatible).
- Total page-weight delta <=60KB.
- Pattern doc matches docs/impact-strip-pattern.md conventions.

You have authorization to: read all files, run gh CLI, dispatch
parallel Agent tool calls, fetch logos from devicons.dev (curl/wget),
write to static/skills/, modify index.html / styles.css / scripts/
test-portfolio.py / docs/, commit + push.
---END PROMPT---
```

---

## Meta-prompt: how to run any of these

If a session is starting cold, paste the relevant block above. If continuing
work in the current branch, additionally include:

```
Skip "Shared context" load — already done in this session. Pick up at PHASE N.
```

If the user wants to skip the critique loop and just ship, paste:

```
Drop the critique loop entirely. Read the issue spec and ship a minimum-
viable implementation. Skip docs, skip tests beyond a single smoke test,
skip the global-adoption framing. This is YAGNI mode.
```

But the YAGNI mode short-circuits the whole point of these prompts. Use it
sparingly.
