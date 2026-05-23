#!/usr/bin/env bash
# M1 smoke checks for the narendranathe/resume2 Pages migration.
#
# Validates the architectural assumptions named in PRD #100 / issue #101 / scope-lock
# at https://github.com/narendranathe/narendranathe.github.io/issues/100#issuecomment-4524042426:
#
#   1. GH Pages on a project page (narendranathe/resume2) serves with correct MIME for
#      jpg, png, avif, webp, json.
#   2. ?v=<hash> cache-bust query strings survive Fastly cache keying.
#   3. Tag deletion on resume2@main is NOT blocked by branch protection / rulesets.
#
# If any of these fail, M1's architecture assumptions are invalid; do not proceed to M2.
# Run from the portfolio repo root:
#
#     bash scripts/m1-smoke-checks.sh
#
# Requirements: bash, curl, git, gh CLI (authenticated as narendranathe).
# Exits 0 on all pass; 1 on any failure with a clear stderr message.

set -uo pipefail

MEDIA_ORIGIN="https://narendranathe.github.io/resume2"
RESUME2_REMOTE="git@github.com:narendranathe/resume2.git"
FAIL_COUNT=0
PASS_COUNT=0

# ── helpers ────────────────────────────────────────────────────────────────

red()    { printf '\033[31m%s\033[0m\n' "$*" >&2; }
green()  { printf '\033[32m%s\033[0m\n' "$*"; }
yellow() { printf '\033[33m%s\033[0m\n' "$*"; }

assert_status_and_content_type() {
  local url="$1"
  local expected_ct="$2"
  local label="$3"

  local response status content_type
  response="$(curl -sI -L -o /dev/null -w '%{http_code}|%{content_type}' --max-time 15 "$url" 2>/dev/null || echo "000|")"
  status="${response%%|*}"
  content_type="${response##*|}"
  # Strip charset suffix (e.g. "application/json; charset=utf-8" -> "application/json")
  content_type="${content_type%%;*}"
  content_type="${content_type// /}"

  if [[ "$status" != "200" ]]; then
    red "  FAIL [$label] $url -> status $status (expected 200)"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
  if [[ "$content_type" != "$expected_ct" ]]; then
    red "  FAIL [$label] $url -> Content-Type '$content_type' (expected '$expected_ct')"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
  green "  PASS [$label] $url -> 200 + $content_type"
  PASS_COUNT=$((PASS_COUNT + 1))
}

# ── gate 1: Pages site is up ────────────────────────────────────────────────

echo
yellow "Gate 1: $MEDIA_ORIGIN reachable"
root_status="$(curl -sI -o /dev/null -w '%{http_code}' --max-time 10 "$MEDIA_ORIGIN/" 2>/dev/null || echo "000")"
if [[ "$root_status" =~ ^(200|301|302|304)$ ]]; then
  green "  PASS root URL responds ($root_status)"
  PASS_COUNT=$((PASS_COUNT + 1))
else
  red "  FAIL root URL returned $root_status. Have you enabled Pages on narendranathe/resume2?"
  red "       See docs/m1-resume2-setup.md Step 1."
  FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# ── gate 2: MIME types per file extension ──────────────────────────────────

echo
yellow "Gate 2: MIME types correct for jpg/png/avif/webp/json"
assert_status_and_content_type "$MEDIA_ORIGIN/og/og-image.jpg"            "image/jpeg" "og.jpg"
assert_status_and_content_type "$MEDIA_ORIGIN/headshots/portrait.jpg"     "image/jpeg" "headshot.jpg"
assert_status_and_content_type "$MEDIA_ORIGIN/headshots/portrait.avif"    "image/avif" "headshot.avif"
assert_status_and_content_type "$MEDIA_ORIGIN/headshots/portrait.webp"    "image/webp" "headshot.webp"
assert_status_and_content_type "$MEDIA_ORIGIN/previews/linkedin.png"      "image/png"  "preview.png"
assert_status_and_content_type "$MEDIA_ORIGIN/manifest.json"              "application/json" "manifest.json"

# ── gate 3: ?v= query strings survive ──────────────────────────────────────

echo
yellow "Gate 3: ?v=<hash> cache-bust survives Fastly"
assert_status_and_content_type "$MEDIA_ORIGIN/og/og-image.jpg?v=abc12345"           "image/jpeg" "og.jpg?v=..."
assert_status_and_content_type "$MEDIA_ORIGIN/manifest.json?v=2026-05-23"           "application/json" "manifest.json?v=..."

# ── gate 4: tag deletion not blocked by protection ─────────────────────────

echo
yellow "Gate 4: tag create + push + delete cycle on resume2@main"

TEST_TAG="_m1_proto_test_$(date +%s)"
WORK_DIR="$(mktemp -d -t m1-tag-check-XXXXXX)"
trap "rm -rf '$WORK_DIR'" EXIT

if ! command -v gh >/dev/null 2>&1; then
  red "  FAIL gh CLI not installed. Install gh and re-run."
  FAIL_COUNT=$((FAIL_COUNT + 1))
elif ! gh auth status >/dev/null 2>&1; then
  red "  FAIL gh CLI not authenticated. Run 'gh auth login' first."
  FAIL_COUNT=$((FAIL_COUNT + 1))
else
  (
    set -e
    cd "$WORK_DIR"
    git clone --depth 1 "$RESUME2_REMOTE" resume2 >/dev/null 2>&1
    cd resume2
    git tag "$TEST_TAG"
    git push origin "$TEST_TAG" >/dev/null 2>&1
    git push --delete origin "$TEST_TAG" >/dev/null 2>&1
  )
  if [[ $? -eq 0 ]]; then
    green "  PASS tag create/push/delete cycle succeeded"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    red "  FAIL tag operations blocked. Check Settings -> Rules -> Rulesets for Tag-target rules,"
    red "       and Settings -> Tags for patterns matching 'resume*' or the test tag."
    red "       Fallback strategy: dated tags only + latest.json pointer (see scope-lock comment)."
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
fi

# ── summary ─────────────────────────────────────────────────────────────────

echo
echo "─────────────────────────────────────"
if [[ $FAIL_COUNT -eq 0 ]]; then
  green "All $PASS_COUNT checks passed. M1 architecture assumptions validated."
  echo "  Next: capture lighthouse baseline (Step 6 in docs/m1-resume2-setup.md)"
  echo "        then update the og:image meta tag in index.html (Step 7)."
  exit 0
else
  red "$FAIL_COUNT check(s) failed, $PASS_COUNT passed."
  echo "  Fix the underlying setup before merging M2. See docs/m1-resume2-setup.md."
  exit 1
fi
