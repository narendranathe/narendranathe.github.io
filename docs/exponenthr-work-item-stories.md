# ExponentHR Work Item Story Bank

Interview-ready stories covering 2025 and 2026 year to date at ExponentHR.

**Companion documents:**
- [`exponenthr-accomplishments.md`](./exponenthr-accomplishments.md) - the delivery record
- [`career-positioning-2026.md`](./career-positioning-2026.md) - how to sell this in the 2026 market

---

## Before you use this

> **Read this first.** No Azure DevOps connector is available in this workspace, so these stories are reconstructed from work item titles, client numbers, and the platform metrics already established. The **problem statements are accurate** - they come from the ticket titles. The **root causes are the defect class each title points to**, which is an informed reading, not a transcript.
>
> Before telling any of these in an interview, open the work item and confirm three things: the real root cause, what you actually shipped, and one number you can defend. Each Tier 1 story ends with a **Fill in** line naming what to recover.

### How the tiers work

- **Tier 1 (13 stories)** - full STAR, follow-up questions, what each proves. These carry your interviews.
- **Tier 2** - one paragraph each, for second examples and breadth.
- **Section 15** maps interview questions to stories.

Stories are tagged `[2025]`, `[2026]`, or `[both years]`.

---

## The story above the stories

Before any individual ticket, know the shape of the two years. This framing is worth more than any single story, and most candidates cannot offer anything like it.

> "My first year was correctness. I worked about 29 items across the whole warehouse - vouchers, deduction basis logic, W-4, time punches, benefits, employee action notices - plus production hotfixes and release support across eight cycles. By the end of it I knew every way that warehouse could go wrong.
>
> That is what earned the second year. In 2026 I stopped fixing rows and started owning the machinery: CI/CD end to end, CDC rebuilt from full reloads to incremental, the availability group copy-down automated, new dimensional models from scratch.
>
> The turning point was in the middle. In 2025 I built a validation framework called Data Checker, because I got tired of learning about defects from clients. And I worked out and documented how to deploy CDC schema changes safely. Those two are why the 2026 platform work was possible at all."

**Why this works:** it answers "are you senior?" without you having to claim it. You describe a progression from reactive to architectural, with a named turning point. Interviewers hear trajectory.

---

# Tier 1: Headline stories

---

## Story 1: Building the thing that finds the bugs `[2025]`

**Workstream:** Data Checker implementation with control table; deployment on training03

### Situation
Every data defect I worked in 2025 - and there were 29 of them - arrived the same way: a client noticed. Wrong voucher descriptions, duplicated allocations, missing login activity, incorrect accrual for terminated employees. The warehouse had no systematic validation. The detection mechanism was a customer complaint.

### Task
Nobody assigned this. The assigned work was the tickets.

### Action
Built **Data Checker**, a validation framework driven by a **control table**. The design decision that matters: validation rules are **configuration, not code**. A new check is a row in the control table, not a script someone writes and forgets. That makes coverage additive and cheap - the reason ad hoc validation scripts always decay is that adding one is a development task.

Deployment crossed a team boundary. Getting it running on `training03` meant working through security and connection string issues with IT.

### Result
The warehouse moved from client-reported defect discovery toward systematic validation.

### Why this is your most important 2025 story
Every other item in that year is "I fixed a bug." This one is **"I noticed we were finding bugs the wrong way and built the mechanism to fix that."** It is the single clearest piece of evidence that you operate above ticket level.

It is also the most **marketable** thing in your record. Data quality and observability is one of the hottest areas in data engineering right now, and a control-table-driven validation framework is architecturally the same idea as dbt tests and Great Expectations: declarative, metadata-driven assertions that run as part of the pipeline. **You built one before you had the vocabulary for it.**

Say that explicitly: *"I built the concept before I knew the tools existed. When I picked up dbt tests, it was the same idea with better ergonomics."*

### Follow-ups to expect
- *"What checks did it run?"* - Recover specifics. Row counts, null rates, referential integrity, grain uniqueness are the likely families.
- *"How did you decide what to check?"* - Your defect history is the answer. You had 29 examples of what goes wrong.
- *"What would you do differently?"* - Run it in CI rather than as a separate process, and fail the load on critical check failure. That is the honest gap and it shows you know where the idea goes next.

