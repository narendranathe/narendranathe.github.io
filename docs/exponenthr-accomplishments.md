# ExponentHR Data Engineering: Delivery Record

**Engineer:** Narendranath Edara
**Role:** Data Engineer - Data Warehouse, CDC ETL, Reporting Platform
**Organization:** ExponentHR, Addison, TX
**Coverage:** 2025 full year and 2026 year to date (as of August 2026)
**System of record:** Azure DevOps work items and sprint boards

**Companion documents:**
- [`exponenthr-work-item-stories.md`](./exponenthr-work-item-stories.md) - interview-ready STAR stories
- [`career-positioning-2026.md`](./career-positioning-2026.md) - market positioning built on this record

---

## 1. Executive summary

ExponentHR runs payroll, benefits, and time-off for thousands of employers. Every figure reaching a client report, a paycheck reconciliation, or a compliance filing passes through the reporting warehouse.

Two years of work with a clear shape:

**2025 was the correctness year.** 29 work items across the full warehouse surface - vouchers, allocations, deduction and contribution basis logic, W-4 elections, time punches, benefits enrollment, performance goals, employee action notices. Production hotfixes, server crash root cause analysis, and release support across 8 cycles. This is also the year I built the **Data Checker** validation framework and researched, tested, and documented the **CDC schema change deployment process** the team now follows.

**2026 is the platform year.** 25 work items, but the center of gravity moved from fixing data to owning the machinery: CI/CD end to end, CDC reengineered from full reloads to incremental merge-upserts, the contained AAG Copy Down tool automated, and new dimensional models designed from scratch.

**The second year was earned by the first.** Deep familiarity with every failure mode in the warehouse is what made it credible to then rebuild the pipelines and release process around it.

### At a glance

| Measure | 2025 | 2026 YTD | Total |
|---|---|---|---|
| Numbered work items | 29 | 25 | **53 unique** |
| Unticketed workstreams | 6 | 5 | 11 |
| Release and sprint cycles | 8 | 2 | **10** |
| Distinct client tenants served | 6 | 11 | **16 unique** |
| Production hotfixes | 2 | - | 2 |
| New frameworks or subject areas built | 2 | 2 | 4 |

One item, **13803**, spans both years: code complete in 2025, released in 2026. It is counted once.

### Platform metrics

| Metric | Result |
|---|---|
| Release cycle | 3 months -> 14 days (~11 weeks idle time removed per release) |
| CDC ETL runtime | 30 min -> under 8 min |
| CDC compute cost | -67% |
| AAG copy-down effort | ~1 hour manual orchestration removed per request, 20+ requests/day |

### Client tenants (16)

`00169`, `00194`, `00336`, `00479`, `00612`, `00630`, `00704`, `00745`, `00747`, `00810`, `00877`, `00972`, `00979`, `00982`, `00994`, `10106`

---

## 2. The two-year arc

The most useful way to read this record is as a progression, not two separate years.

| | 2025 | 2026 |
|---|---|---|
| **Center of gravity** | Data correctness across the warehouse | Platform and pipeline ownership |
| **Typical item** | A client-reported defect in a fact or dimension | A pipeline, release, or model design change |
| **Mode** | Reactive plus systematic - fix, then find the class | Proactive - rebuild the machinery |
| **Signature deliverable** | Data Checker validation framework | CI/CD ownership and CDC incrementalization |
| **What it built** | Complete knowledge of every failure mode | The ability to fix the class, not the instance |

Two 2025 workstreams are the hinge between the years:

1. **Data Checker with control table** - a metadata-driven validation framework. The move from finding defects by client report to catching them systematically.
2. **CDC schema change deployment process** - researched, tested, and documented. The groundwork the 2026 CDC incremental reengineering was built on.

Neither was a ticket handed down. Both are the kind of work an engineer takes on after seeing enough failures to know what is missing.

---

# Part I: 2025

## 3. Payroll, vouchers, and allocations

| Item | Client | Title |
|---|---|---|
| 16552 | - | DW not displaying correct result in [Voucher Code Short Desc] |
| 16518 | - | Incorrect Allocation Description for PIECEWORK allocation type (ODS data fix) |
| 16421 | - | DW duplicating results for Misc. Adjustment Allocation |
| 28168 | - | Duplication in Fact_PayVoucherAllocation |
| 29885 | - | **Hotfix:** Fact_PayVoucherDetail replicating 09/05/25 payroll data |
| 31617 | 00630 | Custom Reporting showing inconsistent payroll amounts |

