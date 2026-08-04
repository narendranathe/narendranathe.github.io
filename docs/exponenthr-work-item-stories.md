# ExponentHR Work Item Story Bank

Interview-ready stories for every work item delivered at ExponentHR during the 2025.12 to 2026.04 cycles.

**Companion documents:**
- [`exponenthr-2026-accomplishments.md`](./exponenthr-2026-accomplishments.md) - the factual delivery record
- [`career-positioning-2026.md`](./career-positioning-2026.md) - how to sell this in the 2026 market

---

## Before you use this

> **Read this first.** The Azure DevOps connector is not available in this workspace, so these stories are reconstructed from work item titles, client numbers, and the platform metrics already established for the ExponentHR data platform. The **problem statements are accurate** - they come straight from the ticket titles. The **root causes are the defect class each title points to**, which is an informed reading, not a transcript of what you found.
>
> Before you tell any of these in an interview, open the actual work item and confirm three things: the real root cause, the fix you actually shipped, and one number you can defend. An interviewer who probes a story you half-remember will find the seam. An interviewer who probes a story you lived will find more depth, which is exactly what you want.
>
> Each Tier 1 story ends with a **Fill in** line naming the specifics worth recovering from Azure DevOps.

### How the tiers work

- **Tier 1 (9 stories)** - full STAR treatment, follow-up questions, and what each one proves. These carry your interviews.
- **Tier 2 (11 stories)** - one compact paragraph each. Use as supporting evidence or when an interviewer asks for a second example.
- **Section 12** maps common interview questions to the story that answers them.

---

# Tier 1: Headline stories

---

## Story 1: Four clients, one root cause

**Work items:** 28369, 34882, 32979 (00169), 33847 (10106), 33866 (10106), 34021 (00612), 32896 (00745)

### Situation
`Fact_PTOSummary` generated a steady stream of client escalations. Four tenants filed four differently-worded tickets over several months. Client 00169 said the accrual rate was wrong. Client 10106 said rates were displaying as `1E-05`, and separately that rates were showing against plans employees were not eligible for. Client 00612 said employees were missing from the summary entirely. Client 00745 said the data was stale.

### Task
The assigned work was four separate bug tickets. Closing them individually was the expected path and would have been defensible.

### Action
I refused to treat them as four bugs. Lined up side by side, the failure modes pointed at one thing: **accrual rate was being derived inline during the load rather than sourced from a modeled, plan-aware definition.** Logic derived in flight drifts across tenants, loses numeric precision, and has no natural place to enforce eligibility rules. That single design choice explains all four symptoms.

So I fixed the model instead of the rows:

1. Added a dedicated table for PTO accrual information (28369), making accrual rate and plan configuration a stored, versioned data asset rather than a recomputation on every refresh.
2. Raised a formal change request for the accrual rate calculation (34882) so the corrected logic shipped once, under review, to every tenant - rather than four divergent patches.
3. Enforced plan eligibility in the model (33866), so a rate can only attach to a plan the employee actually participates in.
4. Corrected numeric type handling (33847) so rates carry the precision and scale the business expects instead of leaking float artifacts into user-facing reports.
5. Fixed the population path dropping employees (34021) and the refresh path causing staleness (32896).

### Result
All four client tickets closed, and the defect class closed with them. PTO accrual moved from a recurring escalation source to a modeled subject area with enforced eligibility.

### Why this story lands
PTO balance is not a dashboard number. Employees plan against it, managers approve against it, and at termination **it converts to money**. Say that sentence in the interview. It reframes the work from "fixed a reporting bug" to "protected a payout obligation."

### What it proves
Systems thinking over ticket-closing. The instinct to ask "why is this the fifth ticket in this area" is the difference between a mid-level and a senior engineer, and this is the cleanest demonstration of it you have.

### Follow-ups to expect
- *"How did you convince your team to do the bigger fix?"* - The change request (34882) is your answer. You did not go rogue; you routed the structural change through the process that exists for structural changes.
- *"How did you know it was one root cause and not four?"* - The `1E-05` and the ineligible-plan rates are the tell. A float precision artifact and a missing eligibility filter both mean the rate is being computed somewhere it should be looked up.
- *"What would you do differently?"* - Honest answer: catch it earlier. Four tickets is three too many. A grain and eligibility test on the summary table would have surfaced this on the first client.

