'use strict';

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');
const test = require('node:test');

const ROOT = path.resolve(__dirname, '..');
const ACTIVATE = path.join(ROOT, 'src', 'hooks', 'caveman-activate.js');
const TRACKER = path.join(ROOT, 'src', 'hooks', 'caveman-mode-tracker.js');

function fixture() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'caveman-math-'));
  fs.writeFileSync(
    path.join(dir, 'settings.json'),
    JSON.stringify({ statusLine: { type: 'command', command: 'true' } })
  );
  return dir;
}

function run(script, dir, options = {}) {
  return spawnSync(process.execPath, [script], {
    cwd: ROOT,
    encoding: 'utf8',
    input: options.input,
    env: {
      ...process.env,
      CLAUDE_CONFIG_DIR: dir,
      ...(options.env || {}),
    },
  });
}

test('source activation loads canonical base skill and filters inactive levels', () => {
  const dir = fixture();
  try {
    const result = run(ACTIVATE, dir, { env: { CAVEMAN_DEFAULT_MODE: 'full' } });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /Never trade accuracy or required reasoning/);
    assert.match(result.stdout, /No em dashes/);
    assert.match(result.stdout, /assistant openers/);
    assert.match(result.stdout, /\*\*full\*\*/);
    assert.doesNotMatch(result.stdout, /\*\*lite\*\*/);
    assert.equal(fs.readFileSync(path.join(dir, '.caveman-active'), 'utf8'), 'full');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('math default loads formula-first skill from canonical source', () => {
  const dir = fixture();
  try {
    const result = run(ACTIVATE, dir, { env: { CAVEMAN_DEFAULT_MODE: 'math' } });
    assert.equal(result.status, 0, result.stderr);
    assert.match(result.stdout, /CAVEMAN MATH ACTIVE/);
    assert.match(result.stdout, /Compress exposition, not reasoning/);
    assert.match(result.stdout, /Render mathematics with LaTeX/);
    assert.match(result.stdout, /No em dashes/);
    assert.equal(fs.readFileSync(path.join(dir, '.caveman-active'), 'utf8'), 'math');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('/caveman math persists and emits formula-first reinforcement', () => {
  const dir = fixture();
  try {
    const result = run(TRACKER, dir, {
      input: JSON.stringify({ prompt: '/caveman math' }),
    });
    assert.equal(result.status, 0, result.stderr);
    assert.equal(fs.readFileSync(path.join(dir, '.caveman-active'), 'utf8'), 'math');
    assert.match(result.stdout, /rendered LaTeX; define symbols; derive; no em dashes\/openers/);

    const next = run(TRACKER, dir, {
      input: JSON.stringify({ prompt: 'Why is simple harmonic motion sinusoidal?' }),
    });
    assert.match(next.stdout, /CAVEMAN MATH/);
    assert.match(next.stdout, /no em dashes\/openers/);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('/caveman-math activates and normal mode deactivates', () => {
  const dir = fixture();
  try {
    run(TRACKER, dir, { input: JSON.stringify({ prompt: '/caveman-math' }) });
    assert.equal(fs.readFileSync(path.join(dir, '.caveman-active'), 'utf8'), 'math');

    run(TRACKER, dir, { input: JSON.stringify({ prompt: 'normal mode' }) });
    assert.equal(fs.existsSync(path.join(dir, '.caveman-active')), false);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('formula-first phrase activates math mode', () => {
  const dir = fixture();
  try {
    run(TRACKER, dir, {
      input: JSON.stringify({ prompt: 'Use formula-first explanation for this derivation' }),
    });
    assert.equal(fs.readFileSync(path.join(dir, '.caveman-active'), 'utf8'), 'math');
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