The voucher and allocation surface produced defects in every direction.

**Duplication (16421, 28168, 29885).** Three separate duplication defects in pay allocations and voucher detail. `29885` was a **production hotfix**: `Fact_PayVoucherDetail` was replicating the 09/05/25 payroll run. Duplicated payroll data is about as urgent as reporting defects get, and it shipped outside the normal release cycle.

**Incorrect attribute resolution (16552, 16518).** Voucher code short description and PIECEWORK allocation description were both resolving wrong. `16518` traced back to ODS and was fixed at the source rather than patched in the warehouse - the right call, and it went back through testing accordingly.

**Inconsistent totals (31617).** Client 00630's custom reporting showed payroll amounts that did not agree. Inconsistency across reports usually means two paths computing the same figure differently, which is a modeling problem rather than an arithmetic one.

---

## 4. Deduction, earning, and contribution basis logic

The most coherent defect cluster of 2025, and the clearest example of a shared root cause surfacing as separate tickets.

| Item | Title |
|---|---|
| 14020 | [ER Contrib Total Comp Category] not getting Base Salary |
| 14030 | [Deduction Rec Item Based On] may not have all basis |
| 16069 | DW incorrect result for [Earning Rec Item Based On] |
| 31483 | [ER Rec Item Based On] may not have all basis |
| 13803 | Incorrect ER contribution code used (code complete 2025, released 2026) |

Four items, three recurring item types - deductions, earnings, employer contributions - and one shared symptom: **the basis resolution was incomplete.** The set of values a recurring item could be calculated against did not cover every valid case, so amounts computed against a partial basis.

`14020` is the same failure stated differently: the employer contribution total compensation category was not picking up base salary, meaning the basis was missing its most significant component.

Getting a deduction or contribution basis wrong does not raise an error. It produces a **plausible number that is too small**, applied to real employee deductions and employer contributions. This is money, and the defect is silent.

The pattern to name: when the same "may not have all basis" phrasing appears across three item types, the fix is not three patches to three lookups. It is completing the basis resolution once, consistently.

---

## 5. W-4 election data

A thread that runs through both years.

| Item | Client | Title |
|---|---|---|
| 27638 | 00704 | Change join in Fact_EmpW4Elections to support full load |
| 16462 | - | Incrementals adding contractors into Dim/Fact_W4ElectionData |
| 31313 | 00630 | Merge issue on Dim_EmpW4Election |

**16462 is the most interesting of the three.** Contractors were being pulled into W-4 election data **by the incremental load specifically.** A defect that appears on the incremental path but not the full load means the two paths disagree about what qualifies for inclusion - the incremental filter was not enforcing the same population rule. That class of bug is dangerous because a full reload appears to fix it and hides the real cause.

**27638** required changing the join in `Fact_EmpW4Elections` so client 00704's full load worked correctly. **31313** was a MERGE failure on `Dim_EmpW4Election` for client 630 - the duplicate-source-row case where MERGE cannot resolve which update wins.

This is W-4 tax withholding data, so the correctness bar is regulatory. The thread continues in 2026 with `14825` and `34366`.

---

## 6. Time punches and time allocation

| Item | Client | Title |
|---|---|---|
| 29973 | - | Fact_TimePunches has unrecognized Dim_TimeSourceID not present in Dim_TimeSource |
| 31616 | 00979 | Fact_TimeAllocation missing punch information for 11/10/2025 |
| 32319 | - | Script for schema changes on Dim_TimePunchType |
| - | - | Clock Out Type enhancement (Sprint 2025.12.15) |

**29973 is a textbook referential integrity failure.** A fact table carrying a dimension key that does not exist in the dimension - an orphaned foreign key. Any join to `Dim_TimeSource` either silently drops those punches or, with an inner join, makes them vanish from reports entirely while the rows still sit in the fact table. Fixing it means both repairing the data and closing the path that allowed an unmatched key to be written.

**31616** had client 00979 missing an entire day of punch information. **32319** and the Clock Out Type enhancement were schema evolution on the time punch dimension, delivered through the 2025.12.15 release.

---

## 7. Statistics and reporting facts

| Item | Client | Title |
|---|---|---|
| 14778 | - | Fact_StatsReports not reflecting Job/Classification fields |
| 25661 | - | Fact_StatsLogon missing login activity |
| 28947 | 00972 | Weekly Store Report |

