# ExponentHR Work Item Story Bank

Interview-ready stories covering 2025 and 2026 year to date at ExponentHR.

This document intentionally carries no internal ticket numbers, client account identifiers, internal table/schema names, internal environment names, or internal tool names. Stories describe the technical mechanism and the defect class generically.

**Companion documents:**
- [`exponenthr-accomplishments.md`](./exponenthr-accomplishments.md) - the delivery record
- [`exponenthr-star-impact-points.md`](./exponenthr-star-impact-points.md) - condensed, resume-ready STAR points
- [`career-positioning-2026.md`](./career-positioning-2026.md) - how to sell this in the 2026 market

---

## Before you use this

> **Read this first.** Corrections are marked inline with `[corrected]` or `[attribution corrected]` in the story titles - **read those first**, they change what you should actually say. Stories without that tag are reconstructed at the level of the engineering pattern, so confirm specific details before relying on them in an interview.
>
> **Worth knowing before you use any of these stories:** a recurring pattern in this record is that this candidate is the one who diagnosed the defect and specified the fix, while a teammate implemented and validated it. That is a legitimate, still-strong story - identifying root causes and specifying fixes is real senior-level work - but it means "diagnosed and specified the fix" is often the honest claim, not "personally implemented." Stories 2, 5, 6, 8, and 11 were corrected on exactly this basis; favor "diagnosed" language over "fixed" language unless a story is explicitly marked fully verified.
>
> Each Tier 1 story ends with a **Fill in** line naming what still needs recovering.

### How the tiers work

- **Tier 1 (14 stories)** - full STAR, follow-up questions, what each proves. These carry your interviews. Three (Stories 2, 8, 11) were corrected after verification; one (Story 14) is new and fully verified.
- **Tier 2** - one paragraph each, for second examples and breadth.
- **Section 15** maps interview questions to stories.

Stories are tagged `[2025]`, `[2026]`, or `[both years]`.

---

## The story above the stories

Before any individual story, know the shape of the two years. This framing is worth more than any single story, and most candidates cannot offer anything like it.

> "My first year was correctness. I worked about 29 items across the whole warehouse - vouchers, deduction basis logic, W-4, time punches, benefits, employee action notices - plus production hotfixes and release support across eight cycles. By the end of it I knew every way that warehouse could go wrong.
>
> That is what earned the second year. In 2026 I stopped fixing rows and started owning the machinery: CI/CD end to end, CDC rebuilt from full reloads to incremental, an automated database provisioning pipeline for a clustered SQL Server environment, new dimensional models from scratch.
>
> The turning point was in the middle. In 2025 I built a validation framework driven by a control table, because I got tired of learning about defects from clients. And I worked out and documented how to deploy CDC schema changes safely. Those two are why the 2026 platform work was possible at all."

**Why this works:** it answers "are you senior?" without you having to claim it. You describe a progression from reactive to architectural, with a named turning point. Interviewers hear trajectory.

---

# Tier 1: Headline stories

---

## Story 1: Building the thing that finds the bugs `[2025]`

**Workstream:** A control-table-driven data validation framework, built from scratch and deployed to a shared test environment

### Situation
Every data defect I worked in 2025 - and there were 29 of them - arrived the same way: a client noticed. Wrong voucher descriptions, duplicated allocations, missing login activity, incorrect accrual for terminated employees. The warehouse had no systematic validation. The detection mechanism was a customer complaint.

### Task
Nobody assigned this. The assigned work was the tickets.

### Action
Built a validation framework driven by a **control table**. The design decision that matters: validation rules are **configuration, not code**. A new check is a row in the control table, not a script someone writes and forgets. That makes coverage additive and cheap - the reason ad hoc validation scripts always decay is that adding one is a development task.

Deployment crossed a team boundary. Getting it running on a shared test environment meant working through security and connectivity issues with the infrastructure team.

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

## Story 2: Four clients, one root cause `[2026]` `[attribution corrected]`

**Work:** A paid-leave accrual data-model cluster spanning four client organizations

> Not every client symptom in this cluster reflects direct hands-on work from this engineer. See the corrected framing in Action and Result below - it is still a strong story, just a more precisely true one.

