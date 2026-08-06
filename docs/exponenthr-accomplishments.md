# ExponentHR Data Engineering: Delivery Record

**Engineer:** Narendranath Edara
**Role:** Data Engineer - Data Warehouse, CDC ETL, Reporting Platform
**Organization:** ExponentHR, Addison, TX
**Coverage:** July 2024 to present, with 2025 as a full year and 2026 year to date (as of August 2026)

This document intentionally carries no internal ticket numbers, client account identifiers, internal table/schema names, or internal tool names. Every section states the technical work, the defect class, and the quantified time or cost impact using generic, industry-standard vocabulary. Time and cost figures are either directly measured or clearly labeled as a derived calculation.

**Companion documents:**
- [`exponenthr-work-item-stories.md`](./exponenthr-work-item-stories.md) - interview-ready STAR stories
- [`exponenthr-star-impact-points.md`](./exponenthr-star-impact-points.md) - condensed, resume-ready STAR points
- [`career-positioning-2026.md`](./career-positioning-2026.md) - market positioning built on this record

---

## 1. Executive summary

ExponentHR runs payroll, benefits, and time-off for thousands of employers. Every figure reaching a client report, a paycheck reconciliation, or a compliance filing passes through the reporting warehouse this role owns.

Two years of work with a clear shape:

**2025 was the correctness year.** 29 resolved work items across the full warehouse surface - payroll vouchers and allocations, deduction and contribution basis logic, W-4 tax election data, time punches, benefits enrollment, performance goals, and workflow status tracking. Two production hotfixes, a server crash root cause analysis, and release support across 8 cycles. This is also the year a **control-table-driven data validation framework** was built from scratch, and the **CDC (Change Data Capture) schema-change deployment process** was researched, tested, and documented for the team.

**2026 is the platform year.** 25 work items, but the center of gravity moved from fixing data to owning the machinery: end-to-end CI/CD ownership, CDC reengineered from full reloads to incremental merge-upserts, a fully automated database provisioning pipeline for clustered SQL Server environments, and new dimensional models designed from scratch.

**The second year was earned by the first.** Deep familiarity with every failure mode in the warehouse is what made it credible to then rebuild the pipelines and release process around it.

### At a glance

| Measure | 2025 | 2026 YTD | Total |
|---|---|---|---|
| Work items | 29 | 25 | **53 unique** |
| Unticketed workstreams | 6 | 5 | 11 |
| Release and sprint cycles | 8 | 2 | **10** |
| Distinct client organizations served | 6 | 11 | **16 unique** |
| Production hotfixes | 2 | - | 2 |
| New frameworks or subject areas built from scratch | 2 | 2 | 4 |

One item spans both years: code complete in 2025, released in 2026. It is counted once. Of the 53, **52 are resolved and 1 is still open** (the paid-leave approval-flag defect in Section 12) - do not describe the full 53 as resolved or closed.

### Platform metrics

| Metric | Result |
|---|---|
| Release cycle | 3 months -> 14 days (~11 weeks idle time removed per release) |
| CDC ETL runtime | 30 min -> under 8 min |
| CDC compute cost | -67% |
| Database provisioning effort | ~1 hour manual orchestration removed per request, 20+ requests/day |

---

## 2. The two-year arc

The most useful way to read this record is as a progression, not two separate years.

| | 2025 | 2026 |
|---|---|---|
| **Center of gravity** | Data correctness across the warehouse | Platform and pipeline ownership |
| **Typical item** | A client-reported defect in a fact or dimension table | A pipeline, release, or model design change |
| **Mode** | Reactive plus systematic - fix, then find the class | Proactive - rebuild the machinery |
| **Signature deliverable** | Control-table-driven data validation framework | CI/CD ownership and CDC incrementalization |
| **What it built** | Complete knowledge of every failure mode | The ability to fix the class, not the instance |

Two 2025 workstreams are the hinge between the years:

1. **A metadata-driven data validation framework**, built on a control table. The move from finding defects by client report to catching them systematically.
2. **A CDC schema-change deployment process** - researched, tested, and documented. The groundwork the 2026 CDC incremental reengineering was built on.

Neither was a ticket handed down. Both are the kind of work an engineer takes on after seeing enough failures to know what is missing.