`14778` had job and classification attributes not carrying into the statistics fact. `25661` had login activity missing from `Fact_StatsLogon` outright. `28947` was a client-specific reporting defect for 00972.

All three share a shape: **rows or attributes that should be present and are not.** Missing data is harder to catch than wrong data because nothing looks anomalous - the report renders cleanly and simply under-reports.

---

## 8. Employee Action Notices, benefits, performance, and routing

| Item | Client | Title |
|---|---|---|
| 30559 | - | **Hotfix:** EAN Field column length mismatch between base table and Dim_EAN |
| 30856 | 00479 | EAN 269367 showing Approved when it should be Completed |
| 30497 | - | Fact_BenEnroll missing updated information |
| 16383 | - | Dim_PerformanceGoals not recognizing Status 98 |
| 16235 | - | Rerouted incorrect in some instances |
| 31622 | 00336 | Dim_Author MERGE failure, update/delete same row |

**30559 was a hotfix on a schema mismatch:** the `Field` column length differed between the base table and `Dim_EAN`. Length mismatches truncate silently on load, so values arrive shortened with no error raised.

**30856 and 16383 are the same defect class:** a status value not interpreted correctly. An EAN showing `Approved` when it should be `Completed`, and `Dim_PerformanceGoals` not recognizing `Status 98`. In both cases the status domain in the warehouse was incomplete relative to the source - an unmapped status either falls through to a default or fails to match at all. Workflow status drives what users act on, so a wrong status is operational, not cosmetic.

**31622** was a MERGE failure on `Dim_Author` for client 00336 - the same duplicate-source-key pattern as `31313` and, later, `32478`. Three MERGE failures across two years on one underlying cause.

**30497** had `Fact_BenEnroll` missing updated benefits enrollment information. **16235** was a rerouting defect affecting some instances.

---

## 9. Data Checker: a validation framework

| Workstream | Detail |
|---|---|
| Data Checker implementation with control table | Metadata-driven validation across warehouse tables |
| Data Checker on training03 | Resolved security and connection string issues with IT |

**This is the most strategically important item in the 2025 record**, and it is easy to overlook because it has no dramatic ticket title.

Every other item in Part I is a defect found because a client reported it. Data Checker is the answer to the obvious question: *why are we always finding out from the client?*

Built as a **control-table-driven** framework, meaning validation rules are configuration rather than hardcoded scripts. New checks are added as rows, not code changes. That is the same architectural idea behind modern data quality tooling - declarative, metadata-driven assertions running as part of the pipeline instead of ad hoc queries someone remembers to run.

Deploying it also crossed a team boundary: getting it running on `training03` required resolving security and connection string issues with IT.

**Why this matters for how the year reads:** in 2025 this engineer moved from fixing defects one at a time to building the system that finds them. That is the transition from engineer to platform engineer, and it happened before the 2026 platform work.

---

## 10. Platform, infrastructure, and release process (2025)

| Workstream | Detail |
|---|---|
| CDC schema change deployment process | Research, testing, and documentation |
| Server crash root cause analysis | SSRS |
| 29462 | Optimization: ShrinkDB in VC |
| SSRS release branch refresh | Branch management |
| 32344 | Scripts for Cosmos Expense table additions, schema changes, constraints |
| 32319 | Script for schema changes on Dim_TimePunchType |

**CDC schema change deployment process (research, testing, documentation).** Schema evolution on a CDC source is one of the genuinely hard problems in data engineering: the capture instance is bound to a table definition, so a column change can break capture, silently drop the new column, or require rebuilding the capture instance and reconciling the gap. Working out a safe process, testing it, and **documenting it for the team** is senior work. It is also the direct groundwork for the 2026 CDC incremental reengineering.

**Server crash root cause analysis (SSRS).** Not "restarted the server" - root cause analysis on a crash. Production incident ownership.

**29462, ShrinkDB in VC.** Storage and performance optimization.

**32344, Cosmos Expense.** Table additions, schema changes, and constraints scripted out - the schema foundation for the Cosmos Expense work that continued into 2026.

---

## 11. Release cycles supported (2025)

Eight cycles, including SSRS-specific releases and a regulatory enhancement.