### Situation
A paid-leave accrual summary generated a steady stream of escalations. Four clients, four differently-worded reports: one had a wrong accrual rate; another had rates displaying as a floating-point artifact, and rates showing against plans employees were not eligible for; a third had employees missing entirely; a fourth had stale data.

Related history: back in 2025, a defect had accrued hours displaying incorrectly for a terminated employee with a cleared balance. A separate defect on the same paid-leave surface - a fabricated sentinel approval date - is still open as of this writing, actively being diagnosed - not resolved. **This surface has been producing defects for over a year, and part of it still is.**

### Task
Four bug reports. Closing them individually was the expected path.

### Action
Lined up together, the failure modes pointed at one design choice: **accrual rate was derived inline during the load rather than sourced from a modeled, plan-aware definition.** In-flight logic drifts across tenants, loses precision, and has nowhere to enforce eligibility. That one choice explains the pattern across all four.

Attribution, precisely stated rather than assumed:

1. **The structural fix** - added a dedicated accrual table, making rate and plan configuration a stored, versioned asset. **Fully confirmed**: created, specified in detail, and driven by me directly. This is the actual structural fix.
2. **The wrong-accrual-rate item** - **fully confirmed**, direct hands-on SQL diagnostic work in my own words.
3. **The non-eligible-plans item** - assigned to a teammate for execution, but the eligibility-flag design is credited to a direct conversation with me in a colleague's comment. Legitimate design credit, not hands-on implementation.
4. **The floating-point-display item** - one indirect mention of me explaining the underlying float-precision behavior to another team member. Weaker evidence; describe it as design input, not a fix I personally shipped.
5. **The stale-records item and the missing-employees item** - no visible involvement in the record reviewed. Do not claim these as personally resolved.
6. **The rate-calculation change request** - assigned to a colleague; no direct evidence I authored it, though it is consistent with and likely informed by the diagnostic work above.

### Result
The structural fix shipped, closing the design flaw at its root. Individual client reports in the cluster resolved on the timeline the team's rollout allowed - not all of them through my own hands, but through the model I specified being deployed. That is the honest and still strong claim: **I owned the fix that the cluster's resolution depended on.**

### Why it lands
Paid-leave balance is not a dashboard number. Employees plan against it, managers approve against it, and **at termination it converts to money.** Say that sentence.

### What it proves
Systems thinking over ticket-closing - recognizing a shared root cause across four clients and building the structural fix everyone else's rollout depended on, rather than claiming personal credit for every symptom report in the cluster.

### Follow-ups to expect
- *"How did you know it was one cause and not four?"* - The float-precision artifact and the missing-eligibility-filter rates are the tell. Both mean the rate is being computed where it should be looked up.
- *"Did you personally close all four client reports?"* - No, and say so. You designed and built the accrual table; the team executed the rollout across tenants. That is an accurate, still-strong answer - overclaiming personal execution on items you didn't touch is the failure mode to avoid here.
- *"What would you do differently?"* - Catch it earlier, and close the remaining open item.

**Fill in:** current status of the still-open approval-flag defect, whether the two unattributed items involved you in any way not visible in this record, employees or plans affected overall.

---

## Story 3: Thirty minutes to eight, and defending it `[both years]`

**Work:** A CDC schema-change deployment process (2025); CDC incremental reengineering (2026); a production CDC incremental failure (2026)

### Situation
The warehouse refreshed via full-table reloads - roughly 30 minutes, with compute cost scaling to total table size rather than to what changed.

### Task
Cut runtime and cost without risking correctness on a payroll-critical platform.

### Action
This is a two-year story, and the sequencing is the point.

**2025 - groundwork.** Before touching the pipeline I researched, tested, and documented a **CDC schema-change deployment process**. You cannot safely rebuild a CDC pipeline until you know what happens when a source table changes underneath it.

**2026 - the rebuild.** Reengineered from full reloads to **incremental merge-upserts**, processing only changed rows. The engineering that matters is not the merge - it is making the incremental path safe to rerun. Incremental loads fail in ways full reloads do not: broken watermarks, bad change-tracking state, partial application. Built it idempotent so a failed run reruns cleanly instead of requiring a DBA to reason about half-applied state.

**2026 - defending it.** One client hit a CDC incremental failure in production. Highest-stakes failure mode on the platform: when incremental breaks, the options are a slow full reload or stale client data, and neither is acceptable on payroll. Diagnosed and restored the incremental path **without falling back to full reload.**