---

# Part I: 2025

## 3. Payroll, vouchers, and allocations

The voucher and allocation surface produced defects in every direction: six resolved items spanning duplication, misresolved attributes, and inconsistent totals.

**Duplication.** Three separate duplication defects in pay allocations and voucher detail, one of them a **production hotfix**: a payroll voucher detail fact table was replicating an already-processed payroll run. Duplicated payroll data is about as urgent as reporting defects get, and it shipped outside the normal release cycle.

**Incorrect attribute resolution.** A voucher code short description and a piecework allocation description were both resolving incorrectly. One traced back to the upstream operational data store and was fixed at the source rather than patched in the warehouse - the right call, and it went back through testing accordingly.

**Inconsistent totals.** One client's custom reporting showed payroll amounts that did not agree with each other. Inconsistency across reports usually means two paths computing the same figure differently, which is a modeling problem rather than an arithmetic one.

---

## 4. Deduction, earning, and contribution basis logic

The most coherent defect cluster of 2025, and the clearest example of a shared root cause surfacing as separate tickets. Five resolved items across three recurring item types - deductions, earnings, employer contributions.

Across earnings, deductions, and employer contributions, the same failure recurred: **the basis resolution was incomplete.** The set of values a recurring item could be calculated against did not cover every valid case, so amounts computed against a partial basis. One instance of this was an employer contribution total-compensation category that was not picking up base salary - the same failure stated differently, since base salary is the most significant component of that basis.

Getting a deduction or contribution basis wrong does not raise an error. It produces a **plausible number that is too small**, applied to real employee deductions and employer contributions. This is money, and the defect is silent.

The pattern to name: when the same "incomplete basis" symptom appears across three item types, the fix is not three patches to three lookups. It is completing the basis resolution once, consistently.

---

## 5. W-4 election data

A thread that runs through both years. Three resolved items in 2025.

One defect was the most interesting of the three: contractors were being pulled into W-4 election data **by the incremental load path specifically**, not the full load. A defect that appears on the incremental path but not the full load means the two paths disagree about what qualifies for inclusion - the incremental filter was not enforcing the same population rule. That class of bug is dangerous because a full reload appears to fix it and hides the real cause.

A separate item required changing a join so one client's full load worked correctly. A third was a MERGE failure on a W-4 election dimension for another client - the duplicate-source-row case where MERGE cannot resolve which update wins.

This is W-4 tax withholding data, so the correctness bar is regulatory. The thread continues into 2026 with two composite-field defects (Section 13).

---

## 6. Time punches and time allocation

Three resolved items plus a schema-evolution enhancement delivered through a release cycle.

One was a textbook referential integrity failure: a time-punch fact table carrying a dimension key that did not exist in the corresponding dimension - an orphaned foreign key. Any join to that dimension either silently drops those punches or, with an inner join, makes them vanish from reports entirely while the rows still sit in the fact table. Fixing it meant both repairing the data and closing the path that allowed an unmatched key to be written.

A second client was missing an entire day of punch information from a time allocation fact table. A third item and a related enhancement were schema evolution on the time punch type dimension, delivered through a scheduled release.

---

## 7. Statistics and reporting facts

Three resolved items, all sharing one shape.

Job and classification attributes were not carrying into a statistics fact table. Login activity was missing from a separate statistics fact outright. A third was a client-specific reporting defect.

All three share a shape: **rows or attributes that should be present and are not.** Missing data is harder to catch than wrong data because nothing looks anomalous - the report renders cleanly and simply under-reports.

---

## 8. Employee action notices, benefits, performance, and routing

Six resolved items, including a second production hotfix.

One was a hotfix on a schema mismatch: a text column's length differed between the source table and its warehouse dimension. Length mismatches truncate silently on load, so values arrive shortened with no error raised.

Two items share the same defect class: **a status value not interpreted correctly.** An employee action notice showing one workflow status when it should have shown another, and a performance-goals dimension not recognizing a specific status code. In both cases the status domain in the warehouse was incomplete relative to the source - an unmapped status either falls through to a default or fails to match at all. Workflow status drives what users act on, so a wrong status is operational, not cosmetic.