**Fill in:** how many employees or plans were affected, how long the cluster ran before you connected the tickets, whether escalation volume for this table dropped afterward.

---

## Story 2: Making the warehouse agree with the product by construction

**Work items:** 36904, 34376 (00194), 36207, 36072

### Situation
`Dim_PerformanceReviewDetails` was failing in both directions at once. Client 00194 was getting extra rows. Other clients were missing data entirely.

### Task
Fix the row counts. The obvious move was to tune the join predicates and add a DISTINCT until 00194's numbers looked right.

### Action
Over-population and under-population in the same object is a specific signal: it means **the warehouse's row-selection logic and the application's row-selection logic had diverged.** The web application knew which review record counted. The ETL was approximating.

Tuning predicates would have made one client's numbers look right by coincidence and left everyone else wrong. So I implemented the web application's actual selection logic in the load (36904). That makes the warehouse agree with the product **by construction**, for every tenant, instead of by luck for the tenant who complained loudest.

The extra rows for 00194 (34376) then resolved as a consequence rather than as a separate fix.

That left the clients who had already been under-reported. Fixing forward would have left their history permanently wrong, so I shipped a maintenance package to backfill the missing data (36072, 36207).

### Result
Review data that matches what users see in the application, plus a repair path for history that was already incorrect.

### What it proves
Source-of-truth discipline, and the willingness to cross a team boundary to get the real logic instead of reverse-engineering it from output. Also: caring about the data that was already wrong, not just the data going forward. Interviewers notice that.

### Follow-ups to expect
- *"How did you get the application logic?"* - Be ready to describe the collaboration with the app team. If you read the application code directly, say so; that is a strength.
- *"Isn't duplicating application logic in the ETL a coupling problem?"* - Yes, and it is the right trade here. The alternative was permanent drift. The better long-term answer is a shared definition or the application exposing the selection as a contract, and saying that shows architectural maturity.

**Fill in:** how many rows the backfill corrected, how many tenants were affected, whether the app team owns the logic now.

---

## Story 3: Thirty minutes to eight, and then defending it

**Work items:** CDC ETL reengineering, plus the 00630 CDC incremental failure

### Situation
The reporting warehouse refreshed via full-table reloads. Runtime was roughly 30 minutes, and the compute cost scaled with total table size rather than with what had actually changed.

### Task
Reduce ETL runtime and cost without risking correctness on a payroll-critical platform.

### Action
Reengineered the CDC pipeline from full reloads to **incremental merge-upserts**, so each run processes only changed rows. The engineering that matters here is not the merge itself - it is making the incremental path safe to rerun. Incremental loads fail in ways full reloads do not: broken watermarks, bad LSN state, partial application. I built the path to be idempotent so a failed run could be rerun cleanly rather than requiring a DBA to reason about half-applied state.

Later, client 00630 hit a CDC incremental failure. This is the highest-stakes failure mode on the platform: when incremental breaks, your options are a slow full reload or stale client data, and neither is acceptable on payroll. I diagnosed and restored the incremental path so the client returned to normal cadence **without falling back to full reload.**

### Result
Runtime dropped from 30 minutes to under 8 minutes. Compute cost fell 67%. When it broke in production, it was restored on the fast path rather than degraded to the slow one.

### Why this story lands
Cost reduction is the single most fundable thing on a 2026 data team. But the second half is what separates this from a resume bullet: **you built the optimization and then defended it under production failure.** Plenty of engineers can show a speedup. Fewer can show they kept it working.

### What it proves
Performance and cost engineering, plus production incident response. Lead with the number, close with the incident.

### Follow-ups to expect
- *"How did you validate the incremental load matched the full reload?"* - Have a reconciliation answer ready. Row counts and checksums against a full reload run is the standard approach.
- *"What broke for 00630?"* - Recover this from Azure DevOps. CDC incremental failures usually trace to capture instance state, LSN or watermark drift, or schema change on the source. Know which one it was.
- *"How do you handle schema evolution on a CDC source?"* - Expect this. It is the standard senior follow-up on any CDC story.