### Result
30 minutes to under 8. Compute cost down 67%. When it broke in production, restored on the fast path.

### Why it lands
Cost reduction is the most fundable thing on a 2026 data team. But the arc is what separates this from a resume bullet: **you did the safety research first, built the optimization second, and defended it under production failure third.** Most candidates can show a speedup. Almost none can show that sequence.

**Fill in:** the actual production-failure root cause, your reconciliation method against full reload, client impact duration.

---

## Story 4: Schema evolution on a CDC source `[2025]`

**Workstream:** CDC schema-change deployment process - research, testing, documentation

### Situation
CDC capture mechanisms are bound to a table definition. When a source table changes, things break in quiet ways: capture can fail, the new column can be silently dropped from the capture instance, or the instance needs rebuilding with a gap to reconcile. The team had no established process.

### Task
Not assigned as a ticket. I took it on because I could see it coming.

### Action
Researched the failure modes, tested the approaches against real schema changes, and **wrote the process down for the team.** Concrete instances handled in the same period included a time-tracking dimension schema change and schema foundation work for a new expense-reporting subject area.

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

## Story 5: The silent money bug `[2025]` `[attribution corrected]`

**Work:** An incomplete basis-resolution cluster across three recurring payroll item types

> **Corrected.** Only one item in this cluster is clearly this candidate's own (he created it). The other three cannot be confirmed as his direct work - an earlier claim of having carried a related item to code complete is not supported and has been dropped. Use the narrower, honest version below.

### Situation
Four defects across three recurring item types shared nearly the same symptom description: a deduction recurring item, an employer-contribution recurring item, and an earning recurring item all reported incomplete basis coverage, and a fourth item reported an employer contribution's total-compensation category not picking up base salary.

### Task
Identify and fix an incomplete basis-resolution defect on the employer-contribution item type.

### Action
Identified (created the report for) the employer-contribution basis defect: the recurring-item basis resolution did not cover every valid case. This is the same defect class visible across the other three items above, whichever team member ultimately worked each one - the set of values a recurring item could be calculated against did not cover every valid case, producing a plausible-but-wrong result rather than an error.

### Result
Closed the employer-contribution instance of the defect. The broader pattern across deduction and earning item types is real domain knowledge to discuss, but describe it as **a defect class you recognized and can explain**, not as four items you personally fixed.

### Why this is still a strong "consequences" story
**Nothing errors.** A partial basis produces a plausible number that is simply too small, applied to real employee contributions. No exception, no alert, no anomalous-looking report. Just money that is quietly wrong for anyone whose basis included the missing component. That is a better answer to "tell me about a bug with real consequences" than any crash story, precisely because the danger is that it does not crash - just be precise about which item is actually yours.

### What it proves
Domain depth in payroll calculation. Be honest that the cross-item-type pattern recognition is an observation about the defect class, not a claim of having personally traced and fixed all three item types.

### Follow-ups to expect
- *"How did you find the missing basis values?"* - Recover this. Comparing against the source's valid set is the likely method.
- *"How would you prevent it?"* - **A validation-framework rule asserting basis completeness.** Connect your own two stories; interviewers notice when your work coheres.

**Fill in:** which basis values were missing on the confirmed item specifically, financial impact if quantified. Do not claim ownership of the other three items without independently confirming your role on each.

---

## Story 6: When incremental and full load disagree `[2025]` `[attribution corrected]`

**Work:** A W-4 population-rule divergence between the incremental and full load paths

> **Corrected.** Neither underlying item is created by or assigned to this candidate. One shows no confirmed involvement from him. The other is better described as a business-rule clarification he contributed, not a claim of having written the fix. Tell this story as a diagnosis/framing contribution, not as a personally-implemented fix.

### Situation
Contractors were appearing in W-4 election data where they did not belong - and critically, the report noted it was **the incrementals** adding them. Separately, one client's full load needed a join change in the W-4 elections fact table.

### Task
Clarify why contractors should never appear in W-4 election data, so the team could align the incremental and full-load population rules.