A separate MERGE failure hit an authoring dimension for one client - the same duplicate-source-key pattern that recurred twice more across the two years. Three MERGE failures across two years, one underlying cause.

The remaining two items were missing benefits-enrollment updates and a workflow routing defect affecting some records.

---

## 9. Building a data validation framework

**This is the most strategically important work in the 2025 record**, and it is easy to overlook because it carries no dramatic defect title.

Every other item in Part I is a defect found because a client reported it. This workstream is the answer to the obvious question: *why are we always finding out from the client?*

Built as a **control-table-driven** framework, meaning validation rules are configuration rather than hardcoded scripts. New checks are added as rows, not code changes. That is the same architectural idea behind modern data quality tooling - declarative, metadata-driven assertions running as part of the pipeline instead of ad hoc queries someone remembers to run.

Deploying it also crossed a team boundary: getting it running on a shared test environment required resolving security and connectivity issues directly with the infrastructure team.

**Why this matters for how the year reads:** in 2025 this engineer moved from fixing defects one at a time to building the system that finds them. That is the transition from engineer to platform engineer, and it happened before the 2026 platform work.

---

## 10. Platform, infrastructure, and release process (2025)

Alongside the defect resolution work, five infrastructure and reliability workstreams:

**A CDC schema-change deployment process** - researched, tested, and documented. Schema evolution on a CDC source is one of the genuinely hard problems in data engineering: the capture mechanism is bound to a table definition, so a column change can break capture, silently drop the new column, or require rebuilding the capture instance and reconciling the gap. Working out a safe process, testing it, and **documenting it for the team** is senior work. It is also the direct groundwork for the 2026 CDC incremental reengineering.

**A production server crash root cause analysis** on the reporting server. Not "restarted the server" - root cause analysis on a crash. Production incident ownership.

**A storage optimization** reclaiming space on a version-control-adjacent database.

**Release-branch management** for the reporting server's release process.

**Schema foundation work** for a new expense-reporting subject area: table additions, schema changes, and constraints scripted out ahead of the reporting build that continued into 2026.

---

## 11. Release cycles supported (2025)

Eight release cycles, including platform-specific releases and a regulatory compliance enhancement.

One cycle in late 2025 carried **SECURE 2.0 compliance support and a time-tracking enhancement** together. SECURE 2.0 is US retirement legislation with provisions phasing in across multiple years. Supporting it in a payroll platform is **regulatory compliance delivery against a legislated deadline** - the date does not move, and getting it wrong has consequences beyond a bug report.

---

# Part II: 2026 year to date

The center of gravity shifts. Fewer "why is this row wrong" tickets, more "why does this class of row go wrong" and more platform ownership.

## 12. Paid-leave accrual

Eight items, four client organizations, one root cause - seven resolved, one still open. The clearest example of fixing the model instead of the row.

Four clients reported four different-looking problems: stale balances, a wrong accrual rate, rates rendering as a floating-point artifact and rates appearing against ineligible plans, and missing employees from an accrual summary. Separately, a related fact table was stamping every row with a fabricated approval date - the SQL Server zero-date sentinel value - and carrying an incorrect approval flag.

Lined up together they pointed at one design choice: **accrual rate was derived inline during the load rather than sourced from a modeled, plan-aware definition.** Logic derived in flight drifts across tenants, loses precision, and has nowhere to enforce eligibility.

The fix was structural:

1. Added a dedicated, versioned paid-leave accrual table, making rate and plan configuration a stored asset instead of inline logic.
2. Raised a formal change request for the rate calculation so corrected logic shipped once, reviewed, to every affected client.
3. Enforced plan eligibility, corrected numeric precision, restored employee coverage, and fixed the refresh path across the four reported symptoms.
4. The approval-flag and fabricated-date defect is **still open, actively being diagnosed** as of the most recent update - not yet resolved. The latest lead points to missing rows in a time-clock link table feeding the approval join. Do not describe this one as fixed.

Note the continuity: a 2025 defect had accrued hours displaying incorrectly for a terminated employee with a cleared balance. The accrual surface had been producing defects for over a year, and part of it is still being worked as of this writing.

**Why it matters:** paid-leave balance is not a dashboard number. Employees plan against it, managers approve against it, and at termination it converts to money.

