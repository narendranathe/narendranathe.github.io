/* Local, labeled engineering illustrations. No external services connected. */
(() => {
  'use strict';
  document.querySelectorAll('[data-design-board]').forEach(board => {
    const tabs = [...board.querySelectorAll('[data-board-tab]')];
    const panels = [...board.querySelectorAll('[data-board-panel]')];
    const select = button => {
      tabs.forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
      panels.forEach(panel => { panel.hidden = panel.dataset.boardPanel !== button.dataset.boardTab; });
    };
    tabs.forEach(button => button.addEventListener('click', () => select(button)));
    if (tabs.length) select(tabs.find(tab => tab.getAttribute('aria-pressed') === 'true') || tabs[0]);
  });
  document.querySelectorAll('[data-etl-demo]').forEach(demo => {
    let deliveries = 0;
    const apply = demo.querySelector('[data-etl-apply]');
    const result = demo.querySelector('[data-etl-result]');
    const recordA = demo.querySelector('[data-etl-a]');
    const recordC = demo.querySelector('[data-etl-c]');
    apply.addEventListener('click', () => {
      deliveries += 1; recordA.textContent = '12'; recordC.hidden = false; apply.textContent = 'Replay batch';
      result.textContent = deliveries === 1 ? '1 batch application. A updated, C inserted. Target: A=12, B=20, C=7.' : deliveries + ' batch applications. Same stored result: A=12, B=20, C=7.';
    });
    demo.querySelector('[data-etl-reset]').addEventListener('click', () => {
      deliveries = 0; recordA.textContent = '10'; recordC.hidden = true; apply.textContent = 'Apply batch';
      result.textContent = 'Target: 2 records. Apply an update and an insert.';
    });
  });
  const steps = {
    restore: ['01 / Copy + restore', 'Restore the requested database copy into the target Contained availability-group environment.'],
    security: ['02 / Security setup', 'Configure security for the restored database.'],
    recovery: ['03 / FULL recovery model', 'Set the target database to the FULL recovery model.'],
    cdc: ['04 / Enable CDC', 'Enable change data capture on the refreshed database.'],
    listener: ['05 / Validate listener', 'Validate connectivity through the availability-group listener.']
  };
  document.querySelectorAll('[data-refresh-demo]').forEach(demo => {
    demo.querySelectorAll('[data-refresh-mode]').forEach(button => button.addEventListener('click', () => {
      const automated = button.dataset.refreshMode === 'automated'; demo.dataset.mode = automated ? 'automated' : 'manual';
      demo.querySelectorAll('[data-refresh-mode]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      demo.querySelector('[data-mode-title]').textContent = automated ? 'Azure DevOps orchestration' : 'Manual coordination';
      demo.querySelector('[data-mode-caption]').textContent = automated ? 'Restore and configuration steps run through the refresh workflow.' : 'An engineer coordinates the restore and configuration steps.';
    }));
    demo.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => {
      demo.querySelectorAll('[data-step]').forEach(other => { other.classList.toggle('is-active', other === button); other.setAttribute('aria-pressed', String(other === button)); });
      const value = steps[button.dataset.step]; demo.querySelector('[data-stage-label]').textContent = value[0]; demo.querySelector('[data-stage-description]').textContent = value[1];
    }));
  });
  document.querySelectorAll('[data-grain-demo]').forEach(demo => demo.querySelectorAll('[data-grain]').forEach(button => button.addEventListener('click', () => {
    const joined = button.dataset.grain === 'joined';
    demo.querySelectorAll('[data-grain]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    demo.querySelector('[data-grain-rows]').textContent = joined ? 'Order A / Item 1 / $42\nOrder A / Item 2 / $42' : 'Order A / $42';
    demo.querySelector('[data-grain-label]').textContent = joined ? 'SUM(order_total) after the join' : 'Total at the order grain';
    demo.querySelector('[data-grain-total]').textContent = joined ? '$84' : '$42';
    demo.querySelector('[data-grain-result]').textContent = joined ? 'The order total is repeated on each line.' : 'Read one order-level record, before joining to line items.';
  })));
  const handoff = {
    intent: ['README.md / project intent', 'Build a batch-scoring pipeline', 'Score synthetic transactions and store one prediction per transaction ID.', 'The next session receives an explicit project goal.'],
    decision: ['specs/README.md / design decision', 'Use idempotent database writes', 'A replay can contain a transaction already stored. Use the transaction ID to prevent a second insert.', 'The next session receives the authored decision and its rationale.'],
    next: ['specs/README.md / next validation step', 'Replay a duplicate transaction', 'Compare persisted rows with unique transaction IDs after replay.', 'The next session receives a concrete validation step.']
  };
  document.querySelectorAll('[data-context-demo]').forEach(demo => demo.querySelectorAll('[data-context]').forEach(button => button.addEventListener('click', () => {
    demo.querySelectorAll('[data-context]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    const value = handoff[button.dataset.context]; ['file','title','body','consequence'].forEach((key,index) => { demo.querySelector('[data-context-' + key + ']').textContent = value[index]; });
  })));
  document.querySelectorAll('[data-replay-demo]').forEach(demo => {
    let arrivals = 1;
    const count = demo.querySelector('[data-arrival-count]'); const log = demo.querySelector('[data-replay-log]'); const duplicate = demo.querySelector('[data-duplicate-row]');
    demo.querySelector('[data-replay]').addEventListener('click', () => {
      arrivals += 1; count.textContent = String(arrivals); duplicate.hidden = false;
      log.textContent = 'tx_1042 already exists.\nDuplicate insert skipped.\nStored predictions: 1.';
    });
    demo.querySelector('[data-replay-reset]').addEventListener('click', () => {
      arrivals = 1; count.textContent = '1'; duplicate.hidden = true; log.textContent = 'tx_1042 inserted.\nStored predictions: 1.';
    });
  });
})();