### Action
The detail that matters is *incremental only*. When a defect appears on the incremental path but not the full load, the two paths **disagree about what qualifies for inclusion**. Contributed the governing business rule that resolved the ambiguity: contractors do not have W-4 elections by definition, so the incremental filter needed to exclude them the same way the full load already did.

This class of bug is dangerous for a specific reason: **a full reload appears to fix it.** The bad rows vanish, everyone moves on, and the cause is still there waiting for the next incremental run.

### Result
Population rules aligned across full and incremental paths, informed by the clarified business rule.

### Why this story is stronger than it looks
It shows you read the *shape* of a bug report, not just its content. "Incrementals appear to be adding contractors" contains its own diagnosis if you know what to listen for, and most engineers would have reloaded and closed it.

It also sets up a great line about your CDC work: *"That is why, when I rebuilt the CDC pipeline the next year, reconciling incremental against full reload was the first thing I validated."*

### Follow-ups to expect
- *"How do you test that the two paths agree?"* - Run both, compare row counts and checksums. Have this ready; it is the real question.
- *"Would a full reload have fixed it?"* - Temporarily, and that is the trap. Say so.

**Fill in:** the actual population rule that diverged, how you validated the fix.

---

## Story 7: Two hotfixes under payroll pressure `[2025]`

**Work:** Two production hotfixes on payroll-critical tables

### Situation
Two defects that could not wait for a release.

**The first:** a pay voucher detail fact table was **replicating an already-processed payroll run.** Duplicated payroll data, on a dated payroll cycle.

**The second:** a text column's length differed between the base table and its warehouse dimension. Length mismatches **truncate silently on load** - no error, values just arrive shortened.

### Task
Ship both outside the normal release cycle.

### Action
Diagnosed and shipped as hotfixes. The first meant identifying why the voucher detail load was reproducing an entire payroll run's rows - a grain or rerun-idempotency failure on the most sensitive table in the warehouse. The second meant reconciling the schema mismatch and dealing with values already truncated.

### Result
Both resolved out of cycle.

### Why to use this
Two things interviewers want evidence of: **you can work under production pressure**, and **you have shipped outside the safety of a normal release**. Hotfix experience is a proxy for trust - organizations do not let junior engineers hotfix payroll tables.

The second detail is also a good "silent failure" example: a length mismatch does not throw. It truncates.

### Follow-ups to expect
- *"What was your rollback plan?"* - Have an answer. Hotfix questions are really risk-management questions.
- *"How did you verify the fix before shipping?"* - The core of hotfix discipline.
- *"How did you prevent recurrence?"* - Ideal place to mention the validation framework.

**Fill in:** actual root causes, turnaround time, how you validated under time pressure.

---

## Story 8: An hour of DBA work, twenty times a day `[2026]`

**Work:** An automated database provisioning pipeline for a clustered SQL Server environment

### Situation
Support, testing, and bug reproduction all needed refreshed client databases - 20+ requests daily. On a clustered, contained Always-On Availability Group environment this is much harder than a restore: remove the database from the cluster, restore, reconcile security and CDC state, validate listener health. Every step manual, on a payroll-critical cluster, where a missed step leaves a database half-joined.

### Action
Built and hardened an idempotent Azure DevOps pipeline covering the full sequence, one click end to end.

Three decisions worth naming:

1. **A hard guard blocking execution against a live production server.** A hard stop, because the failure it prevents is provisioning over production.
2. **Idempotency.** A failed run reruns safely. Without it, partial failure means a DBA reasoning about unknown state at an unknown hour.
3. **Logging detailed enough to diagnose partial failures** without an ad hoc DBA handoff.

Validated the contained-cluster path against a newer SQL Server version on a dedicated test environment - catching version incompatibility on a test environment rather than mid-request. Then moved the tool's own deployment onto the standard CI/CD platform so the automation ships through the same governed path as everything else.

**Verified detail** - this is the single most confidently attributable item in the whole record (created, specified, and hands-on documented by me directly). The 2026 enhancement pass, specifically:
- **The CDC job cleanup had a real bug**: the code cleared job-tracking metadata but never actually removed the underlying SQL Server Agent capture and cleanup jobs. Metadata looked clean; the scheduled jobs kept running. Rewrote it to call SQL Server Agent's job-deletion procedure directly.
- Added an existence-and-CDC-enabled guard before disabling CDC on a database, including killing any active replication command session first - disabling CDC out from under a live session was a real failure mode.
- Added restore-procedure parameters that had been silently defaulting to the wrong behavior.
- Added detection and forced recovery for databases stuck mid-restore.
- Added pre-flight existence checks so an in-progress drop can't race a new provisioning request.