| Cycle | Scope |
|---|---|
| Sprint 6.27 | Code release |
| SSRS Sprint 2025.07.28 | Code release |
| Sprint 8.15.2025 | Delivery |
| Release Sprint 8.22.2025 | Code release |
| Sprint 2025.09.15 | Delivery |
| Sprint 2025.11.07 | Code release |
| Sprint 2025.12.15 | **SECURE 2.0 and Clock Out Type enhancement** |
| Sprint 2025.12.19 | Code management and release to testing |

**Sprint 2025.12.15 deserves separate mention.** SECURE 2.0 is US retirement legislation with provisions phasing in across multiple years. Supporting it in a payroll platform is **regulatory compliance delivery against a legislated deadline** - the date does not move, and getting it wrong has consequences beyond a bug report.

---

# Part II: 2026 year to date

The center of gravity shifts. Fewer "why is this row wrong" tickets, more "why does this class of row go wrong" and more platform ownership.

## 12. PTO and time-off accrual

Eight items, four clients, one root cause. The clearest example of fixing the model instead of the row.

| Item | Client | Title |
|---|---|---|
| 27353 | - | Fact_PTODetails incorrect Approved flag, all records get Approval Date 12/31/1900 |
| 32896 | 00745 | Fact_PTOSummary records not up to date |
| 32979 | 00169 | Fact_PTOSummary showing wrong accrual rate |
| 33847 | 10106 | Some plans in Fact_PTOSummary showing 1E-05 |
| 33866 | 10106 | Accrual rate showing for non-eligible plans |
| 34021 | 00612 | Fact_PTOSummary missing employees |
| 34882 | - | Change request: Fact_PTOSummary accrual rate update |
| 28369 | - | Add table for PTO accrual information |

Four clients reported four different-looking problems: stale balances (00745), a wrong accrual rate (00169), rates rendering as `1E-05` and rates appearing against ineligible plans (10106), and missing employees (00612). Separately, `Fact_PTODetails` was stamping every row with an approval date of **12/31/1900** - the SQL Server zero-date sentinel - and carrying an incorrect approved flag.

Lined up together they pointed at one design choice: **accrual rate was derived inline during the load rather than sourced from a modeled, plan-aware definition.** Logic derived in flight drifts across tenants, loses precision, and has nowhere to enforce eligibility.

The fix was structural:

1. Added a dedicated PTO accrual table (28369), making rate and plan configuration a stored, versioned asset.
2. Raised a formal change request for the rate calculation (34882) so corrected logic shipped once, reviewed, to every tenant.
3. Enforced plan eligibility (33866), corrected numeric precision (33847), restored employee coverage (34021), fixed the refresh path (32896).
4. Corrected approval semantics in `Fact_PTODetails` (27353) so unapproved records carry NULL rather than a fabricated date.

Note the continuity: `16805` in 2025 was accrued hours displaying incorrectly for a terminated employee with a cleared balance. The accrual surface had been producing defects for over a year before it was fixed structurally.

**Why it matters:** PTO balance is not a dashboard number. Employees plan against it, managers approve against it, and at termination it converts to money.

---

## 13. Payroll, vouchers, and contributions (2026)

| Item | Client | Title |
|---|---|---|
| 32495 | 00810 | Voucher duplicated for employee in Fact_PayVoucherDetail |
| 33436 | 00810 | Reissued vouchers missing (triaged, handed off) |
| 37005 | 00982 | Dim_PayDemographics missing vouchers |
| 13803 | - | Incorrect ER contribution code used (code complete 2025) |
| 14825 | - | [W4 State Allowances] contains state filing status and allowances in one field |
| 34366 | - | Dim_W4ElectionData contains election status in allowances value |
| 36204 | - | Add MatchSH2Adj column to ssrs_UpdateRecurring |

**Voucher integrity (32495, 37005).** Failures in both directions: 00810 had a voucher duplicated, 00982 had vouchers missing. Duplication and omission in one domain usually share a root - when declared grain and real grain disagree, one join path fans out while another filters out. This is the same voucher surface that produced `16421`, `28168`, and hotfix `29885` in 2025.

**33436** was triaged and handed to a colleague. Voucher reissue is a distinct upstream event lifecycle and belonged with the owner of that path. Recorded as handed off, not closed.

**W-4 composite fields (14825, 34366).** Two items, one violation: **one attribute per column.** State filing status packed in with allowances; election status inside the allowances value. Any consumer treating allowances as numeric read a contaminated value - in tax withholding input data.