**Fill in:** the actual 00630 root cause, your reconciliation method, and how long the client was affected.

---

## Story 4: An hour of DBA work, twenty times a day

**Work items:** 31554, SQL Copy Down tool enhancement, Copy Down automation YAML update

### Situation
Support, testing, and bug reproduction all needed refreshed copies of client databases - 20+ requests per day. On contained Always-On Availability Groups this is materially harder than a restore: the database must be removed from the availability group, restored, have security and CDC state reconciled, and be validated back into a healthy listener configuration. Every step was manual, on a payroll-critical cluster, where a missed step leaves a database half-joined.

### Task
Make the operation repeatable and safe.

### Action
Built and hardened the SQL Copy Down tool as a one-click, **idempotent** Azure DevOps pipeline covering the full sequence: restore, security sync, CDC state reconciliation, and contained AAG listener validation.

Three design decisions worth naming in an interview:

1. **A LIVE-server guard before any restore logic runs.** A hard stop, because the failure mode this prevents is copying down over production.
2. **Idempotency.** A failed run can be safely rerun. Without that, a partial failure means a DBA reasoning about unknown state at an unknown hour.
3. **Logging and notification detailed enough to diagnose partial failures** without an ad-hoc DBA handoff.

I then validated the contained AAG drop and copy-down path on **Env006 against SQL Server 2025** (31554), catching version incompatibility on a test environment rather than discovering it mid-request. Finally I moved the tool's own deployment onto Azure Pipelines via YAML, so the automation ships through the same governed path as everything else.

### Result
Roughly **1 hour of manual orchestration removed per request, against 20+ requests per day.** The operation became rerunnable instead of requiring DBA intervention on partial failure.

### What it proves
This is your strongest platform story. It is not "I wrote a script" - it is guard rails, idempotency, version validation ahead of need, and treating the automation itself as a deployable product. That is platform engineering, and it maps directly onto how modern teams think about environment provisioning and dev-prod parity.

### Follow-ups to expect
- *"How did you make it idempotent?"* - The core question. Be specific about state checks before each step.
- *"What happens if it fails halfway?"* - Your logging and rerun design is the answer.
- *"Why a hard stop rather than a warning?"* - Because the cost of the mistake is asymmetric. Warnings get clicked through.

**Fill in:** total hours saved per month, whether support self-serves now, how many environments it covers.

---

## Story 5: Three months to fourteen days

**Work items:** Sprint 2025.12.19, DE Sprint 2026.03.05, DE Sprint 2026.04.02, plus CI/CD ownership

### Situation
The deployment cycle ran roughly 3 months. The bottleneck was not build time - it was cross-team idle time, handoffs waiting on other handoffs.

### Task
Own code management and release execution for the data engineering team.

### Action
Took end-to-end ownership of CI/CD through Azure DevOps and drove release execution across three cycles, including code management and release to testing for 2025.12.19 and delivery for DE Sprints 2026.03.05 and 2026.04.02.

### Result
Cycle time went from **3 months to 14 days**, removing roughly 11 weeks of idle time per release.

### Why this story matters more than it looks
This is the story that makes every other story credible. A 14-day cycle is why the accrual change request (Story 1) was worth attempting at all - under a 3-month cycle, a structural fix is a two-quarter bet and nobody approves it. Fast release cadence is what makes root-cause fixes rational instead of reckless.

**Say that connection out loud in an interview.** Most candidates present velocity metrics and correctness work as unrelated bullet points. Presenting them as cause and effect demonstrates you understand why delivery speed matters, which is a different and more senior claim than "I made it faster."

### What it proves
Ownership beyond your assigned lane, and an understanding that process constraints determine which engineering decisions are even available to you.

### Follow-ups to expect
- *"What was actually taking 3 months?"* - Be specific about which handoffs you removed.
- *"What did you keep?"* - Have an answer about a gate you deliberately did not remove. On payroll, some friction is correct, and knowing which is the senior signal.
- *"How did you get buy-in?"* - This was a cross-team change; describe the organizational side.

**Fill in:** which specific gates you removed, which you kept and why, whether defect escape rate changed.

---

## Story 6: A status code in a numeric column, in tax data

**Work items:** 14825, 34366