**Fill in:** how many tables and checks it covered, whether it caught defects before clients did, whether the team still uses it.

---

## Story 2: Four clients, one root cause `[2026]`

**Work items:** 28369, 34882, 32979 (00169), 33847 (10106), 33866 (10106), 34021 (00612), 32896 (00745)

### Situation
`Fact_PTOSummary` generated a steady stream of escalations. Four tenants, four differently-worded tickets. 00169: wrong accrual rate. 10106: rates displaying as `1E-05`, and rates showing against plans employees were not eligible for. 00612: employees missing entirely. 00745: stale data.

Related history: back in 2025, `16805` had accrued hours displaying incorrectly for a terminated employee with a cleared balance. **This surface had been producing defects for over a year.**

### Task
Four bug tickets. Closing them individually was the expected path.

### Action
Lined up together, the failure modes pointed at one design choice: **accrual rate was derived inline during the load rather than sourced from a modeled, plan-aware definition.** In-flight logic drifts across tenants, loses precision, and has nowhere to enforce eligibility. That one choice explains all four symptoms.

1. Added a dedicated PTO accrual table (28369) - accrual rate and plan configuration became a stored, versioned asset.
2. Raised a formal change request for the rate calculation (34882) so corrected logic shipped once, reviewed, to every tenant.
3. Enforced plan eligibility (33866), corrected numeric precision (33847), restored employee coverage (34021), fixed the refresh path (32896).
4. Corrected approval semantics in `Fact_PTODetails` (27353) so unapproved records carry NULL rather than a fabricated `12/31/1900`.

### Result
Four tickets closed, and the defect class closed with them.

### Why it lands
PTO balance is not a dashboard number. Employees plan against it, managers approve against it, and **at termination it converts to money.** Say that sentence.

### What it proves
Systems thinking over ticket-closing, and the judgment to route a structural change through the change request process rather than going around it.

### Follow-ups to expect
- *"How did you know it was one cause and not four?"* - The `1E-05` and the ineligible-plan rates are the tell. A float artifact and a missing eligibility filter both mean the rate is being computed where it should be looked up.
- *"How did you get buy-in?"* - The change request. You did not go rogue.
- *"What would you do differently?"* - Catch it earlier. Counting 2025, this surface produced defects for over a year. A grain and eligibility check in Data Checker would have surfaced it sooner - **and you can say that, because you built Data Checker.**

**Fill in:** employees or plans affected, whether escalation volume dropped.

---

## Story 3: Thirty minutes to eight, and defending it `[both years]`

**Work:** CDC schema change deployment process (2025); CDC incremental reengineering (2026); 00630 CDC incremental failure (2026)

### Situation
The warehouse refreshed via full-table reloads - roughly 30 minutes, with compute cost scaling to total table size rather than to what changed.

### Task
Cut runtime and cost without risking correctness on a payroll-critical platform.

### Action
This is a two-year story, and the sequencing is the point.

**2025 - groundwork.** Before touching the pipeline I researched, tested, and documented the **CDC schema change deployment process**. You cannot safely rebuild a CDC pipeline until you know what happens when a source table changes underneath it.

**2026 - the rebuild.** Reengineered from full reloads to **incremental merge-upserts**, processing only changed rows. The engineering that matters is not the merge - it is making the incremental path safe to rerun. Incremental loads fail in ways full reloads do not: broken watermarks, bad LSN state, partial application. Built it idempotent so a failed run reruns cleanly instead of requiring a DBA to reason about half-applied state.

**2026 - defending it.** Client 00630 hit a CDC incremental failure. Highest-stakes failure mode on the platform: when incremental breaks, the options are a slow full reload or stale client data, and neither is acceptable on payroll. Diagnosed and restored the incremental path **without falling back to full reload.**

### Result
30 minutes to under 8. Compute cost down 67%. When it broke in production, restored on the fast path.