That level of specificity is worth using verbatim in an interview - it is much stronger than "I built an idempotent pipeline."

### Result
~1 hour of manual orchestration removed per request, 20+ requests per day. The operation became rerunnable rather than requiring DBA intervention on partial failure.

### What it proves
Not "I wrote a script" - guard rails, idempotency, version validation ahead of need, and treating the automation itself as a deployable product.

### Follow-ups to expect
- *"How did you make it idempotent?"* - Lead with the job-cleanup fix. That is a real, specific bug story, not a generic idempotency answer.
- *"Why a hard stop rather than a warning?"* - The cost is asymmetric. Warnings get clicked through.

**Fill in:** hours saved per month, whether support self-serves now, environments covered.

---

## Story 9: Ten release cycles and a 3-month problem `[both years]`

**Work:** 8 release cycles in 2025, 2 platform sprints in 2026, end-to-end CI/CD ownership

### Situation
The deployment cycle ran roughly 3 months. The bottleneck was not build time - it was cross-team idle time, handoffs waiting on handoffs.

### Action
**2025:** supported release execution across eight cycles, including release-branch management and code promotion into testing. That is where I learned where the time actually went.

**2026:** took end-to-end ownership of CI/CD through Azure DevOps and drove delivery across two full sprint cycles as owner.

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

**Work:** SECURE 2.0 regulatory compliance delivery, alongside a time-tracking enhancement, through a scheduled release

### Situation
SECURE 2.0 is US retirement legislation with provisions phasing in across multiple years. Payroll platforms have to support it. The deadline is set by law.

### Action
Delivered the data layer support through a scheduled release cycle, alongside a related time-tracking enhancement.

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

## Story 11: Escalating a symptom to its real, upstream cause `[2026]` `[corrected]`

**Work:** A performance-review reporting divergence, resolved for one client and escalated to the product team

> **This story is corrected.** The earlier version claimed the application's row-selection logic was reimplemented directly in the ETL load - that is not accurate. The corrected story below is narrower, and arguably better: recognizing an upstream cause and driving a cross-team escalation, rather than personally reimplementing app logic.

### Situation
A performance-review reporting object was failing in both directions at once. One client was getting extra rows. Other clients were missing data entirely.

### Action
Over-population and under-population in the same object is a specific signal: **the warehouse's row-selection logic and the application's had diverged** somewhere upstream. Fixed the one-client symptom directly in the warehouse. But instead of treating that as done, recognized the divergence traced to an **application-level data model gap** - the product had no single, authoritative definition of "which review record counts" for the warehouse to mirror. Raised and drove a separate cross-team item to push the product team to address the actual root cause, rather than let every future client hit the same defect through a different symptom.

Shipped a maintenance package to backfill clients already under-reported rather than only fixing forward.

Related: a 2025 defect in the same subject area was a performance-goals dimension not recognizing a specific status code - the same class of incomplete domain handling.

### What it proves
**This is a better interview answer than the original, not a weaker one.** Most engineers fix the symptom in their own system and stop. Recognizing that a warehouse defect is actually evidence of an upstream product gap, and escalating cross-functionally to get it addressed at the source instead of just absorbing it downstream, is a more senior instinct than reimplementing someone else's logic yourself.

### Follow-ups to expect
- *"Why didn't you just fix it in the ETL?"* - Because the same gap would keep producing new symptoms for other clients. Fixing the visible case and escalating the cause are both required; one without the other is incomplete.
- *"Did the product team actually fix it?"* - Recover this before using the story. If they didn't, the honest answer is that you escalated correctly and the ball is elsewhere - which is still a legitimate outcome to describe.

**Fill in:** what the product team actually changed as a result of the escalation, and whether the underlying data model gap has recurred since.

---

## Story 12: Point-in-time correctness `[2026]`

**Work:** A slowly changing dimension (SCD Type 2) end-dating defect for one client

### Situation
One client had incorrect effective end dates in a core employee-history dimension.

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

**Work:** A new compliance-relevant dimensional model, designed from scratch