### Situation
Two W-4 defects, one shape. `[W4 State Allowances]` was carrying the state filing status **and** the allowances value packed into one field. Separately, `Dim_W4ElectionData` was carrying election status inside the allowances value.

### Task
Separate the concerns.

### Action
Both are the same violation: **one attribute per column.** Any consumer treating allowances as a numeric quantity - withholding calculation, compliance reporting, any aggregate - was reading a contaminated value. I split them so filing status and election status live in their own attributes and the allowances field holds allowances only.

### Result
Clean, correctly typed W-4 election data.

### Why this story lands
This looks like the smallest item in the list. Use it anyway, because of the domain: **this is tax withholding input data.** The correctness bar is regulatory, not analytical. A wrong allowances value is not a bad chart - it is an under-withheld employee and a compliance exposure.

It is also a genuinely good answer to "tell me about a time you caught something others missed," because a packed field does not throw an error. It silently returns a plausible number. Nothing fails; the value is just wrong.

### What it proves
Data contract thinking, and the judgment to treat a small ticket as important because of what it touches rather than how big it is.

### Follow-ups to expect
- *"How did you find it?"* - Recover this. Whether it came from a client report or your own review changes the story significantly, and the second version is much stronger.
- *"How would you prevent this class of defect?"* - Type constraints and column-level contracts at ingestion. This is your natural bridge to talking about data quality tooling.

**Fill in:** how it was discovered, and whether any downstream withholding calculations were affected.

---

## Story 7: Fix all three repos, not the one that shouted

**Work item:** 36429

### Situation
Reporting databases could not be created from the `release/2025.07.25` branch. This is a pipeline-blocking failure: if you cannot build a reporting database from the release branch, you cannot validate the release. Everything downstream stops.

### Task
Unblock the release.

### Action
The root cause was not in the data or the schema - it was in the pipeline definitions. An agent name in the YAML no longer resolved.

The minimum fix was one line in the repo that surfaced the error. Instead I checked all the pipeline definitions and updated the agent name across **all three affected repositories: Full Load, Incremental, and Employer Reports.** The other two had the same stale reference and had simply not been built yet. Fixing only the loud one would have meant the identical failure ambushing the next person who touched either of the others.

### Result
Release validation unblocked, and the same failure prevented in two repositories that had not surfaced it yet.

### What it proves
Preventive thinking, and treating pipeline configuration as real code with real blast radius. It is a small story that tells an interviewer exactly how you work: when you find a bug, you ask where else it lives.

### Follow-ups to expect
- *"How did you know the other two had it?"* - You checked. Say so plainly.
- *"How would you prevent config drift across repos?"* - Shared or templated pipeline definitions. Good opening to discuss pipeline-as-code patterns.

**Fill in:** how long the release was blocked, and whether you templated the shared config afterward.

---

## Story 8: Point-in-time correctness

**Work item:** 34247 (00747)

### Situation
Client 00747 had incorrect effective end dates in `Dim_EmpInfoHistory`.

### Task
Fix the end-dating.

### Action
This is the correctness backbone of a Type 2 slowly changing dimension. If end dates are wrong, validity intervals either **overlap** or leave **gaps**. Ask "what was this employee's status on the pay date" and you get two answers or none. Every point-in-time query against employee history becomes unreliable, and on an HR platform that means every historical payroll and benefits question.

I corrected the end-dating so intervals close properly and a point-in-time lookup returns exactly one valid row.

### Result
Reliable historical employee lookups for 00747.

### Why this story punches above its size
SCD Type 2 correctness is a **classic senior data engineering interview topic**. Interviewers ask about it specifically because it separates people who have modeled dimensions in production from people who have read about them. You have a real production instance of it. That is worth more than a textbook answer.

This is also your natural bridge to modern tooling: dbt snapshots solve exactly this problem, and being able to say "I have debugged this by hand, so I know what snapshots are protecting me from" is a strong answer.

### Follow-ups to expect
- *"Overlapping or gapping?"* - Know which. They have different causes.
- *"How do you test for it?"* - Assert no overlapping intervals per entity, and that exactly one row is current. Have this ready; it is the real question underneath.
- *"How would you do this in dbt?"* - Snapshots. Make the connection yourself before they ask.