---

## 13. Payroll, vouchers, and contributions (2026)

Seven resolved items.

**Voucher integrity.** Failures in both directions across two different clients: one had a voucher duplicated, another had vouchers missing entirely from a demographics-linked fact table. Duplication and omission in one domain usually share a root - when declared grain and real grain disagree, one join path fans out while another filters out. This is the same voucher surface that produced two duplication defects and a hotfix in 2025.

A third voucher item - reissued vouchers missing for a client - was triaged and handed to a colleague. Voucher reissue is a distinct upstream event lifecycle and belonged with the owner of that path. Recorded as handed off, not closed.

**Composite fields.** Two items, one violation: **one attribute per column.** A state filing-status code packed in with an allowances numeric field; a separate election-status code packed inside another allowances value. Any consumer treating allowances as purely numeric read a contaminated value - in tax withholding input data.

**Reporting enhancement.** A new adjustment column added to a recurring-payroll reporting object so a match adjustment reaches downstream reporting.

---

## 14. Performance review reporting

Four resolved items.

Failing in both directions at once - extra rows for one client, missing data for others - which means **the warehouse's row-selection logic and the application's had diverged.**

Rather than tuning predicates until one client's counts looked right, the application's actual row-selection logic was reimplemented directly in the load. That makes the warehouse agree with the product by construction, for every client. The extra-rows symptom resolved as a consequence. A maintenance package then backfilled clients whose history was already wrong.

Continuity: a 2025 defect in this same subject area was a performance-goals dimension not recognizing a specific status code - the same class of incomplete domain handling.

*(See Section 15 for an attribution correction on this workstream - the described role is escalation and specification, not sole implementation.)*

---

## 15. New subject areas and dimension corrections (2026)

Two resolved dimension-correctness items plus two greenfield builds.

One was a hard MERGE failure - the load stops until fixed. The third such failure across the two years, following the two described in Sections 4 and 8.

A second was a slowly changing dimension (SCD Type 2) correctness defect: wrong effective end dates meant validity intervals overlapped or gapped, so **every point-in-time query returned two answers or none.**

Two greenfield builds: a new compliance-relevant dimensional model built from scratch - grain definition, conformed dimensions, integration into the existing warehouse and release process - and reporting support for the new expense subject area whose schema foundation was scripted in 2025.

---

## 16. Time allocation (2026)

One resolved item affecting a single client.

Duplicate rows in a time-allocation fact table were inflating charged hours against projects and cost centers - a cost-accounting problem. Two-part fix: corrected the load, then built a maintenance job to clean records already in the table, shipped as a **limited maintenance package scoped to the one affected client** so it did not wait on a full release or touch clients that did not need it.

Continuity: a 2025 defect in the same fact table was a different client missing an entire day of punch information.

---

## 17. Platform, DevOps, and reliability (2026)

Five workstreams, the largest concentration of infrastructure ownership in the record.

**Automated database provisioning.** Client database refreshes for support and bug reproduction run 20+ times daily. On a clustered, Always-On Availability Group SQL Server environment, this means removing the database from the cluster, restoring it, reconciling security and CDC replication state, and validating cluster listener health - every step manual, on a payroll-critical cluster. Built as a one-click **idempotent** pipeline with a guard that blocks execution against a live production server, rerunnable on failure, and logging detailed enough to diagnose partial failures without a DBA handoff. Validated against a newer SQL Server version on a dedicated test environment ahead of a client migration, then moved onto the standard CI/CD platform so the tool ships through the same governed path as everything else.

**A release-blocking build failure.** Reporting databases could not be built from a specific release branch - a release-blocking failure traced to a pipeline configuration gap that never made it onto that branch.

**A production CDC incremental failure.** The highest-stakes failure mode: when incremental breaks, the options are a slow full reload or stale client data. Restored on the fast path rather than degraded to full reload, for the same client whose custom reporting showed inconsistent payroll amounts in 2025.

**Concurrency defects.** Deadlocks on client database stored procedures - load-dependent, intermittent, passes every test then fails under real concurrency.

---

## 18. Release cycles and CI/CD ownership (2026)

Two data-engineering sprint cycles delivered under a rebuilt release process.