### Situation
A compliance-relevant subject area existed in the application but had no warehouse representation - data that could not be reported, trended, or audited alongside the rest of the HR data.

### Action
Greenfield modeling: established the fact grain, built conformed dimensions so the new subject area joins cleanly to existing employee and organizational dimensions, and integrated it into the load and release process.

### Result
A reportable, auditable subject area.

### Why you need this in the rotation
Most of your record is repair work. Excellent repair work, but an interviewer scanning it will wonder **whether you can build or only fix.** This is the answer, and you should volunteer it rather than wait.

Pair with the expense-reporting subject area (Tier 2), where you scripted the schema foundation in 2025 and delivered reporting support in 2026 - a build you carried across both years.

### Follow-ups to expect
- *"What grain did you choose and why?"* - The central question in dimensional design.
- *"What did you get wrong?"* - Have something. A model you would grain differently in hindsight is credible.

**Fill in:** the grain, which conformed dimensions it reuses, who consumes it.

---

## Story 14: Naming the failure modes nobody was watching for `[2026]` `[new, fully verified]`

**Work:** Proactive monitoring and self-healing recovery for daily incremental SQL Agent jobs

### Situation
The incremental ETL pipeline ran daily client jobs starting overnight, typically finishing before morning. There was no detection layer for failure. When a job silently failed, never started, or got stuck mid-execution, the gap was discovered manually - sometimes hours or days later, by which point the CDC change log could already be past its retention window and unrecoverable.

### Task
Build detection for a category of failure that had none, before the next silent gap became a permanent data loss.

### Action
Named three distinct, previously uncovered failure modes, each requiring different detection logic:

1. **Missed run** - the scheduled job never fired or was skipped, and nobody was notified.
2. **Stuck run** - a long-running query, lock contention, or blocked process held the job open past its window, delaying the next cycle.
3. **Silent failure** - the job crashed without logging an end time, so it appeared neither complete nor running - a naive "did it run today" check would misclassify it as still in progress.

### Result
A monitoring and self-healing layer covering all three failure modes, closing a gap where data loss was previously discovered only by accident and only after the recovery window had likely already closed.

### Why this is a strong, safe story to tell
This is the cleanest example in the whole record of naming a problem precisely enough to solve it. "Add monitoring" is generic. Naming three distinct failure modes - each with a different signature and a different detection strategy - is what a senior reliability engineer actually does, and it demonstrates you understand *why* naive health checks fail (a stuck job and a missed job look identical to a check that only asks "did anything run").

It is also fully verified: created, specified, and entirely authored by this engineer, with no attribution ambiguity.

### What it proves
Reliability engineering maturity - the instinct to ask "how would this fail silently" before it does, not after.

### Follow-ups to expect
- *"How do you tell a stuck run from a slow-but-healthy one?"* - Have a threshold answer ready.
- *"What's the recovery action for each mode?"* - "Self-healing" implies an automated response, not just an alert. Know what actually happens for each of the three cases.
- *"How did you validate it doesn't false-positive?"* - A monitoring system that cries wolf gets ignored. Have an answer.

**Fill in:** the actual detection thresholds and self-healing actions for each failure mode, and whether it has caught a real incident since deployment.

---

# Tier 2: Supporting stories

### A production reporting-server crash root cause analysis `[2025]`
Not "restarted the server" - root cause analysis on a production reporting-server crash. *Use for "tell me about a production incident" if you want a second example after the CDC incremental failure, or when asked about ownership beyond your assigned lane.*

### An orphaned dimension key in a time-punch fact table `[2025]`
A time-punch fact table carried a dimension key that did not exist in the corresponding dimension - a textbook referential integrity failure. The consequence is subtle: an inner join makes those punches **vanish from reports** while the rows still sit in the fact table, so the data looks present and reports silently under-count. Fixing it means repairing the data and closing the write path that allowed an unmatched key. *Strong answer for "how do you enforce referential integrity" and a natural lead-in to the validation framework story.*