**Fill in:** whether intervals overlapped or gapped, the root cause, and how you validated the fix.

---

## Story 9: Building a subject area from nothing

**Work item:** Attestations dimensional model (no ticket number)

### Situation
Attestations existed in the application but had no warehouse representation. Compliance data that could not be reported on, trended, or audited alongside the rest of the HR data.

### Task
Design and build the dimensional model.

### Action
Greenfield modeling rather than defect repair: established the fact grain, built conformed dimensions so attestations join cleanly to the existing employee and organizational dimensions, and integrated it into the warehouse's load and release process.

### Result
Attestations became a reportable, auditable subject area.

### Why you need this story in the rotation
Everything else in your year is repair work. Excellent repair work, but repair work. **An interviewer scanning your list will wonder whether you can build, or only fix.** This is the answer, and you should volunteer it rather than wait to be asked.

Pair it with the Cosmos Expense SSRS work (Tier 2) as a second build example.

### What it proves
Kimball dimensional modeling from a blank page: grain definition, conformed dimensions, integration with an existing warehouse. That is a design skill, and it is distinct from everything else in the record.

### Follow-ups to expect
- *"What grain did you choose and why?"* - The central question in dimensional design. Have a crisp answer.
- *"How did you conform it to existing dimensions?"* - Be specific about which dimensions it reuses.
- *"What did you get wrong?"* - Have something. A model you would grain differently in hindsight is a strong, credible answer.

**Fill in:** the actual grain, which conformed dimensions it reuses, who consumes it now.

---

# Tier 2: Supporting stories

One paragraph each. Use these when an interviewer wants a second example, or to show breadth across the platform.

### 32478 - Merge conflict on Dim_StatsReportType (Client 00994)
Client 00994's load was **hard-failing** on a MERGE - the case where a target row matches more than one source row, so the statement cannot decide which update wins and aborts. Not a soft data-quality issue: the load stops and the client's data goes stale until someone fixes it. I resolved the ambiguity in the source-to-target key relationship so each target row matches at most one source row. *Use this when asked about grain, MERGE semantics, or debugging a failing load.*

### 32495 - Voucher duplicated in Fact_PayVoucherDetail (Client 00810)
An employee's voucher appeared twice in the pay voucher fact. Duplication in a pay fact is directly money-adjacent - it inflates what reconciliation reports show as paid. Root cause was a grain mismatch between the declared fact grain and the source's real grain, causing fan-out on a join. Fixed by restoring grain integrity rather than adding a deduplication step downstream. *Pairs naturally with 37005 below - same domain, opposite symptom.*

### 37005 - Dim_PayDemographics missing vouchers (Client 00982)
The mirror image of 32495: vouchers absent from the pay demographics dimension. Duplication and omission in the same domain are usually the same root cause seen from two sides - when declared grain and real grain disagree, one join path fans out while another filters out. Closed the gap so voucher coverage was complete. *Tell this immediately after 32495; the pairing is the insight.*

### 13803 - Incorrect ER contribution code used
An employer contribution was being applied under the wrong code. Contribution codes drive employer-side cost reporting and downstream filings, so a mis-mapped code is not a labeling problem - it lands in numbers the employer reports externally. Corrected the mapping. *Use for "tell me about a bug with real-world consequences."*

### 36204 - Add MatchSH2Adj column to ssrs_UpdateRecurring
Added the `MatchSH2Adj` column to the `ssrs_UpdateRecurring` stored procedure so the match adjustment value flows through the recurring update path into SSRS reporting instead of being invisible to the reports that needed it. *Small, but shows you work across the full stack from procedure to report.*

### 35366 - Fact_TimeAllocation duplicate rows (Client 00877)
Duplicate rows in the time allocation fact. Time allocation feeds labor distribution and cost attribution, so duplicates **inflate charged hours against projects and cost centers** - a billing and cost-accounting problem, not just a reporting one. Two-part fix: corrected the load so duplicates stopped being produced, then built a maintenance job to clean the stale and duplicate records already sitting in the table, shipped as a **limited maintenance package scoped to 00877**. The scoping is the interesting part - a tenant-scoped package shipped on its own timeline without waiting for a full release and without touching tenants that did not need it. *Use for "tell me about a time you fixed both the cause and the damage," or for blast-radius reasoning.*