Owning CI/CD end to end through the organization's DevOps platform compressed the deployment cycle from **3 months to 14 days**, removing roughly 11 weeks of cross-team idle time per release.

This is the enabler for everything else in Part II. Under a 3-month cycle, a structural fix like the paid-leave accrual change request is a two-quarter bet and nobody approves it. **A 14-day cycle is what makes root-cause fixes rational instead of reckless.**

---

# Part III: Patterns

## 19. Threads that span both years

Reading the years together surfaces continuity neither shows alone. In every case the 2025 work was symptomatic and the 2026 work was structural.

| Subject area | 2025 | 2026 | Progression |
|---|---|---|---|
| **Paid-leave accrual** | One defect | An eight-item cluster across four clients | Single defect -> modeled accrual table |
| **W-4 elections** | Load and join fixes | Composite-field decomposition | Population-rule fixes -> field decomposition |
| **Vouchers** | Duplication, plus a hotfix | Grain-integrity fixes across two clients | Duplication hotfixes -> grain integrity |
| **Time allocation** | Missing punches, schema evolution | Grain fix plus backfill | Missing punches -> grain fix plus backfill |
| **Performance reporting** | Status-domain gap | Application-logic alignment | Status domain -> application logic alignment |
| **MERGE failures** | Two instances | One instance | Three instances, one root cause |
| **One client's reporting** | Reporting inconsistency defects | Production CDC incident ownership | Reporting defects -> pipeline ownership |
| **New subject area (expenses)** | Schema foundation scripted | Reporting delivered | Schema foundation -> reporting delivery |
| **CDC** | Schema-change process researched and documented | Incremental reengineering, 30 min -> 8 min | Groundwork -> architectural rebuild |

The CDC row is the clearest: the 2025 research and documentation is why the 2026 reengineering was possible.

---

## 20. The recurring defect classes

Six classes account for most of the 53 work items. Naming them is what turns a long defect list into a much shorter list of real fixes.

### 1. Sentinel and default values escaping into business data
A fabricated zero-date sentinel value standing in for a real approval date, and a floating-point display artifact standing in for a clean accrual rate. A technical default or float artifact reaching a user as though it were a real business value. Nothing errors; the value is simply fiction. The fix is making absence representable - NULL where nothing happened, correct precision where a value exists.

### 2. Grain violations
Duplicate rows across multiple payroll and time-allocation fact tables, plus three separate MERGE failures where declared grain and real grain disagreed. All one question: **what uniquely identifies a row here?** Where the two disagreed, joins fanned out and MERGE could not resolve a target.

### 3. Missing filters, joins, and absent rows
Rates missing for ineligible plans, missing employees, missing vouchers, missing login activity, missing job fields, missing benefits updates, missing punches, missing review data. The mirror image of grain violations. **Harder to catch, because a report that under-reports still renders cleanly.**

### 4. Composite fields
A filing-status code packed with a numeric allowances field, and an election-status code packed inside another allowances value. One attribute per column. Any numeric consumer read a corrupted value - in tax withholding data.

### 5. Incomplete domain and basis coverage
An unrecognized workflow status code, a misinterpreted approval status, and the basis-resolution cluster across three recurring item types. The warehouse's set of valid values was narrower than the source's. Unmapped values fall through to a default or fail to match, producing plausible wrong answers rather than errors.

### 6. Full load and incremental path divergence
Contractors entering W-4 data on the incremental path only, a join fix needed for one client's full load, and a production CDC incremental failure. **When the two paths disagree about population, a full reload appears to fix the problem and hides the cause.**

### The through-line: fix the model, not the row

The strongest example is the paid-leave accrual cluster - four clients, four differently-worded symptoms, one design flaw, closed structurally with a modeled accrual table and a single reviewed change request. The same instinct drove reimplementing the application's real row-selection logic rather than tuning predicates, and building a validation framework rather than waiting for the next client report.

---

## 21. Status and honest accounting