### Why it lands
Cost reduction is the most fundable thing on a 2026 data team. But the arc is what separates this from a resume bullet: **you did the safety research first, built the optimization second, and defended it under production failure third.** Most candidates can show a speedup. Almost none can show that sequence.

**Fill in:** the actual 00630 root cause, your reconciliation method against full reload, client impact duration.

---

## Story 4: Schema evolution on a CDC source `[2025]`

**Workstream:** CDC schema change deployment process - research, testing, documentation

### Situation
CDC capture instances are bound to a table definition. When a source table changes, things break in quiet ways: capture can fail, the new column can be silently dropped from the capture instance, or the instance needs rebuilding with a gap to reconcile. The team had no established process.

### Task
Not assigned as a ticket. I took it on because I could see it coming.

### Action
Researched the failure modes, tested the approaches against real schema changes, and **wrote the process down for the team.** Related items in the same period were the concrete instances: `32319` (schema changes on `Dim_TimePunchType`) and `32344` (Cosmos Expense table additions, schema changes, and constraints).

### Result
A documented, tested process the team follows, and the foundation the 2026 CDC incremental reengineering was built on.

### Why you must have this story ready
**"How do you handle schema evolution on a CDC source?" is the standard senior follow-up to any CDC story.** Most candidates answer hypothetically. You researched it, tested it, documented it, and then built on it.

The documentation matters as much as the research. Writing it down for the team is a seniority signal that interviewers specifically look for and rarely find.

### Follow-ups to expect
- *"Walk me through what happens when a column is added."* - Know your actual process end to end.
- *"How do you handle a column type change?"* - Harder case. Have a position.
- *"How do you backfill the gap after rebuilding a capture instance?"* - The question underneath the question.

**Fill in:** the actual process steps, where the documentation lives, whether the team adopted it.

---

## Story 5: The silent money bug `[2025]`

**Work items:** 14020, 14030, 16069, 31483, 13803

### Situation
Four tickets across three recurring item types, all saying nearly the same thing:

- `[Deduction Rec Item Based On] may not have all basis`
- `[ER Rec Item Based On] may not have all basis`
- `DW incorrect result for [Earning Rec Item Based On]`
- `[ER Contrib Total Comp Category] not getting Base Salary`

### Task
Four separate tickets on paper.

### Action
One shared root cause: **the basis resolution was incomplete.** The set of values a recurring item could be calculated against did not cover every valid case. `14020` is the same defect stated differently - the employer contribution category was missing base salary, its most significant component.

I also carried `13803` (incorrect employer contribution code) to code complete in 2025; it released in the 2026 cycle.

### Result
Basis coverage completed across deduction, earning, and employer contribution item types.

### Why this is your best "consequences" story
**Nothing errors.** A partial basis produces a plausible number that is simply too small, applied to real employee deductions and real employer contributions. No exception, no alert, no anomalous-looking report. Just money that is quietly wrong for anyone whose basis included the missing component.

That is a better answer to "tell me about a bug with real consequences" than any crash story, because the danger is precisely that it does not crash.

### What it proves
Domain depth in payroll calculation, and pattern recognition - you saw "may not have all basis" appear across three item types and treated it as one problem.

### Follow-ups to expect
- *"How did you find the missing basis values?"* - Recover this. Comparing against the source's valid set is the likely method.
- *"How would you prevent it?"* - **A Data Checker rule asserting basis completeness.** Connect your own two stories; interviewers notice when your work coheres.

**Fill in:** which basis values were missing, financial impact if quantified, whether all three item types shipped together.

---

## Story 6: When incremental and full load disagree `[2025]`

**Work items:** 16462, 27638 (00704)

### Situation
Contractors were appearing in W-4 election data where they did not belong - and critically, the ticket noted it was **the incrementals** adding them. Separately, client 00704's full load needed a join change in `Fact_EmpW4Elections` (27638).

### Task
Stop contractors entering `Dim_W4ElectionData` and `Fact_W4ElectionData`.

### Action
The detail that matters is *incremental only*. When a defect appears on the incremental path but not the full load, the two paths **disagree about what qualifies for inclusion** - the incremental filter was not enforcing the same population rule as the full load.