**36204** added the `MatchSH2Adj` column to `ssrs_UpdateRecurring` so the match adjustment reaches SSRS reporting.

---

## 14. Performance review reporting

| Item | Client | Title |
|---|---|---|
| 34376 | 00194 | Dim_PerformanceReviewDetails pulling extra rows |
| 36072 | - | Missing data (maintenance package) |
| 36207 | - | Missing data |
| 36904 | - | Implement web logic to avoid duplicate rows |

Failing in both directions at once - extra rows for 00194, missing data for others - which means **the warehouse's row-selection logic and the application's had diverged.**

Rather than tuning predicates until one client's counts looked right, I implemented the web application's actual selection logic in the load (36904). That makes the warehouse agree with the product by construction, for every tenant. The extra rows (34376) resolved as a consequence. A maintenance package then backfilled clients whose history was already wrong (36072, 36207).

Continuity: `16383` in 2025 was `Dim_PerformanceGoals` not recognizing Status 98 - the same subject area, the same class of incomplete domain handling.

---

## 15. Employee dimensions and new subject areas (2026)

| Item | Client | Title |
|---|---|---|
| 32478 | 00994 | Merge conflict on Dim_StatsReportType |
| 34247 | 00747 | Dim_EmpInfoHistory issue with effective end date |
| - | - | Attestations dimensional model (new build) |
| - | - | Cosmos Expense Project SSRS support |

**32478** was a hard MERGE failure - the load stops until fixed. The third such failure across the two years, after `31313` and `31622`.

**34247** is SCD Type 2 correctness. Wrong effective end dates mean validity intervals overlap or gap, so **every point-in-time query returns two answers or none.**

**Attestations** was greenfield: grain definition, conformed dimensions, integration into the existing warehouse and release process. **Cosmos Expense SSRS support** built on the 2025 schema scripting work (32344).

---

## 16. Time allocation (2026)

| Item | Client | Title |
|---|---|---|
| 35366 | 00877 | Fact_TimeAllocation duplicate rows, plus stale-record maintenance job |

Duplicates inflate charged hours against projects and cost centers - a cost-accounting problem. Two-part fix: corrected the load, then built a maintenance job to clean records already in the table, shipped as a **limited maintenance package scoped to 00877** so it did not wait on a full release or touch tenants that did not need it.

Continuity: `31616` in 2025 was the same table missing punch information for 00979.

---

## 17. Platform, DevOps, and reliability (2026)

| Item | Title |
|---|---|
| 31554 | Copy Down tool for contained AAG fix, including Env006 for SQL Server 2025 |
| - | SQL Copy Down tool enhancement |
| - | Copy Down automation YAML: deploy from Azure Pipelines |
| 36429 | Unable to create Reporting DB from release/2025.07.25; agent name update across three repos |
| - | 00630 CDC incremental failure |
| 36119 | Deadlock on client databases for stored procedures |

**Copy Down tool.** Client database refreshes run 20+ times daily. On contained Always-On Availability Groups this means removing the database from the AG, restoring, reconciling security and CDC state, and validating listener health - every step manual, on a payroll-critical cluster. Built as a one-click **idempotent** pipeline with a LIVE-server guard before restore logic, rerunnable on failure, and logging detailed enough to diagnose partial failures without a DBA handoff. Validated on **Env006 against SQL Server 2025** ahead of need, then moved onto Azure Pipelines so the tool ships through the same governed path as everything else.

**36429.** Reporting databases could not be built from `release/2025.07.25` - a release-blocking failure caused by a stale agent name in the pipeline YAML. Fixed across **all three affected repos** (Full Load, Incremental, Employer Reports), not just the one that surfaced the error.

**00630 CDC incremental failure.** The highest-stakes failure mode: when incremental breaks, the options are a slow full reload or stale client data. Restored on the fast path rather than degraded to full reload. Same client whose custom reporting showed inconsistent payroll amounts in 2025 (`31617`).

**36119.** Deadlocks on client database stored procedures - load-dependent, intermittent, passes every test then fails under real concurrency.

---

## 18. Release cycles and CI/CD ownership (2026)

| Cycle | Scope |
|---|---|
| DE Sprint 2026.03.05 | Data engineering sprint delivery |
| DE Sprint 2026.04.02 | Data engineering sprint delivery |