### Three MERGE failures, one cause `[both years]`
A W-4 election dimension for one client (2025), an authoring dimension for another client (2025), a reporting-type dimension for a third client (2026). All the same failure: a target row matched by more than one source row, so MERGE cannot decide which update wins and aborts. **These are hard failures** - the load stops and client data goes stale until someone fixes it. Each was resolved by fixing the source-to-target key relationship so one target row matches at most one source row. *Tell all three together. Three instances of one root cause across two years is a much better answer than one instance, and it sets up "what would you do differently" - a uniqueness check on the source would have caught every one.*

### Two status-domain gaps `[2025]`
A performance-goals dimension not recognizing a specific status code, and an employee action notice showing one workflow status when it should have shown another. Same class: the warehouse's set of valid status values was narrower than the source's, so unmapped statuses fall through to a default or fail to match. Workflow status drives what users act on, so this is operational, not cosmetic. *Good for "tell me about an assumption that turned out wrong."*

### Two composite-field defects `[2026]`
A state-allowances field carried filing status **and** the allowances value in one field; a separate W-4 election dimension carried election status inside the allowances value. One violation, twice: **one attribute per column.** Any consumer treating allowances as numeric - withholding calculation, compliance reporting, any aggregate - read a contaminated value. Separated so each attribute stands alone. *Small items, big domain: this is tax withholding input, so the bar is regulatory. Also a clean answer to "a bug that did not throw an error" - a packed field silently returns a plausible number.*

### Attribute resolution, and fixing at the source `[2025]`
A voucher code short description and a piecework allocation description both resolving incorrectly. The second is the one to tell: the root cause was in the upstream **operational data store**, so the fix went back to the source and through testing rather than being patched in the warehouse. *Use for "tell me about resisting a quick fix." Patching downstream would have been faster and would have left the wrong data flowing to every other consumer.*

### The voucher grain thread `[both years]`
Duplication in a miscellaneous adjustment allocation (2025), duplication in a pay-voucher allocation fact table (2025), a duplicated voucher for one client (2026), and missing vouchers for another client (2026). Duplication and omission in one domain are usually the same root seen from two sides: when declared grain and real grain disagree, one join path fans out while another filters out. *Tell the duplication and the omission together - the pairing is the insight.*

### Time-allocation duplicates and cleanup `[2026]`
Duplicate rows inflating charged hours against projects and cost centers - a cost-accounting problem, not just reporting. Two-part fix: stopped the load producing duplicates, then built a maintenance job for records already in the table, shipped as a **limited maintenance package scoped to the one affected client** so it did not wait on a full release or touch clients that did not need it. *Use for "fixed both the cause and the damage," or for blast-radius reasoning.* Continuity: the same table was missing punch data for a different client in 2025.

### Deadlocks on client databases `[2026]`
Stored procedures deadlocking on client databases. The worst class of production defect to chase: load-dependent, intermittent, passes every test, then fails under real concurrency with the victim transaction dying half-done. *Strong "hardest bug you have debugged" answer - lead with why deadlocks resist normal debugging.*

### A reporting database build blocked on the release branch `[2026]` `[corrected]`
Reporting databases could not be built from a specific release branch - release-blocking, because you cannot validate a release you cannot build. Confirmed root cause: a pipeline configuration file that never made it onto the release branch. *An earlier framing and a claim that the fix spanned multiple repositories are not corroborated in the verified record - use the confirmed version (a missing pipeline configuration gap blocked reporting database builds) and don't claim the multi-repo fix as fact unless you confirm it yourself first.*

### The fabricated sentinel approval date `[2026]` `[status corrected: still open]`
Every record in a paid-leave detail fact table stamped with a fabricated zero-date sentinel value, plus an incorrect approved flag. A technical default escaping into business data: nothing errors, but the **approval audit trail is fiction**. *Correction: this is still open, not resolved.* The most recent lead points to missing rows in a time-clock link table feeding the approval join. Frame it as "actively diagnosing," not "fixed" - it is still an excellent answer for "a bug that did not throw an error," you just describe it as in-progress work rather than a closed win.

### The missing-data cluster `[2025]`
A benefits-enrollment fact table missing updated information; a logon-activity fact table missing login activity outright; a statistics fact table not reflecting job and classification fields; a client-specific reporting defect. All the same shape: **rows or attributes that should be present and are not.** *Use to make the point that missing data is harder to catch than wrong data - the report renders cleanly and simply under-reports, so nothing looks anomalous.*

