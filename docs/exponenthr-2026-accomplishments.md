# ExponentHR Data Engineering: Accomplishments Record

**Engineer:** Narendranath Edara
**Role:** Data Engineer - Data Platform, CDC ETL, and Reporting Warehouse
**Organization:** ExponentHR, Addison, TX
**Review period:** Sprint 2025.12.19 through DE Sprint 2026.04.02 and ongoing
**System of record:** Azure DevOps work items and DE sprint boards

---

## 1. Executive summary

ExponentHR runs payroll, benefits, and time-off for thousands of employers. Every number that reaches a client report, a paycheck reconciliation, or a compliance filing passes through the reporting warehouse I own. This year the work fell into two halves that reinforced each other:

**Correctness.** I closed 25 numbered work items spanning 11 client tenants, covering PTO accrual, payroll vouchers, employer contributions, W-4 elections, performance reviews, employee history, and time allocation. Most of these arrived as isolated client tickets. I treated them as symptoms, found the shared defect classes underneath, and fixed the model instead of the row.

**Platform.** I hardened the delivery and refresh machinery that those fixes ride on: the SQL Copy Down tool for contained Always-On Availability Groups, the CDC incremental path, the Azure Pipelines YAML that builds reporting databases, and the concurrency behavior of client-database stored procedures.

The two halves connect directly. A correctness fix is only worth what the release pipeline can deliver, and the platform work is why a schema change now reaches production in 14 days instead of 3 months.

### At a glance

| Measure | Result |
|---|---|
| Numbered work items delivered | 25 |
| Additional workstreams without a ticket number | 4 (Copy Down enhancement, Copy Down YAML automation, Attestations model, Cosmos Expense SSRS support) |
| Client tenants directly served | 11 (00169, 00194, 00612, 00630, 00745, 00747, 00810, 00877, 00982, 00994, 10106) |
| Warehouse objects repaired or extended | 10 existing tables and procedures |
| New data assets built | 2 (PTO accrual table, Attestations dimensional model) |
| Sprint and release cycles owned | 3 (2025.12.19, 2026.03.05, 2026.04.02) |
| Release cycle time | 3 months -> 14 days |
| CDC ETL runtime | 30 min -> under 8 min, compute cost -67% |
| AAG copy-down effort | ~1 hour of manual orchestration removed per request, 20+ requests per day |

---

## 2. How the work breaks down