Owning CI/CD end to end through Azure DevOps compressed the deployment cycle from **3 months to 14 days**, removing roughly 11 weeks of cross-team idle time per release.

This is the enabler for everything else in Part II. Under a 3-month cycle, a structural fix like the accrual change request (34882) is a two-quarter bet and nobody approves it. **A 14-day cycle is what makes root-cause fixes rational instead of reckless.**

---

# Part III: Patterns

## 19. Threads that span both years

Reading the years together surfaces continuity neither shows alone. In every case the 2025 work was symptomatic and the 2026 work was structural.

| Subject area | 2025 | 2026 | Progression |
|---|---|---|---|
| **PTO accrual** | 16805 | 27353, 28369, 32896, 32979, 33847, 33866, 34021, 34882 | Single defect -> modeled accrual table |
| **W-4 elections** | 16462, 27638, 31313 | 14825, 34366 | Load and join fixes -> field decomposition |
| **Vouchers** | 16421, 28168, 29885 | 32495, 33436, 37005 | Duplication hotfixes -> grain integrity |
| **Time allocation** | 29973, 31616, 32319 | 35366 | Missing punches -> grain fix plus backfill |
| **Performance** | 16383 | 34376, 36072, 36207, 36904 | Status domain -> application logic alignment |
| **MERGE failures** | 31313, 31622 | 32478 | Three instances, one root cause |
| **Client 00630** | 31313, 31617 | CDC incremental failure | Reporting defects -> pipeline ownership |
| **Cosmos Expense** | 32344 | SSRS support | Schema foundation -> reporting delivery |
| **CDC** | Schema change process, researched and documented | Incremental reengineering, 30 min -> 8 min | Groundwork -> architectural rebuild |

The CDC row is the clearest: the 2025 research and documentation is why the 2026 reengineering was possible.

---

## 20. The recurring defect classes

Six classes account for most of 53 work items. Naming them is what turns a long ticket list into a much shorter list of real fixes.

### 1. Sentinel and default values escaping into business data
`12/31/1900` approval dates (27353) and `1E-05` accrual rates (33847). A technical default or float artifact reaching a user as though it were a real business value. Nothing errors; the value is simply fiction. The fix is making absence representable - NULL where nothing happened, correct precision where a value exists.

### 2. Grain violations
Duplicate rows in `Fact_PayVoucherDetail` (32495, 29885), `Fact_PayVoucherAllocation` (28168), Misc. Adjustment Allocation (16421), `Fact_TimeAllocation` (35366), `Dim_PerformanceReviewDetails` (34376), plus three MERGE failures (31313, 31622, 32478). All one question: **what uniquely identifies a row here?** Where declared grain and real grain disagreed, joins fanned out and MERGE could not resolve a target.

### 3. Missing filters, joins, and absent rows
Rates on ineligible plans (33866), missing employees (34021), missing vouchers (37005), missing login activity (25661), missing job fields (14778), missing benefits updates (30497), missing punches (31616), missing review data (36207, 36072). The mirror image of grain violations. **Harder to catch, because a report that under-reports still renders cleanly.**

### 4. Composite fields
Filing status packed with allowances (14825), election status inside allowances (34366). One attribute per column. Any numeric consumer read a corrupted value - in tax withholding data.

### 5. Incomplete domain and basis coverage
`Status 98` unrecognized (16383), EAN status wrong (30856), and the basis cluster (14020, 14030, 16069, 31483). The warehouse's set of valid values was narrower than the source's. Unmapped values fall through to a default or fail to match, producing plausible wrong answers rather than errors.

### 6. Full load and incremental path divergence
Contractors entering W-4 data on the incremental path only (16462), the join change needed for 00704's full load (27638), the 00630 CDC incremental failure. **When the two paths disagree about population, a full reload appears to fix the problem and hides the cause.**

### The through-line: fix the model, not the row

The strongest example is PTO accrual - four clients, four differently-worded tickets, one design flaw, closed structurally with a modeled accrual table and a single reviewed change request. The same instinct drove implementing the application's real logic rather than tuning predicates (36904), fixing all three repos rather than the one that failed (36429), and building Data Checker rather than waiting for the next client report.

---

## 21. Status and honest accounting

