/* Accessible, dependency-free controls for the Data Engineering Systems Lab. */
(function () {
  'use strict';
  const core = window.DELabCore;
  if (!core) { console.error('Data Engineering Lab core could not load.'); return; }
  const $ = id => document.getElementById(id);
  const fmt = number => Number(number).toLocaleString('en-US');
  let mode = 'incremental';
  let issue = 'none';
  let dataset = 'clean';
  let runNumber = 0;

  function pressedOptions(selector, activeValue, key) {
    document.querySelectorAll(selector).forEach(button => {
      const isActive = button.dataset[key] === activeValue;
      button.setAttribute('aria-pressed', String(isActive));
      button.classList.toggle('selected', isActive);
      button.classList.toggle('active', isActive);
    });
  }

  function addTrace(lines) {
    const list = $('cdc-log');
    const items = lines.map((line, index) => {
      const item = document.createElement('li');
      const timestamp = document.createElement('span');
      timestamp.textContent = '00:0' + index;
      item.append(timestamp, document.createTextNode(' ' + line));
      return item;
    });
    list.replaceChildren(...items);
  }

  function runCDC() {
    const events = Number($('event-volume').value);
    const r = core.simulateCDC({mode, issue, events});
    runNumber += 1;
    $('metric-applied').textContent = fmt(r.applied);
    $('metric-rejected').textContent = fmt(r.rejects);
    $('metric-seconds').textContent = r.seconds.toFixed(2);
    $('flow-capture').textContent = fmt(r.inputEvents) + ' received';
    $('flow-check').textContent = fmt(r.rejects + r.duplicates + r.delayed) + ' held / skipped';
    $('flow-merge').textContent = fmt(r.applied) + ' applied';
    $('run-status').textContent = 'RUN ' + String(runNumber).padStart(3, '0') + ' / COMPLETED';
    $('cdc-meta').textContent = 'Additional: ' + fmt(r.duplicates) + ' duplicates · ' + fmt(r.delayed) + ' late arrivals · ' + fmt(r.lagMs) + ' ms synthetic lag.';
    const lines = [
      'Captured ' + fmt(r.inputEvents) + ' synthetic change events.',
      issue === 'schema'
        ? 'Schema drift detected: ' + fmt(r.rejects) + ' events quarantined.'
        : issue === 'duplicates'
          ? 'Idempotency check skipped ' + fmt(r.duplicates) + ' duplicate events.'
          : issue === 'late'
            ? 'Watermark held ' + fmt(r.delayed) + ' late-arriving events.'
            : 'Schema, grain and replay checks passed.',
      (mode === 'incremental' ? 'Incremental merge' : 'Full refresh') + ' applied ' + fmt(r.applied) + ' events in ' + r.seconds.toFixed(2) + ' simulated seconds.'
    ];
    addTrace(lines);
    const insights = {
      none: 'Healthy change streams still need a tested replay and recovery path.',
      duplicates: 'At-least-once delivery can repeat messages. Stable keys and idempotent merge logic prevent double-application.',
      schema: 'A schema change should trigger a controlled quarantine, not silently corrupt the downstream contract.',
      late: 'Late events need a watermark, backfill or policy. Applying all messages immediately can break correctness.'
    };
    $('cdc-insight').textContent = insights[issue] + (mode === 'full' ? ' Full refresh reprocesses the whole dataset, trading simplicity for more work.' : ' Incremental strategy reduces work by processing changes.');
  }

  function previewDQ(validated) {
    const rows = core.rowsForScenario(dataset);
    const result = core.validateRows(rows);
    const failedByIndex = new Map();
    result.findings.forEach(finding => {
      if (!failedByIndex.has(finding.index)) failedByIndex.set(finding.index, []);
      failedByIndex.get(finding.index).push(finding.rule);
    });
    const body = $('dq-rows');
    const entries = rows.map((row, index) => {
      const tr = document.createElement('tr');
      const failures = validated ? failedByIndex.get(index) : null;
      if (failures) tr.classList.add('invalid');
      [row.id, row.effective, row.amount == null ? 'NULL' : fmt(row.amount), !validated ? '—' : failures ? 'FAIL' : 'PASS'].forEach(value => {
        const td = document.createElement('td');
        td.textContent = String(value);
        tr.appendChild(td);
      });
      return tr;
    });
    body.replaceChildren(...entries);
    const summary = $('dq-summary');
    summary.classList.toggle('failed', validated && result.invalid > 0);
    if (!validated) {
      summary.textContent = 'READY TO CHECK';
      $('dq-findings').textContent = 'Press Validate records to run all three data contracts.';
    } else {
      summary.textContent = fmt(result.valid) + ' / ' + fmt(result.total) + (result.invalid ? ' PASSED' : ' PASSED ✓');
      $('dq-findings').textContent = result.findings.length
        ? result.findings.map(f => 'Row ' + (f.index + 1) + ': ' + f.rule + ' - ' + f.message).join('\n')
        : 'No violations detected. Ready for merge.';
    }
  }

  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
    mode = button.dataset.mode;
    pressedOptions('[data-mode]', mode, 'mode');
  }));
  document.querySelectorAll('[data-issue]').forEach(button => button.addEventListener('click', () => {
    issue = button.dataset.issue;
    pressedOptions('[data-issue]', issue, 'issue');
  }));
  $('event-volume').addEventListener('input', event => {
    $('volume-readout').textContent = fmt(event.target.value) + ' events';
  });
  $('run-cdc').addEventListener('click', runCDC);

  document.querySelectorAll('[data-dataset]').forEach(button => button.addEventListener('click', () => {
    dataset = button.dataset.dataset;
    pressedOptions('[data-dataset]', dataset, 'dataset');
    previewDQ(false);
  }));
  $('run-dq').addEventListener('click', () => previewDQ(true));

  const tabs = Array.from(document.querySelectorAll('[role=tab]'));
  function activateTab(tab, focus) {
    tabs.forEach(other => {
      const active = other === tab;
      other.setAttribute('aria-selected', String(active));
      other.tabIndex = active ? 0 : -1;
      other.classList.toggle('active', active);
      const panel = $('panel-' + other.dataset.panel);
      panel.hidden = !active;
    });
    if (focus) tab.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab, false));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
        : (index + (event.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length;
      activateTab(tabs[next], true);
    });
  });

  const toggle = document.querySelector('.nav-toggle');
  const nav = $('nav-links');
  function closeNav() {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }
  toggle.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(opened));
    toggle.setAttribute('aria-label', opened ? 'Close navigation' : 'Open navigation');
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', closeNav));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeNav();
  });

  $('year').textContent = String(new Date().getFullYear());
  runCDC();
  previewDQ(true);
})();
