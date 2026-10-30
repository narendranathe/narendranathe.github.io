const test = require('node:test');
const assert = require('node:assert/strict');
const {simulateCDC, rowsForScenario, validateRows} = require('../core.js');

test('incremental model is faster than full reload for the same volume', () => {
  const fast = simulateCDC({events: 2400, mode: 'incremental'});
  const slow = simulateCDC({events: 2400, mode: 'full'});
  assert.equal(fast.applied, 2400);
  assert.ok(fast.seconds < slow.seconds);
  assert.ok(fast.efficiency > 0);
});

test('duplicate CDC messages are idempotently excluded', () => {
  const run = simulateCDC({events: 1000, issue: 'duplicates'});
  assert.equal(run.duplicates, 90);
  assert.equal(run.applied + run.duplicates, run.inputEvents);
});

test('schema drift quarantines invalid events instead of applying them', () => {
  const run = simulateCDC({events: 1000, issue: 'schema'});
  assert.equal(run.rejects, 120);
  assert.equal(run.applied, 880);
});

test('late arrivals are flagged separately, not silently counted as applied', () => {
  const run = simulateCDC({events: 1000, issue: 'late'});
  assert.equal(run.delayed, 70);
  assert.equal(run.applied, 930);
});

test('untrusted controls are clamped and default to known modes', () => {
  const run = simulateCDC({events: 100000, mode: 'invented', issue: 'invented'});
  assert.equal(run.inputEvents, 10000);
  assert.equal(run.mode, 'incremental');
  assert.equal(run.issue, 'none');
});

test('clean rows pass all data contracts', () => {
  const result = validateRows(rowsForScenario('clean'));
  assert.equal(result.valid, 4);
  assert.equal(result.invalid, 0);
  assert.equal(result.findings.length, 0);
});

test('duplicate business grain fails precisely one row', () => {
  const result = validateRows(rowsForScenario('duplicates'));
  assert.equal(result.invalid, 1);
  assert.equal(result.findings[0].rule, 'UNIQUE_GRAIN');
});

test('sentinel dates and missing fields fail with explicit rules', () => {
  const result = validateRows(rowsForScenario('sentinel'));
  assert.equal(result.invalid, 2);
  assert.deepEqual(result.findings.map(f => f.rule), ['VALID_DATE', 'REQUIRED_AMOUNT']);
});

test('invalid input cannot crash validation', () => {
  assert.equal(validateRows(null).total, 0);
  assert.equal(validateRows([null]).invalid, 1);
});

test('each scenario returns an independent array, not shared mutable state', () => {
  const rows = rowsForScenario('clean');
  rows[0].amount = 0;
  assert.equal(rowsForScenario('clean')[0].amount, 1200);
});