| Item | Status |
|---|---|
| 33436 - 00810 reissued vouchers missing | **Triaged and handed off.** Belonged with the owner of the upstream reissue lifecycle. |
| 16518 - PIECEWORK allocation description | Root cause in ODS; **data fix sent back to testing** rather than patched in the warehouse. |
| 13803 - Incorrect ER contribution code | Code complete 2025, released 2026. Counted once. |
| All other numbered items | Delivered through the release cycles in Sections 11 and 18. |

Where this document states a root cause, it describes the defect class the work item represents. Per-item specifics live in Azure DevOps. The platform metrics quoted (3 months to 14 days, 30 min to under 8 min, -67% compute, ~1 hour per copy-down, 20+ daily requests) are the established measured figures.

---

## 22. Appendix: complete work item index

### 2025 (29 items)

| ID | Client | Title | Theme |
|---|---|---|---|
| 13803 | - | Incorrect ER contribution code used (released 2026) | Basis logic |
| 14020 | - | [ER Contrib Total Comp Category] not getting Base Salary | Basis logic |
| 14030 | - | [Deduction Rec Item Based On] may not have all basis | Basis logic |
| 14778 | - | Fact_StatsReports not reflecting Job/Classification fields | Stats |
| 16069 | - | DW incorrect result for [Earning Rec Item Based On] | Basis logic |
| 16235 | - | Rerouted incorrect in some instances | Workflow |
| 16383 | - | Dim_PerformanceGoals not recognizing Status 98 | Performance |
| 16421 | - | DW duplicating results for Misc. Adjustment Allocation | Payroll |
| 16462 | - | Incrementals adding contractors into Dim/Fact_W4ElectionData | W-4 |
| 16518 | - | Incorrect Allocation Description for PIECEWORK (ODS fix) | Payroll |
| 16552 | - | Incorrect result in [Voucher Code Short Desc] | Payroll |
| 16805 | - | Hours accrued for terminated employee / balance cleared | PTO |
| 25661 | - | Fact_StatsLogon missing login activity | Stats |
| 27638 | 00704 | Change join in Fact_EmpW4Elections to support full load | W-4 |
| 28168 | - | Duplication in Fact_PayVoucherAllocation | Payroll |
| 28947 | 00972 | Weekly Store Report | Stats |
| 29462 | - | Optimization: ShrinkDB in VC | Platform |
| 29885 | - | **Hotfix:** Fact_PayVoucherDetail replicating 09/05/25 payroll | Payroll |
| 29973 | - | Fact_TimePunches unrecognized Dim_TimeSourceID | Time |
| 30497 | - | Fact_BenEnroll missing updated information | Benefits |
| 30559 | - | **Hotfix:** EAN Field column length mismatch | EAN |
| 30856 | 00479 | EAN 269367 showing Approved instead of Completed | EAN |
| 31313 | 00630 | Merge issue on Dim_EmpW4Election | W-4 |
| 31483 | - | [ER Rec Item Based On] may not have all basis | Basis logic |
| 31616 | 00979 | Fact_TimeAllocation missing punch information 11/10/2025 | Time |
| 31617 | 00630 | Custom Reporting showing inconsistent payroll amounts | Payroll |
| 31622 | 00336 | Dim_Author MERGE failure, update/delete same row | Dimensions |
| 32319 | - | Script for schema changes on Dim_TimePunchType | Platform |
| 32344 | - | Scripts for Cosmos Expense tables, schema, constraints | Platform |

**2025 unticketed workstreams:** Data Checker implementation with control table; Data Checker security and connection string resolution on training03; CDC schema change deployment process research, testing, documentation; SSRS server crash root cause analysis; SSRS release branch refresh; SECURE 2.0 and Clock Out Type enhancement.

### 2026 year to date (25 items, 24 new)