This class of bug is dangerous for a specific reason: **a full reload appears to fix it.** The bad rows vanish, everyone moves on, and the cause is still there waiting for the next incremental run. The fix has to be reconciling the population logic across both paths, not reloading.

### Result
Population rules aligned across full and incremental paths.

### Why this story is stronger than it looks
It shows you read the *shape* of a bug report, not just its content. "Incrementals appear to be adding contractors" contains its own diagnosis if you know what to listen for, and most engineers would have reloaded and closed it.

It also sets up a great line about your CDC work: *"That is why, when I rebuilt the CDC pipeline the next year, reconciling incremental against full reload was the first thing I validated."*

### Follow-ups to expect
- *"How do you test that the two paths agree?"* - Run both, compare row counts and checksums. Have this ready; it is the real question.
- *"Would a full reload have fixed it?"* - Temporarily, and that is the trap. Say so.

**Fill in:** the actual population rule that diverged, how you validated the fix.

---

## Story 7: Two hotfixes under payroll pressure `[2025]`

**Work items:** 29885, 30559

### Situation
Two defects that could not wait for a release.

**29885:** `Fact_PayVoucherDetail` was **replicating the 09/05/25 payroll run.** Duplicated payroll data, on a dated payroll cycle.

**30559:** the `Field` column length differed between the base table and `Dim_EAN`. Length mismatches **truncate silently on load** - no error, values just arrive shortened.

### Task
Ship both outside the normal release cycle.

### Action
Diagnosed and shipped as hotfixes. `29885` meant identifying why the voucher detail load was reproducing an entire payroll run's rows - a grain or rerun-idempotency failure on the most sensitive table in the warehouse. `30559` meant reconciling the schema mismatch and dealing with values already truncated.

### Result
Both resolved out of cycle.

### Why to use this
Two things interviewers want evidence of: **you can work under production pressure**, and **you have shipped outside the safety of a normal release**. Hotfix experience is a proxy for trust - organizations do not let junior engineers hotfix payroll tables.

The `30559` detail is also a good "silent failure" example: a length mismatch does not throw. It truncates.

### Follow-ups to expect
- *"What was your rollback plan?"* - Have an answer. Hotfix questions are really risk-management questions.
- *"How did you verify the fix before shipping?"* - The core of hotfix discipline.
- *"How did you prevent recurrence?"* - Ideal place to mention Data Checker.

**Fill in:** actual root causes, turnaround time, how you validated under time pressure.

---

## Story 8: An hour of DBA work, twenty times a day `[2026]`

**Work items:** 31554, Copy Down tool enhancement, Copy Down automation YAML

### Situation
Support, testing, and bug reproduction all needed refreshed client databases - 20+ requests daily. On contained Always-On Availability Groups this is much harder than a restore: remove the database from the AG, restore, reconcile security and CDC state, validate listener health. Every step manual, on a payroll-critical cluster, where a missed step leaves a database half-joined.

### Action
Built and hardened the SQL Copy Down tool as a one-click **idempotent** Azure DevOps pipeline covering the full sequence.

Three decisions worth naming:

1. **A LIVE-server guard before any restore logic runs.** A hard stop, because the failure it prevents is copying down over production.
2. **Idempotency.** A failed run reruns safely. Without it, partial failure means a DBA reasoning about unknown state at an unknown hour.
3. **Logging detailed enough to diagnose partial failures** without an ad hoc DBA handoff.

Validated the contained AAG path on **Env006 against SQL Server 2025** (31554) - catching version incompatibility on a test environment rather than mid-request. Then moved the tool's own deployment onto Azure Pipelines so the automation ships through the same governed path as everything else.

### Result
~1 hour of manual orchestration removed per request, 20+ requests per day. The operation became rerunnable rather than requiring DBA intervention on partial failure.

### What it proves
Not "I wrote a script" - guard rails, idempotency, version validation ahead of need, and treating the automation itself as a deployable product.

