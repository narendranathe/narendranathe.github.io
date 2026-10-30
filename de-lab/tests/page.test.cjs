const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '../..');
const folder = path.join(root, 'de-lab');
const html = fs.readFileSync(path.join(folder, 'index.html'), 'utf8');
const js = fs.readFileSync(path.join(folder, 'app.js'), 'utf8');
const css = fs.readFileSync(path.join(folder, 'styles.css'), 'utf8');

test('all on-page anchor links have real targets', () => {
  const ids = [...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]);
  assert.equal(ids.length, new Set(ids).size, 'IDs must be unique');
  for (const [, target] of html.matchAll(/href="#([^"]+)"/g)) {
    assert.ok(ids.includes(target), 'Missing anchor: #' + target);
  }
});

test('all static asset and internal page paths exist', () => {
  const attrs = [...html.matchAll(/\b(?:href|src)="([^"]+)"/g)].map(m => m[1]);
  for (const url of attrs) {
    if (/^(?:https?:|mailto:|#|data:)/.test(url)) continue;
    const location = decodeURIComponent(url.split(/[?#]/)[0]);
    assert.ok(fs.existsSync(path.resolve(folder, location)), 'Missing local file: ' + url);
  }
});

test('accessible tabs, labels, and feedback regions are present', () => {
  assert.match(html, /role="tablist"/);
  assert.equal((html.match(/role="tab"/g) || []).length, 2);
  assert.equal((html.match(/role="tabpanel"/g) || []).length, 2);
  assert.match(html, /aria-live="polite"/);
  assert.match(html, /href="#main"[^>]*>Skip to content/);
  assert.match(html, /for="event-volume"/);
  assert.match(css, /prefers-reduced-motion:reduce/);
});

test('two simulators remain distinct and are never presented as production telemetry', () => {
  assert.match(html, /SIMULATOR \/ 001/);
  assert.match(html, /SIMULATOR \/ 002/);
  assert.match(html, /SYNTHETIC MODEL/);
  assert.match(html, /Production outcomes/);
  assert.match(html, /NOT A BENCHMARK/);
  assert.match(html, /de-lab\//);
});

test('browser controls avoid HTML injection and persistence', () => {
  assert.doesNotMatch(js, /\.innerHTML\s*=/);
  assert.doesNotMatch(js, /\b(?:localStorage|sessionStorage|fetch)\s*\(/);
  assert.match(js, /createTextNode/);
  assert.match(js, /setAttribute\('aria-selected'/);
});

test('site has unique metadata and isolated local scripts', () => {
  assert.match(html, /<link rel="canonical" href="https:\/\/narendranathe\.github\.io\/de-lab\/">/);
  assert.match(html, /<script src="\.\/core\.js" defer><\/script>/);
  assert.match(html, /<script src="\.\/app\.js" defer><\/script>/);
  assert.match(html, /<link rel="stylesheet" href="\.\/styles\.css">/);
  assert.match(html, /<meta name="viewport"/);
});
