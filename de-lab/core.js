/* Deterministic, educational data engineering simulations.
 * Synthetic figures are not measurements of any production system.
 * Browser global and Node CommonJS exports keep testing dependency-free.
 */
(function (root) {
  'use strict';
  const MODES = Object.freeze(['incremental', 'full']);
  const ISSUES = Object.freeze(['none', 'duplicates', 'schema', 'late']);
  const clamp = (n, low, high) => Math.min(high, Math.max(low, n));

  function simulateCDC(input) {
    const options = input || {};
    const mode = MODES.includes(options.mode) ? options.mode : 'incremental';
    const issue = ISSUES.includes(options.issue) ? options.issue : 'none';
    const inputEvents = clamp(Math.round(Number(options.events) || 1200), 100, 10000);
    const rejects = issue === 'schema' ? Math.round(inputEvents * 0.12) : 0;
    const duplicates = issue === 'duplicates' ? Math.round(inputEvents * 0.09) : 0;
    const delayed = issue === 'late' ? Math.round(inputEvents * 0.07) : 0;
    const applied = inputEvents - rejects - duplicates - delayed;
    const seconds = +(mode === 'incremental'
      ? 0.9 + inputEvents / 2100 + (issue === 'schema' ? 0.3 : 0)
      : 5.6 + inputEvents / 430).toFixed(2);
    const lagMs = Math.round(seconds * (mode === 'incremental' ? 72 : 160));
    return {mode, issue, inputEvents, applied, rejects, duplicates, delayed,
      seconds, lagMs, efficiency: Math.round((1 - seconds / (5.6 + inputEvents / 430)) * 100)};
  }

  const ROW_SETS = Object.freeze({
    clean: [
      {id: 'A101', effective: '2026-10-01', amount: 1200},
      {id: 'A102', effective: '2026-10-02', amount: 1420},
      {id: 'A103', effective: '2026-10-03', amount: 1560},
      {id: 'A104', effective: '2026-10-04', amount: 1190}
    ],
    duplicates: [
      {id: 'A101', effective: '2026-10-01', amount: 1200},
      {id: 'A102', effective: '2026-10-02', amount: 1420},
      {id: 'A102', effective: '2026-10-03', amount: 1420},
      {id: 'A104', effective: '2026-10-04', amount: 1190}
    ],
    sentinel: [
      {id: 'A101', effective: '2026-10-01', amount: 1200},
      {id: 'A102', effective: '1900-12-31', amount: 1420},
      {id: 'A103', effective: '2026-10-03', amount: null},
      {id: 'A104', effective: '2026-10-04', amount: 1190}
    ]
  });

  function rowsForScenario(name) {
    const list = ROW_SETS[name] || ROW_SETS.clean;
    return list.map(row => ({...row}));
  }

  function validateRows(rows) {
    if (!Array.isArray(rows)) return {total: 0, valid: 0, invalid: 0, findings: []};
    const seen = new Set();
    const findings = [];
    rows.forEach((row, index) => {
      if (!row || typeof row !== 'object') {
        findings.push({index, rule: 'ROW_SHAPE', message: 'Row must be an object.'});
        return;
      }
      const id = String(row.id == null ? '' : row.id).trim();
      if (!id) findings.push({index, rule: 'REQUIRED_ID', message: 'Missing record ID.'});
      else if (seen.has(id)) findings.push({index, rule: 'UNIQUE_GRAIN', message: 'Duplicate business key ' + id + '.'});
      else seen.add(id);
      if (row.effective === '1900-12-31' || !/^\d{4}-\d{2}-\d{2}$/.test(String(row.effective || ''))) {
        findings.push({index, rule: 'VALID_DATE', message: 'Missing, malformed, or sentinel effective date.'});
      }
      if (row.amount == null || !Number.isFinite(Number(row.amount))) {
        findings.push({index, rule: 'REQUIRED_AMOUNT', message: 'Amount is missing or non-numeric.'});
      }
    });
    const invalid = new Set(findings.map(f => f.index)).size;
    return {total: rows.length, valid: rows.length - invalid, invalid, findings};
  }

  const api = Object.freeze({simulateCDC, rowsForScenario, validateRows});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.DELabCore = api;
})(typeof window !== 'undefined' ? window : undefined);