### Follow-ups to expect
- *"How did you make it idempotent?"* - The core question. Be specific about state checks.
- *"Why a hard stop rather than a warning?"* - The cost is asymmetric. Warnings get clicked through.

**Fill in:** hours saved per month, whether support self-serves now, environments covered.

---

## Story 9: Ten release cycles and a 3-month problem `[both years]`

**Work:** 8 release cycles in 2025, 2 DE sprints in 2026, CI/CD ownership

### Situation
The deployment cycle ran roughly 3 months. The bottleneck was not build time - it was cross-team idle time, handoffs waiting on handoffs.

### Action
**2025:** supported release execution across eight cycles - Sprint 6.27, SSRS 2025.07.28, 8.15, 8.22, 2025.09.15, 2025.11.07, 2025.12.15, 2025.12.19 - including SSRS release branch refresh and code management into testing. That is where I learned where the time actually went.

**2026:** took end-to-end ownership of CI/CD through Azure DevOps and drove delivery across DE Sprints 2026.03.05 and 2026.04.02.

### Result
Cycle time from **3 months to 14 days**, removing roughly 11 weeks of idle time per release.

### Why this story makes the others credible
A 14-day cycle is why the accrual change request (Story 2) was worth attempting. Under a 3-month cycle a structural fix is a two-quarter bet and nobody approves it. **Fast release cadence is what makes root-cause fixes rational instead of reckless.**

Say that connection out loud. Most candidates list velocity metrics and correctness work as unrelated bullets. Presenting them as cause and effect is a more senior claim than "I made it faster."

The 2025 half also matters: you did not arrive and reorganize the release process. You worked inside it for eight cycles first, then changed it.

### Follow-ups to expect
- *"What was actually taking 3 months?"* - Be specific about which handoffs you removed.
- *"What did you keep?"* - Have an answer about a gate you deliberately did not remove. On payroll, some friction is correct.

**Fill in:** which gates you removed, which you kept and why, whether defect escape rate changed.

---

## Story 10: Shipping to a legislated deadline `[2025]`

**Work:** Sprint 2025.12.15 - SECURE 2.0 and Clock Out Type enhancement

### Situation
SECURE 2.0 is US retirement legislation with provisions phasing in across multiple years. Payroll platforms have to support it. The deadline is set by law.

### Action
Delivered the data layer support through the 2025.12.15 release, alongside the Clock Out Type enhancement.

### Result
Shipped on cycle.

### Why to use this story
Almost every other item in your record is a defect fix or an internal improvement. **This is regulatory compliance delivery on a deadline you did not control and could not negotiate.**

That is a different kind of evidence. It says you can work to an external mandate with real consequences, in a domain where "we will get it in the next release" is not available.

It also demonstrates domain depth. Retirement plan legislation, contribution and match mechanics, and payroll data are specialized. Combined with the W-4 tax work and the deduction basis work, you can credibly say **payroll and benefits data is a domain you know**, not just a place you happened to work. Domain expertise commands a premium.

### Follow-ups to expect
- *"What did SECURE 2.0 require on the data side?"* - Recover the specifics before using this story.
- *"How did you validate compliance?"* - Testing and sign-off process.

**Fill in:** what the provisions required, your scope versus the team's, how it was validated.

---

## Story 11: Making the warehouse agree with the product `[2026]`

**Work items:** 36904, 34376 (00194), 36207, 36072

### Situation
`Dim_PerformanceReviewDetails` was failing in both directions at once. Client 00194 was getting extra rows. Other clients were missing data entirely.

### Action
Over-population and under-population in the same object is a specific signal: **the warehouse's row-selection logic and the application's had diverged.** The application knew which review record counted; the ETL was approximating.

Tuning predicates would have made one client right by coincidence. Instead I implemented the web application's actual selection logic in the load (36904), making the warehouse agree with the product **by construction**, for every tenant. The extra rows (34376) resolved as a consequence.

That left clients already under-reported, so I shipped a maintenance package to backfill (36072, 36207) rather than only fixing forward.

Related: `16383` in 2025 was `Dim_PerformanceGoals` not recognizing `Status 98` - the same subject area and the same class of incomplete domain handling.

