/* Local, labeled workflow illustrations. No production services connected. */
(() => {
  'use strict';
  const steps = {
    restore: ['01 / Copy + restore', 'The requested database copy is restored into the target environment. The workflow accounts for Contained availability groups.'],
    security: ['02 / Security setup', 'Security setup is part of the refresh workflow, rather than another task to coordinate after a restore.'],
    recovery: ['03 / Recovery mode', 'The workflow configures full recovery mode as part of preparing the target database.'],
    cdc: ['04 / Enable CDC', 'Change data capture is enabled during setup so the refreshed database has the required capture configuration.'],
    listener: ['05 / Validate listener', 'Listener validation checks the expected connection path. The people operating the workflow still own exceptions and follow-up.']
  };
  document.querySelectorAll('[data-refresh-demo]').forEach(demo => {
    demo.querySelectorAll('[data-refresh-mode]').forEach(button => button.addEventListener('click', () => {
      const automated = button.dataset.refreshMode === 'automated';
      demo.dataset.mode = automated ? 'automated' : 'manual';
      demo.querySelectorAll('[data-refresh-mode]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
      demo.querySelector('[data-mode-title]').textContent = automated ? 'One orchestrated workflow' : 'Repeated manual coordination';
      demo.querySelector('[data-mode-caption]').textContent = automated ? 'Azure DevOps coordinates the setup stages.' : 'Restore and setup stages need someone to coordinate them.';
    }));
    demo.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => {
      demo.querySelectorAll('[data-step]').forEach(other => { other.classList.toggle('is-active', other === button); other.setAttribute('aria-pressed', String(other === button)); });
      const value = steps[button.dataset.step];
      demo.querySelector('[data-stage-label]').textContent = value[0];
      demo.querySelector('[data-stage-description]').textContent = value[1];
    }));
  });
  const handoff = {
    intent: ['README.md / product intent', 'What are we trying to build?', 'Keep a reviewer-oriented explanation of the product and its purpose next to the source.', 'The next session can start with the intended outcome instead of guessing from a diff.'],
    decision: ['specs/README.md / authored decision', 'Why this approach?', 'Example: Keep duplicate writes harmless. A replay can contain a transaction we already stored.', 'The developer or agent writes the decision. The tool does not reconstruct its meaning from a full chat history.'],
    next: ['specs/README.md / next step', 'Where should the next session begin?', 'Example: Replay a duplicate and compare the persisted row count with the unique transaction count.', 'A concrete next check is easier to act on than a summary that only says work is in progress.']
  };
  document.querySelectorAll('[data-context-demo]').forEach(demo => demo.querySelectorAll('[data-context]').forEach(button => button.addEventListener('click', () => {
    demo.querySelectorAll('[data-context]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    const value = handoff[button.dataset.context];
    ['file','title','body','consequence'].forEach((key,index) => { demo.querySelector('[data-context-' + key + ']').textContent = value[index]; });
  })));
  document.querySelectorAll('[data-replay-demo]').forEach(demo => {
    let arrivals = 1;
    const count = demo.querySelector('[data-arrival-count]');
    const log = demo.querySelector('[data-replay-log]');
    demo.querySelector('[data-replay]').addEventListener('click', () => { arrivals += 1; count.textContent = String(arrivals); log.textContent = 'tx_1042 already exists.\nDuplicate insert skipped.\nStored predictions: 1.'; });
    demo.querySelector('[data-replay-reset]').addEventListener('click', () => { arrivals = 1; count.textContent = '1'; log.textContent = 'tx_1042 inserted.\nStored predictions: 1.'; });
  });
})();