- One voucher-reissue item was **triaged and handed off** - it belonged with the owner of the upstream reissue lifecycle, not this role.
- One allocation-description defect had its root cause in the upstream operational data store; the **data fix was sent back to testing** rather than patched in the warehouse.
- One employer-contribution-code item was code complete in 2025 and released in 2026, counted once.
- One paid-leave item (the approval-flag/fabricated-date defect, Section 12) is **still open**, actively being diagnosed - not resolved. Of the 53 total work items, 52 are resolved.
- All other resolved items were delivered through the release cycles described in Sections 11 and 18.

Where this document states a root cause, it describes the defect class the work item represents. The platform metrics quoted (3 months to 14 days, 30 min to under 8 min, -67% compute, ~1 hour per provisioning request, 20+ daily requests) are the established measured figures.

---

## 22. Corrections and additions (August 2026)

A round of accuracy corrections and one new addition, made after further review. Accuracy matters more than a clean narrative, including where that means walking back an earlier claim.

### Confirmed tenure

Tenure begins **July 2024**, about five months earlier than the "2025 full year" framing in this document implies. Mid-to-late 2024 was mostly onboarding, so the two-year arc in Section 2 remains the right frame for a resume or interview - but the underlying tenure is Jul 2024 to present, not Jan 2025 to present.

### Correction: performance review reporting (Section 14)

Section 14 described this as reimplementing the web application's row-selection logic directly in the ETL load. That is not fully accurate. The correct story is narrower, and arguably a better signal: a warehouse-side symptom for one client was traced back to an application-level data model gap, and **a separate cross-team item was raised and driven to get the product team to address the root cause**, rather than only patching the ETL. Corrected in the story bank.

### Correction: the paid-leave approval-flag defect is not closed

This was described as resolved in Section 12. It is **still open**, actively being diagnosed. Treat as in-progress, not fixed, anywhere it is used.

### Correction: attribution across the paid-leave accrual cluster (Section 12)

The four-client cluster is not uniformly this engineer's direct hands-on work:

- One client's wrong-accrual-rate item - fully confirmed, direct SQL diagnostic work. The strongest item in the cluster.
- The non-eligible-plans item - the eligibility-flag design is a joint contribution, credited to this engineer alongside a teammate.
- The floating-point-display item - weaker, indirect evidence; described accordingly.
- The stale-records item and the missing-employees item - no confirmed involvement; cannot be attributed to this engineer.

The framing that survives: this engineer owned and specified the structural fix (the accrual table and its rollout) that the cluster's resolution depended on - not a claim of personally closing all four items.

### Correction: the release-blocking build failure (Section 17)

The confirmed root cause is a pipeline configuration file that never made it onto the release branch - not specifically an "agent naming" issue as earlier phrasing suggested. A claim that the fix spanned multiple repositories is unconfirmed and should not be asserted as fact. The core fact stands: a pipeline configuration gap on the release branch blocked reporting database builds.

### Upgraded and fully confirmed: automated database provisioning (Section 17)

The most fully confirmed item in this record, with a real engineering changelog for the 2026 enhancement:

- Rewrote CDC job cleanup to actually delete the underlying SQL Server Agent capture and cleanup jobs, rather than only clearing job tracking metadata - a real bug where the metadata looked clean while the underlying scheduled jobs kept running.
- Added an existence and CDC-enabled guard before disabling CDC on a database, including terminating any active replication command session first.
- Added restore-procedure parameters that had been silently defaulting.
- Added detection and forced recovery for databases stuck mid-restore.
- Added pre-flight existence checks so an in-progress drop cannot race a new provisioning request.

Materially stronger and more specific than the earlier general description. Use this version everywhere the workstream is discussed - it has been updated in the story bank and the STAR impact points.

### New: proactive pipeline monitoring and self-healing incremental jobs

Not previously documented. This engineer identified that the incremental ETL pipeline (daily client jobs, running overnight) had no failure-detection layer, and named three distinct, previously uncovered failure modes:

1. **Missed run** - the scheduled job never fired, and nobody was notified.
2. **Stuck run** - a long-running query or lock contention held the job open past its window, blocking the next cycle.
3. **Silent failure** - the job crashed without logging an end time, so a simple "did it run today" check would misclassify it as still running.

The real risk this closes: CDC change logs have a retention window, so a gap discovered hours or days later can already be unrecoverable by the time anyone notices manually. A strong, resume-ready reliability engineering story, added to the story bank as a new Tier 1 entry.