### What it proves
Source-of-truth discipline, willingness to cross a team boundary for the real logic, and caring about data that was already wrong.

### Follow-ups to expect
- *"Isn't duplicating application logic in the ETL a coupling problem?"* - Yes, and it is the right trade here. The better long-term answer is a shared definition or the application exposing selection as a contract. Saying that shows architectural maturity.

**Fill in:** rows corrected by the backfill, tenants affected, who owns the logic now.

---

## Story 12: Point-in-time correctness `[2026]`

**Work item:** 34247 (00747)

### Situation
Client 00747 had incorrect effective end dates in `Dim_EmpInfoHistory`.

### Action
This is the correctness backbone of a Type 2 slowly changing dimension. Wrong end dates mean validity intervals **overlap** or leave **gaps**. Ask "what was this employee's status on the pay date" and you get two answers or none - so every historical payroll and benefits question becomes unreliable.

Corrected the end-dating so intervals close properly and a point-in-time lookup returns exactly one valid row.

### Why it punches above its size
**SCD Type 2 correctness is a classic senior interview topic.** Interviewers ask because it separates people who have modeled dimensions in production from people who have read about them. You have a real production instance.

It is also your bridge to modern tooling: dbt snapshots solve exactly this. *"I have debugged Type 2 end-dating by hand, so I know what snapshots are protecting me from."*

### Follow-ups to expect
- *"Overlapping or gapping?"* - Know which. Different causes.
- *"How do you test for it?"* - Assert no overlapping intervals per entity, exactly one current row. This is the real question.

**Fill in:** overlap or gap, root cause, validation method.

---

## Story 13: Building a subject area from nothing `[2026]`

**Work:** Attestations dimensional model

### Situation
Attestations existed in the application but had no warehouse representation - compliance data that could not be reported, trended, or audited alongside the rest of the HR data.

### Action
Greenfield modeling: established the fact grain, built conformed dimensions so attestations join cleanly to existing employee and organizational dimensions, and integrated it into the load and release process.

### Result
A reportable, auditable subject area.

### Why you need this in the rotation
Most of your record is repair work. Excellent repair work, but an interviewer scanning it will wonder **whether you can build or only fix.** This is the answer, and you should volunteer it rather than wait.

Pair with Cosmos Expense (Tier 2), where you scripted the schema foundation in 2025 (`32344`) and delivered SSRS support in 2026 - a build you carried across both years.

### Follow-ups to expect
- *"What grain did you choose and why?"* - The central question in dimensional design.
- *"What did you get wrong?"* - Have something. A model you would grain differently in hindsight is credible.

**Fill in:** the grain, which conformed dimensions it reuses, who consumes it.

---

# Tier 2: Supporting stories

### SSRS server crash root cause analysis `[2025]`
Not "restarted the server" - root cause analysis on a production SSRS crash. *Use for "tell me about a production incident" if you want a second example after the 00630 CDC failure, or when asked about ownership beyond your assigned lane.*

### 29973 - Orphaned dimension key in Fact_TimePunches `[2025]`
`Fact_TimePunches` carried a `Dim_TimeSourceID` that did not exist in `Dim_TimeSource` - a textbook referential integrity failure. The consequence is subtle: an inner join makes those punches **vanish from reports** while the rows still sit in the fact table, so the data looks present and reports silently under-count. Fixing it means repairing the data and closing the write path that allowed an unmatched key. *Strong answer for "how do you enforce referential integrity" and a natural lead-in to Data Checker.*

### 31313, 31622, 32478 - Three MERGE failures, one cause `[both years]`
`Dim_EmpW4Election` for client 630 (2025), `Dim_Author` for 00336 (2025), `Dim_StatsReportType` for 00994 (2026). All the same failure: a target row matched by more than one source row, so MERGE cannot decide which update wins and aborts. **These are hard failures** - the load stops and client data goes stale until someone fixes it. Each was resolved by fixing the source-to-target key relationship so one target row matches at most one source row. *Tell all three together. Three instances of one root cause across two years is a much better answer than one instance, and it sets up "what would you do differently" - a uniqueness check on the source would have caught every one.*