### 36119 - Deadlock on client databases for stored procedures
Stored procedures on client databases were deadlocking. This is the worst class of production defect to chase: load-dependent and intermittent, passes every test, then fails under real concurrency, and the victim transaction dies with work half-done. Addressed the contention so concurrent execution completes reliably. *Strong answer for "hardest bug you have debugged" - lead with why deadlocks resist normal debugging.*

### 33436 - Reissued vouchers missing (Client 00810) - handed off
Triaged and handed to a colleague. Voucher reissue is a distinct upstream event lifecycle from original issuance, and it belonged with the owner of that path rather than being worked around in the reporting layer. *Do not hide this one. "I diagnosed it, determined it belonged upstream, and handed it to the right owner with context" is a better answer than pretending you closed everything. Interviewers trust candidates who distinguish what they own from what they routed.*

### Cosmos Expense Project - SSRS support
Provided reporting-layer support for the Cosmos Expense project so expense data reaches SSRS through the same governed warehouse path as everything else, rather than through a one-off extract. *Use as a second build example alongside Attestations, and as evidence you resist one-off pipelines.*

### 27353 - Fact_PTODetails approval flag and 12/31/1900 dates
Every record in the PTO details fact was being stamped with an approval date of **12/31/1900** - the SQL Server zero-date sentinel - and carrying an incorrect approved flag. This is a technical default escaping into business data: nothing errors, but the approval audit trail is fiction. Corrected the approval semantics so the flag reflects the real approval event and unapproved records carry NULL rather than a fabricated date. *Excellent answer for "a bug that did not throw an error." Also a clean way to talk about representing absence correctly instead of substituting a placeholder that reads as data.*

### 32896 / 32979 - Fact_PTOSummary staleness and wrong rates
Covered in depth as part of Story 1. Mentioned separately here because they are individually ticketed and may come up by number.

---

# Section 12: Question-to-story map

| If they ask... | Tell... |
|---|---|
| "Walk me through a technical problem you are proud of" | Story 1 (accrual cluster) |
| "Tell me about improving performance or reducing cost" | Story 3 (CDC, 30 min to 8 min, -67%) |
| "Describe something you automated" | Story 4 (Copy Down tool) |
| "Tell me about a production incident" | Story 3 second half (00630), or 36119 (deadlocks) |
| "Hardest bug you have debugged" | 36119 (deadlocks) - lead with why they resist debugging |
| "A bug that did not throw an error" | 27353 (12/31/1900) or Story 6 (W-4) |
| "Tell me about data modeling experience" | Story 9 (Attestations) then Story 8 (SCD Type 2) |
| "Explain slowly changing dimensions" | Story 8 - you have a production instance, not a definition |
| "Tell me about working with another team" | Story 2 (application logic alignment) |
| "A time you went beyond your assigned task" | Story 7 (three repos) or Story 5 (CI/CD ownership) |
| "How do you handle competing priorities?" | Story 1 - four clients, one structural fix |
| "Tell me about a mistake or something you would redo" | Story 1 follow-up: four tickets was three too many |
| "Something you did not finish / had to hand off" | 33436 - answer it straight |
| "How do you ensure data quality?" | Story 6 plus the four defect classes in the accomplishments doc |
| "Experience with CI/CD" | Story 5, then Story 4 and Story 7 |
| "Tell me about ambiguity" | Story 2 - divergent logic with no documented source of truth |
| "Why should we hire you?" | Story 5 connected to Story 1: fast delivery is what makes structural fixes possible |

---

## Three habits these stories demonstrate

Whatever the question, these are the through-lines worth surfacing. They are more memorable than any individual ticket.

1. **When a bug appears repeatedly, fix the model, not the row.** Story 1 is the proof: four tickets, one design flaw, one structural fix.
2. **When you find a bug, ask where else it lives.** Story 7: three repos, not one. Story 2: every tenant, not just the one that complained.
3. **Fix the damage, not just the cause.** 35366 and Story 2 both shipped backfills. Stopping the bleeding is half the job; the data that is already wrong stays wrong until someone repairs it.