### A storage optimization `[2025]`
Storage and performance optimization on a version-control-adjacent database. *Minor, but useful when asked about cost or storage management.*

### Inconsistent payroll amounts for one client `[2025]`
Custom reporting showing payroll amounts that did not agree with each other. Inconsistency across reports usually means two paths computing one figure differently - a modeling problem, not arithmetic. *Note the continuity: this is the same client whose CDC incremental path you later owned and restored in 2026.*

### Reissued vouchers, handed off `[2026]`
Triaged and handed to a colleague. Voucher reissue is a distinct upstream event lifecycle and belonged with the owner of that path. *Do not hide this. "I diagnosed it, determined it belonged upstream, and handed it off with context" is a better answer than pretending you closed everything. Interviewers trust candidates who distinguish what they own from what they routed.*

### Rerouting incorrect in some instances `[2025]`
A workflow routing defect affecting some instances. *"In some instances" is the interesting part - intermittent, conditional defects are harder than deterministic ones because reproduction is the whole battle.*

---

# Section 15: Question-to-story map

| If they ask... | Tell... |
|---|---|
| "Walk me through your background" | The story above the stories - the two-year arc |
| "Technical problem you are proud of" | Story 2 (accrual cluster) or Story 1 (validation framework) |
| "Tell me about something you built" | Story 1 (validation framework), Story 13 (new dimensional model) |
| "Improving performance or reducing cost" | Story 3 (CDC, 30 min to 8, -67%) |
| "How do you ensure data quality?" | **Story 1.** This is your best answer and most candidates have nothing comparable |
| "Describe something you automated" | Story 8 (database provisioning) |
| "Tell me about a production incident" | Story 3 second half (CDC incident), Story 7 (hotfixes), reporting-server crash RCA |
| "Hardest bug you have debugged" | The deadlocks story or Story 6 (incremental divergence) |
| "How do you monitor and detect failure?" | **Story 14 (new, fully verified)** - naming three distinct failure modes for silent pipeline failure |
| "A bug that did not throw an error" | **Story 5 (basis logic)** or the composite-field story. *Not the fabricated-date story as a closed example - it is still open; use it only as an in-progress diagnosis story.* |
| "A bug with real-world consequences" | Story 5 (silent money), Story 10 (SECURE 2.0) |
| "Explain slowly changing dimensions" | Story 12 - a production instance, not a definition |
| "How do you handle CDC schema evolution?" | **Story 4.** Have this ready; it is the standard senior CDC follow-up |
| "Data modeling experience" | Story 13 (new dimensional model), then Story 12 (SCD Type 2) |
| "Working with another team" | Story 11 (corrected: escalating to the product team, not reimplementing their logic), Story 1 (the infrastructure team on the shared test environment) |
| "Going beyond your assigned task" | Story 1, Story 4, or Story 14 |
| "Competing priorities" | Story 2 - four clients, one structural fix (attribution corrected - own it as the fix, not as personally closing every ticket) |
| "A mistake or something you would redo" | Story 2 - counting 2025, that surface leaked for over a year, and part of it still is |
| "Something you handed off" | The reissued-vouchers story - answer it straight |
| "Experience with CI/CD" | Story 9, then Story 8 |
| "Ambiguity" | Story 11 (corrected) - divergent logic, no documented source of truth, resolved by escalating rather than absorbing it |
| "Resisting a quick fix" | The attribute-resolution story - fixed at the source, not patched downstream |
| "Regulatory or compliance work" | Story 10 (SECURE 2.0), plus the W-4 items |
| "Why should we hire you?" | The two-year arc: correctness earned the platform ownership |

---

## Four habits these stories demonstrate

More memorable than any individual item. Surface these whatever the question.

1. **When a bug appears repeatedly, fix the model, not the row.** Story 2: four items, one design flaw. Story 5: four items, one incomplete basis.
2. **When you find a bug, ask where else it lives.** The release-blocking build failure: checked beyond the one repo that surfaced the error. Story 11: every client, not just the complainer. The three MERGE failures: one cause, found three times.
3. **Fix the damage, not just the cause.** Story 11 and the time-allocation cleanup both shipped backfills. Stopping the bleeding is half the job.
4. **When you keep finding defects the same way, change the way you find them.** Story 1. This is the habit that separates the two years, and the one worth leading with.