| ID | Client | Title | Theme |
|---|---|---|---|
| 14825 | - | [W4 State Allowances] contains filing status and allowances | Payroll |
| 27353 | - | Fact_PTODetails incorrect Approved, Approval Date 12/31/1900 | PTO |
| 28369 | - | Add table for PTO accrual information | PTO |
| 31554 | - | Copy Down tool for contained AAG fix (Env006, SQL Server 2025) | Platform |
| 32478 | 00994 | Merge conflict on Dim_StatsReportType | Dimensions |
| 32495 | 00810 | Voucher duplicated in Fact_PayVoucherDetail | Payroll |
| 32896 | 00745 | Fact_PTOSummary records not up to date | PTO |
| 32979 | 00169 | Fact_PTOSummary showing wrong accrual rate | PTO |
| 33436 | 00810 | Reissued vouchers missing (handed off) | Payroll |
| 33847 | 10106 | Some plans in Fact_PTOSummary showing 1E-05 | PTO |
| 33866 | 10106 | Accrual rate showing for non-eligible plans | PTO |
| 34021 | 00612 | Fact_PTOSummary missing employees | PTO |
| 34247 | 00747 | Dim_EmpInfoHistory effective end date | Dimensions |
| 34366 | - | Dim_W4ElectionData contains election status in allowances | Payroll |
| 34376 | 00194 | Dim_PerformanceReviewDetails pulling extra rows | Performance |
| 34882 | - | Change request: Fact_PTOSummary accrual rate update | PTO |
| 35366 | 00877 | Fact_TimeAllocation duplicate rows plus maintenance job | Time |
| 36072 | - | Dim_PerformanceReviewDetails missing data (maintenance pkg) | Performance |
| 36119 | - | Deadlock on client databases for stored procedures | Platform |
| 36204 | - | Add MatchSH2Adj column to ssrs_UpdateRecurring | Payroll |
| 36207 | - | Dim_PerformanceReviewDetails missing data | Performance |
| 36429 | - | Reporting DB build failure; agent name update across 3 repos | Platform |
| 36904 | - | Implement web logic for Dim_PerformanceReviewDetails | Performance |
| 37005 | 00982 | Dim_PayDemographics missing vouchers | Payroll |

**2026 unticketed workstreams:** SQL Copy Down tool enhancement; Copy Down automation YAML to deploy from Azure Pipelines; 00630 CDC incremental failure; Attestations dimensional model; Cosmos Expense Project SSRS support.

---

## 23. Appendix: pulling the real work item data

This record was written from work item titles and client numbers, not fetched from Azure DevOps. To verify root causes and recover specifics, connect the work item API.

### Which server you need

**Not** the Azure MCP Server (`@azure/mcp`, sometimes called `Azure.Mcp.Server`). That covers Azure **resources** - Storage, Cosmos DB, Kusto, Monitor, SQL, AKS, Key Vault - and its "DevOps" section is Bicep, Terraform, Deploy, and Workbooks. It has **no work item tools**.

Work items live in the **separate Azure DevOps MCP Server** (`@azure-devops/mcp`, repository `microsoft/azure-devops-mcp`), which exposes the `wit_*` toolset: `wit_my_work_items`, `wit_get_work_items_batch_by_ids`, plus `repos`, `wiki`, and `build`.

### Local, not remote

Microsoft hosts a remote endpoint at `https://mcp.dev.azure.com/{organization}`, but per Microsoft's documentation it authenticates via Microsoft Entra ID and **Claude Code, Claude Desktop, Cursor, and Codex cannot currently authenticate to it.** Use the local server with a PAT. Requires Node.js 20+.

```jsonc
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "<your-org-name>"],
      "env": { "ADO_PAT": "<personal-access-token>" }
    }
  }
}
```

A read-only PAT scoped to **Work Items (Read)** is sufficient.

### What to pull

All 53 IDs, batch-fetched:

```
2025: 13803, 14020, 14030, 14778, 16069, 16235, 16383, 16421, 16462,
      16518, 16552, 16805, 25661, 27638, 28168, 28947, 29462, 29885,
      29973, 30497, 30559, 30856, 31313, 31483, 31616, 31617, 31622,
      32319, 32344

2026: 14825, 27353, 28369, 31554, 32478, 32495, 32896, 32979, 33436,
      33847, 33866, 34021, 34247, 34366, 34376, 34882, 35366, 36072,
      36119, 36204, 36207, 36429, 36904, 37005
```

Fields worth recovering: **repro steps and resolution notes** (actual root cause), **linked commits or pull requests** (what shipped), **created and closed dates** (cycle time), and **discussion comments** (where the diagnosis lives).

### Sources

- [Enable AI assistance with Azure DevOps MCP Server](https://learn.microsoft.com/azure/devops/mcp-server/mcp-server-overview?view=azure-devops)
- [Set up the remote Azure DevOps MCP Server](https://learn.microsoft.com/azure/devops/mcp-server/remote-mcp-server?view=azure-devops) - client authentication limitation
- [What are the Azure MCP Server tools?](https://learn.microsoft.com/azure/developer/azure-mcp-server/tools/) - confirms no work item namespace