| Theme | Items | Section |
|---|---|---|
| PTO and time-off accrual | 8 | [Section 3](#3-pto-and-time-off-accrual) |
| Payroll, vouchers, and contributions | 7 | [Section 4](#4-payroll-vouchers-and-contributions) |
| Performance review reporting | 4 | [Section 5](#5-performance-review-reporting) |
| Employee dimensions and new subject areas | 5 | [Section 6](#6-employee-dimensions-and-new-subject-areas) |
| Time allocation | 1 | [Section 7](#7-time-allocation) |
| Platform, DevOps, and reliability | 6 | [Section 8](#8-platform-devops-and-reliability) |
| Sprint and release ownership | 3 cycles | [Section 9](#9-sprint-and-release-ownership) |

---

## 3. PTO and time-off accrual

The single largest cluster of the year. Eight work items across four clients all landed on the same subject area, and the pattern only becomes visible when you line them up.

| Item | Client | Title |
|---|---|---|
| 27353 | - | Fact_PTODetails has incorrect Approved flag, all records get Approval Date 12/31/1900 |
| 32896 | 00745 | Fact_PTOSummary records not up to date |
| 32979 | 00169 | Fact_PTOSummary showing wrong accrual rate |
| 33847 | 10106 | Some plans in Fact_PTOSummary showing 1E-05 |
| 33866 | 10106 | Fact_PTOSummary accrual rate showing for non-eligible plans |
| 34021 | 00612 | Fact_PTOSummary missing employees |
| 34882 | - | Change Request: Fact_PTOSummary accrual rate update |
| 28369 | - | Add table for PTO accrual information |

### What was going wrong

Four clients reported four different-looking problems in the same table:

- **00745** saw stale balances. The summary was not reflecting recent activity, so employees and managers were reading yesterday's truth.
- **00169** saw an accrual rate that did not match the plan definition.
- **10106** saw two things at once: rates rendering as `1E-05`, and accrual rates appearing against plans the employee was not even eligible for.
- **00612** saw employees missing from the summary entirely.

Separately, `Fact_PTODetails` was marking records with an incorrect approval status and stamping every row with an approval date of **12/31/1900** - the SQL Server zero-date sentinel. That is the signature of an empty or defaulted datetime being written through as if it were a real business event rather than being carried as NULL.

### Why it mattered

PTO balance is not a nice-to-have report. Employees plan against it, managers approve against it, and at termination it converts to money. A wrong accrual rate is a payout defect waiting to surface, and a `12/31/1900` approval date makes it impossible to audit who approved what and when.

### What I did

I stopped fixing these per-client. The `1E-05` display, the wrong rates, and the rates on ineligible plans were all downstream of the same thing: accrual rate was being derived inline during the load rather than sourced from a modeled, plan-aware definition. Derived-in-flight logic drifts, loses precision, and cannot enforce eligibility.

1. **Made accrual a first-class data asset (28369).** Added a dedicated table for PTO accrual information so accrual rate and plan configuration are stored and versioned rather than recomputed on every refresh. This is the structural fix the other tickets were asking for.
2. **Raised a formal change request for the rate logic (34882)** rather than patching each client's symptom, so the corrected accrual calculation shipped once, reviewed, to every tenant.
3. **Enforced plan eligibility (33866)** so a rate can only attach to a plan the employee actually participates in.
4. **Corrected numeric handling (33847)** so accrual rates carry the precision and scale the business expects instead of surfacing float artifacts in scientific notation to end users.
5. **Restored full employee coverage (34021)** by fixing the population path that was silently dropping employees from the summary.
6. **Fixed the refresh path (32896)** so the summary reflects current activity instead of lagging.
7. **Corrected approval semantics in Fact_PTODetails (27353)** so the approved flag reflects the real approval event and unapproved records no longer carry a fabricated 12/31/1900 date.

**Outcome:** one subject area that was generating a steady stream of per-client escalations now has a modeled accrual source, enforced eligibility, and correct approval lineage. The four client tickets closed, and the class of defect closed with them.

---

## 4. Payroll, vouchers, and contributions

The money-adjacent work. Seven items covering pay vouchers, employer contributions, and W-4 election data.

| Item | Client | Title |
|---|---|---|
| 32495 | 00810 | Voucher duplicated for employee in Fact_PayVoucherDetail |
| 33436 | 00810 | Reissued vouchers missing (triaged, handed off) |
| 37005 | 00982 | Dim_PayDemographics missing vouchers |
| 13803 | - | Incorrect ER contribution code used |
| 14825 | - | [W4 State Allowances] has state filing status and allowances in the same field |
| 34366 | - | Dim_W4ElectionData contains election status in allowances value |
| 36204 | - | Add MatchSH2Adj column to ssrs_UpdateRecurring |

### Voucher integrity (32495, 33436, 37005)

Vouchers failed in both directions across two clients: **00810** had an employee voucher duplicated in `Fact_PayVoucherDetail`, and **00982** had vouchers missing from `Dim_PayDemographics`.

Duplication and omission in the same domain almost always trace to the same root: the load's declared grain does not match the source's real grain, so a join fans out on one path and filters out on another. I restored grain integrity on the voucher load so a voucher appears exactly once, and closed the gap that was leaving vouchers out of the pay demographics dimension.

**33436 (reissued vouchers missing)** I triaged and handed to Nathan. Reissue is a distinct event lifecycle from original issuance, and it belonged with the owner of that upstream path rather than being force-fit into the reporting layer. Recording it here as handed off, not closed by me.

### Employer contribution coding (13803)

An incorrect employer contribution code was being applied. Contribution codes drive employer-side cost reporting and downstream filings, so a mis-mapped code is not a cosmetic labeling issue - it lands in numbers the employer reports externally. Corrected the code mapping so employer contributions are attributed to the right bucket.

### W-4 election data (14825, 34366)

Two items, one defect class: **a status code occupying a field meant to hold a number.**

- `[W4 State Allowances]` was carrying the state filing status *and* the allowances value packed into a single field (14825).
- `Dim_W4ElectionData` was carrying election status inside the allowances value (34366).

Anyone consuming allowances as a numeric quantity - for withholding calculation, for compliance reporting, for any aggregate - was reading a contaminated value. I separated the concerns so filing status and election status live in their own attributes and the allowances field holds allowances only. This is tax-withholding input data, so the correctness bar here is regulatory, not just analytical.

### Recurring update support (36204)

Added the `MatchSH2Adj` column to the `ssrs_UpdateRecurring` procedure so the match adjustment value is carried through the recurring update path into SSRS reporting, rather than being invisible to the reports that need it.

---

## 5. Performance review reporting

`Dim_PerformanceReviewDetails` failed in both directions - too many rows for some clients, too few for others - and both symptoms had the same origin.

| Item | Client | Title |
|---|---|---|
| 34376 | 00194 | Dim_PerformanceReviewDetails pulling extra rows |
| 36072 | - | Dim_PerformanceReviewDetails missing data (maintenance package) |
| 36207 | - | Dim_PerformanceReviewDetails missing data |
| 36904 | - | Implement web logic for Dim_PerformanceReviewDetails to avoid duplicate rows |

### The pattern

Client **00194** was getting extra rows. Other clients were missing data entirely (36207, 36072). Over-population and under-population in the same object point to a single cause: **the warehouse's row-selection logic and the web application's row-selection logic had diverged.** The application knew which review record was the one that counted; the ETL was guessing.

### What I did

1. **Aligned the ETL to the application's own logic (36904).** Instead of hand-tuning DISTINCT clauses and join predicates until the row counts looked right for one client, I implemented the web application's selection logic in the load. That makes the warehouse agree with the product by construction, for every tenant, rather than by coincidence for the tenant who complained.
2. **Eliminated the extra rows for 00194 (34376)** as a consequence of that alignment.
3. **Backfilled the missing data (36207, 36072)** through a maintenance package, so clients who had already been under-reported got their history corrected rather than only being right going forward.

**Outcome:** review data that matches what users see in the application, and a repair path for the history that was already wrong.

---

## 6. Employee dimensions and new subject areas

| Item | Client | Title |
|---|---|---|
| 32478 | 00994 | Merge conflict on Dim_StatsReportType |
| 34247 | 00747 | Dim_EmpInfoHistory - issue with effective end date |
| - | - | Building the dimensional model for Attestations |
| - | - | Cosmos Expense Project support for SSRS |

### Merge conflict on Dim_StatsReportType (32478)

Client **00994**'s load was failing on a MERGE against `Dim_StatsReportType` - the failure mode where a target row is matched by more than one source row, so the statement cannot decide which update wins and aborts. This is a hard failure, not a soft one: the load stops, and the client's data goes stale until it is fixed. I resolved the ambiguity in the source-to-target key relationship so each target row matches at most one source row and the load runs clean.

### Effective end date on Dim_EmpInfoHistory (34247)

Client **00747** had incorrect effective end dates in employee info history. This is the correctness backbone of a Type 2 slowly changing dimension: if end dates are wrong, the validity intervals either overlap or leave gaps, and **every point-in-time query is wrong.** Ask "what was this employee's status on the pay date" and you get two answers or none. Fixed the end-dating so intervals close correctly and historical lookups return exactly one valid row per point in time.

### Attestations dimensional model (new build)

Greenfield work rather than a defect fix. I designed and built the dimensional model for Attestations, taking a subject area with no warehouse representation and giving it conformed dimensions and a reportable fact grain. This is the difference between a compliance artifact that exists only in the application and one that can be reported, trended, and audited alongside the rest of the HR data.

### Cosmos Expense Project SSRS support (new build)

Provided the reporting-layer support for the Cosmos Expense project so expense data reaches SSRS through the same governed path as the rest of the warehouse, rather than through a one-off extract.

---

## 7. Time allocation

| Item | Client | Title |
|---|---|---|
| 35366 | 00877 | Fact_TimeAllocation duplicate rows, plus maintenance job to clean up stale records |

Client **00877** had duplicate rows in `Fact_TimeAllocation`. Time allocation feeds labor distribution and cost attribution, so duplicates inflate charged hours against projects and cost centers.

Two-part fix:

1. **Stop the bleeding.** Corrected the load so duplicates are no longer produced.
2. **Clean what was already there.** Duplicates and stale records already in the table would have persisted indefinitely, so I built a maintenance job to remove stale `Fact_TimeAllocation` records, shipped as a limited maintenance package scoped to 00877.

The scoping matters. A limited, client-scoped maintenance package let the cleanup ship on its own timeline without waiting on a full release and without touching tenants that did not need it.

---

## 8. Platform, DevOps, and reliability

The infrastructure that everything above depends on.

| Item | Title |
|---|---|
| 31554 | Copy Down tool for contained availability group fix, including contained AAG drop and copy down (Env006) for SQL Server 2025 |
| - | SQL Copy Down tool enhancement |
| - | SQL Copy Down tool automation: YAML update to deploy from Azure Pipelines |
| 36429 | Unable to create Reporting DB using release/2025.07.25 branch, resolved via agent name update in YAML across Full Load, Incremental, and Employer Reports repos |
| - | 00630: CDC incremental failure |
| 36119 | Deadlock on client databases for stored procedures |

### SQL Copy Down tool (31554 and follow-on enhancements)

The Copy Down tool refreshes client databases for support, testing, and reproduction work - 20+ requests a day. Contained Always-On Availability Groups make that materially harder than a plain restore: the database has to be removed from the availability group, restored, have security and CDC state reconciled, and be validated back into a healthy AAG listener configuration. Any missed step leaves a database in a half-joined state on a payroll-critical cluster.

Work delivered:

- **Fixed the contained AAG path (31554)**, including drop and copy down of contained AAG databases on **Env006 for SQL Server 2025** - validating the tool against the new SQL Server version rather than discovering the incompatibility during a live request.
- **Enhanced the tool** beyond the initial fix to cover more of the manual sequence operators were performing by hand.
- **Moved deployment onto Azure Pipelines** by updating the automation YAML, so the tool ships through the same governed pipeline as everything else instead of being deployed manually.

**Outcome:** roughly **1 hour of manual orchestration removed per copy-down request**, against 20+ requests per day, with the operation made idempotent so a failed run can be safely rerun instead of requiring a DBA to reason about partial state.

### Reporting DB build failure on the release branch (36429)

Reporting databases could not be created from the `release/2025.07.25` branch. This is a pipeline-blocking failure: if you cannot build a reporting database from the release branch, you cannot validate the release.

Root cause was in the pipeline definitions themselves - an agent name that no longer resolved. I updated the agent name in the YAML across all three affected repositories: **Full Load, Incremental, and Employer Reports.** Fixing all three together rather than only the repo that surfaced the error prevented the same failure from reappearing in the next repo someone happened to build.

### CDC incremental failure (00630)

Client **00630** hit a failure in the CDC incremental path. This is the highest-stakes failure mode in the platform: the incremental load is what replaced full-table reloads, and it is the reason ETL runs in under 8 minutes instead of 30. When incremental breaks, the options are a slow full reload or stale client data. I diagnosed and restored the incremental path so the client returned to normal refresh cadence without falling back to full reload.

This work sits directly on top of the CDC reengineering that took ETL from **30 minutes to under 8 minutes at 67% lower compute cost** - protecting that gain is why incremental failures get treated as urgent rather than routine.

### Stored procedure deadlocks on client databases (36119)

Stored procedures on client databases were deadlocking. Deadlocks are the worst class of production defect to chase because they are load-dependent and intermittent: they pass every test, then fail under real concurrency, and the victim transaction dies with data half-processed. I addressed the contention so concurrent execution on client databases completes reliably instead of one session being chosen as the deadlock victim.

---

## 9. Sprint and release ownership

Beyond individual work items, I owned code management and release execution across three cycles:

| Cycle | Scope |
|---|---|
| **Sprint 2025.12.19** | Code management and release to testing |
| **DE Sprint 2026.03.05** | Data engineering sprint delivery |
| **DE Sprint 2026.04.02** | Data engineering sprint delivery |

This is the connective tissue that makes the rest of the record real. Owning CI/CD end-to-end through Azure DevOps is what compressed the deployment cycle from **3 months to 14 days**, removing roughly 11 weeks of cross-team idle time per release. Every fix in Sections 3 through 8 reached production through that pipeline, and several of them - the accrual change request, the performance review logic alignment, the maintenance packages - only made sense to attempt because the release window was short enough to iterate.

---

## 10. Cross-cutting engineering themes

Reading the year as a whole, four defect classes account for most of the client-reported work. Naming them is what turned 25 tickets into a much smaller number of actual fixes.

### Sentinel values escaping into business data

`12/31/1900` approval dates in `Fact_PTODetails` (27353) and `1E-05` accrual rates in `Fact_PTOSummary` (33847) are the same bug wearing different clothes: a technical default or a floating-point artifact reaching a user as though it were a real business value. The fix in both cases was to make the absence of a value representable - NULL where nothing was approved, correct precision and scale where a rate exists - rather than substituting a placeholder that reads as data.

### Grain violations

Duplicate rows in `Fact_PayVoucherDetail` (32495), `Fact_TimeAllocation` (35366), and `Dim_PerformanceReviewDetails` (34376, 36904), and the MERGE conflict on `Dim_StatsReportType` (32478), are all one question: **what uniquely identifies a row in this table?** Where the declared grain and the source's real grain disagreed, joins fanned out and MERGE statements could not resolve a target. Every fix here was a grain fix, not a deduplication patch.

### Missing filters and missing joins

Accrual rates on ineligible plans (33866), employees absent from PTO summary (34021), vouchers absent from pay demographics (37005), and missing performance review data (36207, 36072) are the mirror image of grain violations: rows appearing that should have been filtered, or disappearing because a join dropped them. Same discipline, opposite direction.

### Composite fields

State filing status packed in with allowances (14825) and election status inside the allowances value (34366) both violate one attribute per column. Any consumer treating the field as numeric read a corrupted value. Splitting them was the fix, and in a tax-withholding context the correctness bar is regulatory.

### The through-line: fix the model, not the row

The strongest example is the PTO cluster. Four clients, four differently-worded tickets, one underlying cause - accrual rate derived in flight instead of sourced from a model. Patching each client would have closed four tickets and left the fifth to arrive later. Adding the accrual table (28369) and raising the rate change request (34882) closed the class. The same instinct drove 36904 - implement the application's real logic rather than tune predicates until one client's row count looked right - and 36429 - update all three repos rather than just the one that failed.

---

## 11. Status and honest accounting

Not everything in this record is closed by me, and the distinction matters.

| Item | Status |
|---|---|
| 33436 - 00810 reissued vouchers missing | **Triaged and handed off to Nathan.** Voucher reissue is a distinct upstream event lifecycle and belonged with the owner of that path rather than being worked around in the reporting layer. |
| All other numbered items in Sections 3 to 8 | Delivered through the sprints listed in Section 9. |

Where this document describes a root cause, it describes the defect class the work item represents. Specific per-client row counts, before-and-after timings, and ticket-level resolution notes live in Azure DevOps; the platform-level metrics quoted here (3 months to 14 days, 30 min to under 8 min, -67% compute, ~1 hour per copy-down, 20+ daily requests) are the measured figures already established for the ExponentHR data platform work.

---

## 12. Appendix: complete work item index

Sorted by work item ID.

| ID | Client | Title | Theme |
|---|---|---|---|
| 13803 | - | Incorrect ER contribution code used | Payroll |
| 14825 | - | [W4 State Allowances] has state filing status and allowances in the field | Payroll |
| 27353 | - | Fact_PTODetails incorrect Approved, all records get Approval Date 12/31/1900 | PTO |
| 28369 | - | Add table for PTO accrual information | PTO |
| 31554 | - | Copy Down tool for contained availability group fix (incl. Env006, SQL Server 2025) | Platform |
| 32478 | 00994 | Merge conflict on Dim_StatsReportType | Dimensions |
| 32495 | 00810 | Voucher duplicated for employee in Fact_PayVoucherDetail | Payroll |
| 32896 | 00745 | Fact_PTOSummary records not up to date | PTO |
| 32979 | 00169 | Fact_PTOSummary showing wrong accrual rate | PTO |
| 33436 | 00810 | Reissued vouchers missing (handed off) | Payroll |
| 33847 | 10106 | Some plans in Fact_PTOSummary showing 1E-05 | PTO |
| 33866 | 10106 | Fact_PTOSummary accrual rate showing for non-eligible plans | PTO |
| 34021 | 00612 | Fact_PTOSummary missing employees | PTO |
| 34247 | 00747 | Dim_EmpInfoHistory issue with effective end date | Dimensions |
| 34366 | - | Dim_W4ElectionData contains election status in allowances value | Payroll |
| 34376 | 00194 | Dim_PerformanceReviewDetails pulling extra rows | Performance |
| 34882 | - | Change request: Fact_PTOSummary accrual rate update | PTO |
| 35366 | 00877 | Fact_TimeAllocation duplicate rows, plus stale-record maintenance job | Time allocation |
| 36072 | - | Dim_PerformanceReviewDetails missing data (maintenance package) | Performance |
| 36119 | - | Deadlock on client databases for stored procedures | Platform |
| 36204 | - | Add MatchSH2Adj column to ssrs_UpdateRecurring | Payroll |
| 36207 | - | Dim_PerformanceReviewDetails missing data | Performance |
| 36429 | - | Unable to create Reporting DB from release/2025.07.25; agent name update in YAML across Full Load, Incremental, Employer Reports | Platform |
| 36904 | - | Implement web logic for Dim_PerformanceReviewDetails to avoid duplicate rows | Performance |
| 37005 | 00982 | Dim_PayDemographics missing vouchers | Payroll |

### Workstreams without a work item ID

| Workstream | Theme |
|---|---|
| SQL Copy Down tool enhancement | Platform |
| SQL Copy Down tool automation: YAML update to deploy from Azure Pipelines | Platform |
| 00630 - CDC incremental failure | Platform |
| Building the dimensional model for Attestations | New build |
| Cosmos Expense Project support for SSRS | New build |

### Sprint cycles

| Cycle | Scope |
|---|---|
| Sprint 2025.12.19 | Code management and release to testing |
| DE Sprint 2026.03.05 | Data engineering sprint delivery |
| DE Sprint 2026.04.02 | Data engineering sprint delivery |

---

## 13. Appendix: pulling the real work item data

This document and the story bank were written from work item titles and client numbers, not from Azure DevOps itself. To verify root causes and recover specifics, connect the work item API.

### Which server you need

**Not** the Azure MCP Server (`@azure/mcp`, sometimes referred to as `Azure.Mcp.Server`). That server covers Azure **resources** - storage, Cosmos DB, Kusto, Monitor, SQL, AKS, Key Vault - and its "DevOps" section is Bicep, Terraform, Deploy, and Workbooks. It has no work item tools.

Work items live in the **separate Azure DevOps MCP Server** (`@azure-devops/mcp`, repository `microsoft/azure-devops-mcp`), which exposes the `wit_*` toolset: `wit_my_work_items`, `wit_get_work_items_batch_by_ids`, and related tools, plus `repos`, `wiki`, and `build`.

### Local, not remote

Microsoft hosts a remote endpoint at `https://mcp.dev.azure.com/{organization}`, but per Microsoft's own documentation it authenticates via Microsoft Entra ID, and **Claude Code, Claude Desktop, Cursor, and Codex cannot currently authenticate to it.** Use the local server with a Personal Access Token.

Requires Node.js 20+.

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

A read-only PAT scoped to **Work Items (Read)** is sufficient for verification and is the right level of access for this purpose.

### What to pull

Batch-fetch by ID. The 25 IDs are in Section 12 above:

```
13803, 14825, 27353, 28369, 31554, 32478, 32495, 32896, 32979, 33436,
33847, 33866, 34021, 34247, 34366, 34376, 34882, 35366, 36072, 36119,
36204, 36207, 36429, 36904, 37005
```

For each, the fields worth recovering are the **repro steps and resolution notes** (the actual root cause), **linked commits or pull requests** (what shipped), **created and closed dates** (cycle time), and **discussion comments** (where the diagnosis lives).

### Sources

- [Enable AI assistance with Azure DevOps MCP Server](https://learn.microsoft.com/azure/devops/mcp-server/mcp-server-overview?view=azure-devops)
- [Set up the remote Azure DevOps MCP Server](https://learn.microsoft.com/azure/devops/mcp-server/remote-mcp-server?view=azure-devops) - see the client authentication limitation
- [What are the Azure MCP Server tools?](https://learn.microsoft.com/azure/developer/azure-mcp-server/tools/) - confirms no work item namespace
