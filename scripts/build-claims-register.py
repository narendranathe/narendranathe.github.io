#!/usr/bin/env python3
"""
Build the claims register from the page's own data-gt-id attributes.

Every visible claim on index.html cites a GROUND_TRUTH.md evidence id in
a data-gt-id attribute. This script reads those attributes back out,
joins them to the evidence status table below, and writes
static/claims-register.csv.

Generating the register from the page rather than maintaining it by hand
is the whole point: a hand-kept register drifts the moment someone edits
a section, and a register that disagrees with the page is worse than no
register. If a claim moves, the row moves with it.

Statuses follow GROUND_TRUTH.md:

  DOC      backed by something a third party can open: a public repo, a
           DOI, a certification, or the 2021 resume.
  STATED   the owner's own account of their work. Usable, and honest to
           label as such, but not independently checkable.
  VERIFY   unresolved conflict or missing value. MUST NOT be published.
  BLOCKED  does not ship until the stated problem is fixed.

Usage
-----
    python scripts/build-claims-register.py            # write the CSV
    python scripts/build-claims-register.py --check    # CI: verify in sync
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO_ROOT / "index.html"
REGISTER_CSV = REPO_ROOT / "static" / "claims-register.csv"

# id -> (claim, status, how a reader checks it)
#
# The four project ids marked DOC were read directly from their public
# repositories on 2026-08-15; the "evidence" column names the file or
# artifact that settles each one. AutoApply is STATED precisely because
# it is private: no amount of confidence makes a closed repo checkable.
EVIDENCE: dict[str, tuple[str, str, str]] = {
    # --- ExponentHR ---
    "E-PTO": ("Payroll accrual defect root-caused in SQL and shipped to every client tenant through change-request review", "STATED", "Employment record; no public artifact"),
    "E-SECURE2": ("SECURE 2.0 retirement-plan compliance delivered against a legislated deadline", "STATED", "Employment record; no public artifact"),
    "E-SELFHEAL": ("Self-healing monitoring for production SQL Agent jobs across missed, stuck, and silent failures", "STATED", "Employment record; no public artifact"),
    "E5-RECOVERY": ("CDC capture restored under one hour after an availability-group failover, on a documented runbook", "STATED", "Employment record; no public artifact"),
    "E-LIVEREC": ("Live CDC incremental-load failure diagnosed and restored in place under production pressure", "STATED", "Employment record; no public artifact"),
    "E-OBS": ("SSIS execution history rebuilt in SQL; control-table-driven validation making data drift alertable", "STATED", "Employment record; no public artifact"),
    "E-RETENTION": ("Change history recovered through fn_cdc_get_all_changes before the CDC retention window closed", "STATED", "Employment record; no public artifact"),
    "E1-CDC": ("CDC ETL from full reloads to idempotent incremental merge-upserts: 30 min to under 8, compute -67%, freshness SLA held", "STATED", "Employment record; no public artifact"),
    "E-IDEM": ("Database provisioning rewritten idempotent, four latent failure modes closed: 5,000 eng-hrs/yr, ~$300K, 2.5 FTEs", "STATED", "Employment record; derivation in GROUND_TRUTH.md"),
    "E2-CICD": ("Release cycle 3 months to 14 days through end-to-end Azure DevOps ownership; ~11 weeks idle removed per release", "STATED", "Employment record; no public artifact"),
    "E3-FABRIC": ("Reporting migrated to Microsoft Fabric semantic models with OLAP tuning: 12s to under 4s, support tickets -40%", "STATED", "Employment record; ticket derivation in GROUND_TRUTH.md"),
    "E-REPORTAUTO": ("Git and Azure DevOps API workflows automated in Python: 15+ hrs/sprint, ~$23K/yr", "STATED", "Employment record; no public artifact"),
    # --- Missouri S&T ---
    "M1": ("Azure AI Anomaly Detector pipelines at 95%+ accuracy; production memory leak caught 4 hrs before outage", "STATED", "Employment record; no public artifact"),
    "M2": ("Tunable per-service alert thresholds: ~250 weekly P3 alerts filtered, signal-to-noise 1:5 to 1:1.2", "STATED", "Employment record; no public artifact"),
    "M3": ("Static D-series VMs to AKS with horizontal pod autoscaling: -$3,200/mo, CPU 12% to 64%", "STATED", "Employment record; no public artifact"),
    "M4": ("NLP pipelines over 10,000+ reviews, published in the Journal of Nonprofit & Public Sector Marketing", "DOC", "DOI 10.1080/10495142.2025.2525123"),
    # --- C2FO ---
    "C-SQL": ("SQL-driven product and user-behavior analysis on a B2B fintech working-capital platform", "STATED", "Employment record; no public artifact"),
    "C-PRD": ("Requirement documents from stakeholder interviews; resource-allocation time -50%", "STATED", "Self-reported; labeled as such on the page"),
    "C-CSPO": ("Certified Scrum Product Owner", "DOC", "Scrum Alliance certification"),
    # --- Udaan ---
    "U-FORECAST": ("Demand-forecasting and inventory models in Power BI, Excel macros, Google Data Studio: allocation ROI +7%", "STATED", "Employment record; the $4M figure is BLOCKED and absent"),
    "U-FULFILL": ("Statistical demand analysis for capacity planning: 99.3% order fulfillment sustained", "STATED", "Employment record; no public artifact"),
    "U-RCA": ("Root-cause analysis on recurring value-chain failures with process flows rewritten", "DOC", "2021 resume"),
    "U-BCP": ("Business continuity plan devised and executed to keep delivery cycles running through application downtime", "DOC", "2021 resume"),
    # --- Zomato ---
    "Z-COMP": ("Real-time competitor analytics platform: 9% market share gain in contested metros", "STATED", "Employment record; no public artifact"),
    "Z-SEARCH": ("Contextual signals supplied and evaluated for search ranking (analyst side, not model training)", "STATED", "Employment record; scope deliberately narrowed on the page"),
    "Z-ES": ("Elasticsearch index over 100K+ internal documents: support desk volume down ~80%", "STATED", "Employment record; no public artifact"),
    "Z-CAMPAIGN": ("Funnel instrumentation and A/B tests on campaign and discount strategy: campaign revenue +200%", "STATED", "Employment record; no public artifact"),
    "Z-DASH": ("Central dashboard for category-level, city-wise launch percentage", "STATED", "Employment record; no public artifact"),
    "Z-PNL": ("Portfolio contribution from -18 to +2 rupees per order across 300 restaurants", "DOC", "2021 resume"),
    "Z-GROWTH": ("14% compounded growth in one quarter, campaign coverage lifted to 70%", "DOC", "2021 resume"),
    "Z-LOYALTY": ("200+ partners onboarded to a loyalty program, cutting discount burn 7% for that cohort", "DOC", "2021 resume"),
    # --- Projects ---
    "P-HOOKS": ("repo-context-hooks: zero runtime dependencies, 330+ tests, Sigstore-signed releases, CodeQL on every PR", "DOC", "pypi.org/project/repo-context-hooks + pyproject.toml dependencies=[] + .github/workflows/"),
    "P-FRAUD": ("Fraud platform: P99 1.12ms at 100 TPS on 100,000 synthetic transactions with 2,034 labeled fraud", "DOC", "github.com/narendranathe/fraud-detection-ml-platform README + data generator"),
    "P-FINTUNE": ("FinTune: QLoRA 4-bit NF4, PII redaction, KL-divergence drift monitoring, 3-state breaker, 35+ tests across 7 modules", "DOC", "github.com/narendranathe/fintune tests/ + README"),
    "P-JOBSCOUT": ("JobScout: 153 companies across 6 ATS integrations plus Playwright fallback, Flask API, SQLite WAL", "DOC", "github.com/narendranathe/job-scout backend/config/companies.py"),
    "P-AUTOAPPLY": ("AutoApply AI: 40+ endpoints, 11 ATS adapters, 6 LLM providers, 355 backend tests, private Fly.io deployment", "STATED", "Private repo; the page says plainly that these are not checkable"),
    "P-RISK": ("Portfolio Risk Analytics: Spark-to-FastAPI handoff not wired, console sink only, API on generated data", "DOC", "Published as a limitation, not a claim. The original throughput and latency figures remain BLOCKED and absent."),
}

# Present in GROUND_TRUTH.md but deliberately absent from the page.
# Anything listed here appearing in a data-gt-id is a build failure.
WITHHELD: dict[str, tuple[str, str]] = {
    "E-UPTIME": ("VERIFY", "Unconfirmed whether the 98% to 99.9% improvement was owner-driven"),
    "U-TEAM": ("VERIFY", "Verb unresolved: trained and mentored, or hired and managed"),
    "E-SCALE": ("VERIFY", "400 databases / ~70 TB / 10 servers / 15-min cadence unverified against internal records"),
    "U-4M": ("BLOCKED", "$4M savings needs a base roughly 7x documented city GMV"),
    "P-RISK-METRICS": ("BLOCKED", "15K+ records, 47.8 TPS, sub-5s, live risk views unsupported by the repo"),
    "P-RECON": ("VERIFY", "In progress, and unresolved whether it is what earlier notes call SENTINEL"),
}

SECTION_LABELS = {
    "hero": "Hero",
    "proof": "Measured outcomes",
    "experience": "Experience",
    "systems": "Projects",
    "fit": "Where this fits",
}


class Collector(HTMLParser):
    """Record every data-gt-id together with the section it sits in."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.section: str | None = None
        self.hits: list[tuple[str, str]] = []  # (id, section)

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        attrs = dict(attrs_list)
        if tag == "section" and attrs.get("id") in SECTION_LABELS:
            self.section = attrs["id"]
        gid = attrs.get("data-gt-id")
        if gid:
            for one in (x.strip() for x in gid.split(",")):
                if one:
                    self.hits.append((one, self.section or "unknown"))