### 16383, 30856 - Status domain gaps `[2025]`
`Dim_PerformanceGoals` not recognizing `Status 98`, and EAN 269367 showing `Approved` when it should be `Completed`. Same class: the warehouse's set of valid status values was narrower than the source's, so unmapped statuses fall through to a default or fail to match. Workflow status drives what users act on, so this is operational, not cosmetic. *Good for "tell me about an assumption that turned out wrong."*

### 14825, 34366 - A status code in a numeric column `[2026]`
`[W4 State Allowances]` carried state filing status **and** the allowances value in one field; `Dim_W4ElectionData` carried election status inside the allowances value. One violation, twice: **one attribute per column.** Any consumer treating allowances as numeric - withholding calculation, compliance reporting, any aggregate - read a contaminated value. Separated so each attribute stands alone. *Small tickets, big domain: this is tax withholding input, so the bar is regulatory. Also a clean answer to "a bug that did not throw an error" - a packed field silently returns a plausible number.*

### 16552, 16518 - Attribute resolution, and fixing at the source `[2025]`
Voucher code short description and PIECEWORK allocation description both resolving incorrectly. `16518` is the one to tell: the root cause was in **ODS**, upstream of the warehouse, so the fix went back to the source and through testing rather than being patched in the warehouse. *Use for "tell me about resisting a quick fix." Patching downstream would have been faster and would have left the wrong data flowing to every other consumer.*

### 16421, 28168, 32495, 37005 - The voucher grain thread `[both years]`
Duplication in Misc. Adjustment Allocation (2025), duplication in `Fact_PayVoucherAllocation` (2025), a duplicated voucher for 00810 (2026), and missing vouchers for 00982 (2026). Duplication and omission in one domain are usually the same root seen from two sides: when declared grain and real grain disagree, one join path fans out while another filters out. *Tell the duplication and the omission together - the pairing is the insight.*

### 35366 - Fact_TimeAllocation duplicates and cleanup `[2026]`
Duplicate rows inflating charged hours against projects and cost centers - a cost-accounting problem, not just reporting. Two-part fix: stopped the load producing duplicates, then built a maintenance job for records already in the table, shipped as a **limited maintenance package scoped to 00877** so it did not wait on a full release or touch tenants that did not need it. *Use for "fixed both the cause and the damage," or for blast-radius reasoning.* Continuity: `31616` was the same table missing punch data for 00979 in 2025.

### 36119 - Deadlocks on client databases `[2026]`
Stored procedures deadlocking on client databases. The worst class of production defect to chase: load-dependent, intermittent, passes every test, then fails under real concurrency with the victim transaction dying half-done. *Strong "hardest bug you have debugged" answer - lead with why deadlocks resist normal debugging.*

### 36429 - Fix all three repos, not the one that shouted `[2026]`
Reporting databases could not be built from `release/2025.07.25` - release-blocking, because you cannot validate a release you cannot build. Root cause was a stale agent name in the pipeline YAML. The minimum fix was one repo; I updated **all three** (Full Load, Incremental, Employer Reports) because the other two carried the same stale reference and simply had not been built yet. *Small story that tells an interviewer exactly how you work: when you find a bug, you ask where else it lives.*

### 27353 - The 12/31/1900 approval date `[2026]`
Every record in `Fact_PTODetails` stamped with `12/31/1900` - the SQL Server zero-date sentinel - plus an incorrect approved flag. A technical default escaping into business data: nothing errors, but the **approval audit trail is fiction**. Corrected so the flag reflects the real approval event and unapproved records carry NULL. *Excellent for "a bug that did not throw an error," and a clean way to discuss representing absence correctly instead of substituting a placeholder that reads as data.*

### 30497, 25661, 14778, 28947 - The missing-data cluster `[2025]`
`Fact_BenEnroll` missing updated enrollment information; `Fact_StatsLogon` missing login activity; `Fact_StatsReports` not reflecting job and classification fields; the 00972 Weekly Store Report. All the same shape: **rows or attributes that should be present and are not.** *Use to make the point that missing data is harder to catch than wrong data - the report renders cleanly and simply under-reports, so nothing looks anomalous.*

