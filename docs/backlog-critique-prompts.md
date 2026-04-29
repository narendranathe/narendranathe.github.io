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