def collect(html: str) -> list[tuple[str, str]]:
    p = Collector()
    p.feed(html)
    return p.hits


def build_rows(html: str) -> list[dict]:
    hits = collect(html)
    where: dict[str, set[str]] = {}
    for gid, sec in hits:
        where.setdefault(gid, set()).add(SECTION_LABELS.get(sec, sec))

    rows = []
    for gid in sorted(where):
        claim, status, evidence = EVIDENCE.get(
            gid, ("UNKNOWN - not in the evidence table", "VERIFY", "")
        )
        rows.append({
            "id": gid,
            "claim": claim,
            "status": status,
            "evidence": evidence,
            "where_used": "; ".join(sorted(where[gid])),
        })
    return rows


def to_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(
        buf, fieldnames=["id", "claim", "status", "evidence", "where_used"],
        lineterminator="\n",
    )
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="fail if the committed CSV is out of sync with the page")
    args = ap.parse_args()

    html = INDEX_HTML.read_text(encoding="utf-8")
    rows = build_rows(html)
    generated = to_csv(rows)

    problems: list[str] = []

    # A published claim with no evidence row is an uncited number.
    unknown = [r["id"] for r in rows if r["claim"].startswith("UNKNOWN")]
    if unknown:
        problems.append(f"data-gt-id with no evidence-table row: {unknown}")

    # VERIFY and BLOCKED do not ship, per GROUND_TRUTH.md.
    bad = [f'{r["id"]} ({r["status"]})' for r in rows if r["status"] not in ("DOC", "STATED")]
    if bad:
        problems.append(f"unpublishable status on a visible claim: {bad}")

    # Withheld ids must not have leaked back onto the page.
    leaked = [r["id"] for r in rows if r["id"] in WITHHELD]
    if leaked:
        problems.append(f"withheld id published: {leaked}")

    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1

    if args.check:
        if not REGISTER_CSV.exists():
            print(f"FAIL: {REGISTER_CSV} missing; run this script", file=sys.stderr)
            return 1
        if REGISTER_CSV.read_text(encoding="utf-8") != generated:
            print("FAIL: claims-register.csv is stale; regenerate it", file=sys.stderr)
            return 1
        print(f"claims register in sync: {len(rows)} claims")
        return 0

    REGISTER_CSV.parent.mkdir(parents=True, exist_ok=True)
    REGISTER_CSV.write_text(generated, encoding="utf-8")
    doc = sum(1 for r in rows if r["status"] == "DOC")
    print(f"wrote {REGISTER_CSV.relative_to(REPO_ROOT)}: {len(rows)} claims "
          f"({doc} DOC, {len(rows) - doc} STATED), {len(WITHHELD)} withheld")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