### 29462 - ShrinkDB optimization `[2025]`
Storage and performance optimization in VC. *Minor, but useful when asked about cost or storage management.*

### 31617 - Inconsistent payroll amounts for 00630 `[2025]`
Custom reporting showing payroll amounts that did not agree with each other. Inconsistency across reports usually means two paths computing one figure differently - a modeling problem, not arithmetic. *Note the continuity: this is the same client whose CDC incremental path you later owned and restored in 2026.*

### 33436 - Reissued vouchers, handed off `[2026]`
Triaged and handed to a colleague. Voucher reissue is a distinct upstream event lifecycle and belonged with the owner of that path. *Do not hide this. "I diagnosed it, determined it belonged upstream, and handed it off with context" is a better answer than pretending you closed everything. Interviewers trust candidates who distinguish what they own from what they routed.*

### 16235 - Rerouting incorrect in some instances `[2025]`
A workflow routing defect affecting some instances. *"In some instances" is the interesting part - intermittent, conditional defects are harder than deterministic ones because reproduction is the whole battle.*

---

# Section 15: Question-to-story map

| If they ask... | Tell... |
|---|---|
| "Walk me through your background" | The story above the stories - the two-year arc |
| "Technical problem you are proud of" | Story 2 (accrual cluster) or Story 1 (Data Checker) |
| "Tell me about something you built" | Story 1 (Data Checker), Story 13 (Attestations) |
| "Improving performance or reducing cost" | Story 3 (CDC, 30 min to 8, -67%) |
| "How do you ensure data quality?" | **Story 1.** This is your best answer and most candidates have nothing comparable |
| "Describe something you automated" | Story 8 (Copy Down) |
| "Tell me about a production incident" | Story 3 second half (00630), Story 7 (hotfixes), SSRS crash RCA |
| "Hardest bug you have debugged" | 36119 (deadlocks) or Story 6 (incremental divergence) |
| "A bug that did not throw an error" | **Story 5 (basis logic)**, 27353 (12/31/1900), or 14825 (W-4) |
| "A bug with real-world consequences" | Story 5 (silent money), Story 10 (SECURE 2.0) |
| "Explain slowly changing dimensions" | Story 12 - a production instance, not a definition |
| "How do you handle CDC schema evolution?" | **Story 4.** Have this ready; it is the standard senior CDC follow-up |
| "Data modeling experience" | Story 13 (Attestations), then Story 12 (SCD Type 2) |
| "Working with another team" | Story 11 (app logic), Story 1 (IT on training03) |
| "Going beyond your assigned task" | Story 1, Story 4, or 36429 (three repos) |
| "Competing priorities" | Story 2 - four clients, one structural fix |
| "A mistake or something you would redo" | Story 2 - counting 2025, that surface leaked for over a year |
| "Something you handed off" | 33436 - answer it straight |
| "Experience with CI/CD" | Story 9, then Story 8 and 36429 |
| "Ambiguity" | Story 11 - divergent logic, no documented source of truth |
| "Resisting a quick fix" | 16518 - fixed in ODS, not patched downstream |
| "Regulatory or compliance work" | Story 10 (SECURE 2.0), plus the W-4 items |
| "Why should we hire you?" | The two-year arc: correctness earned the platform ownership |

---

## Four habits these stories demonstrate

More memorable than any individual ticket. Surface these whatever the question.

1. **When a bug appears repeatedly, fix the model, not the row.** Story 2: four tickets, one design flaw. Story 5: four tickets, one incomplete basis.
2. **When you find a bug, ask where else it lives.** 36429: three repos, not one. Story 11: every tenant, not just the complainer. The three MERGE failures: one cause, found three times.
3. **Fix the damage, not just the cause.** Story 11 and 35366 both shipped backfills. Stopping the bleeding is half the job.
4. **When you keep finding defects the same way, change the way you find them.** Story 1. This is the habit that separates the two years, and the one worth leading with.
