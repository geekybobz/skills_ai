#!/usr/bin/env node
// UserPromptSubmit hook: track mode and inject a compact persistence reminder.

const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');
const { getDefaultMode, safeWriteFlag, readFlag, VALID_MODES } = require('./caveman-config');

const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);
const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.caveman-active');

function removeFlag() {
  try { fs.unlinkSync(flagPath); } catch (_) {}
}

function parseMode(prompt) {
  const parts = prompt.split(/\s+/);
  const cmd = parts[0];
  const arg = parts[1] || '';

  if (cmd === '/caveman-commit') return 'commit';
  if (cmd === '/caveman-review') return 'review';
  if (cmd === '/caveman-compress' || cmd === '/caveman:caveman-compress') return 'compress';
  if (cmd === '/caveman-math' || cmd === '/caveman:caveman-math') return 'math';

  if (cmd === '/caveman' || cmd === '/caveman:caveman') {
    if (!arg) return getDefaultMode();
    if (arg === 'off' || arg === 'stop' || arg === 'disable') return 'off';
    if (arg === 'wenyan-full') return 'wenyan';
    if (VALID_MODES.includes(arg) && !INDEPENDENT_MODES.has(arg)) return arg;
    return null;
  }

  if (/\bnormal mode\b/i.test(prompt) ||
      /\b(stop|disable|deactivate|turn off)\b.*\bcaveman\b/i.test(prompt) ||
      /\bcaveman\b.*\b(stop|disable|deactivate|turn off)\b/i.test(prompt)) {
    return 'off';
  }

  if (/\bformula[- ]first\b/i.test(prompt) ||
      /\bless story\b/i.test(prompt) ||
      /\b(use|activate|enable|start|turn on)\b.*\b(math mode|caveman math)\b/i.test(prompt)) {
    return 'math';
  }

  if (/\b(activate|enable|turn on|start|talk like)\b.*\bcaveman\b/i.test(prompt) ||
      /\bcaveman\b.*\b(mode|activate|enable|turn on|start)\b/i.test(prompt)) {
    return getDefaultMode();
  }

  return null;
}

function reinforcement(mode) {
  if (mode === 'math') {
    return 'CAVEMAN MATH: formula first; define symbols; derive; LaTeX; verify on request.';
  }
  return `CAVEMAN (${mode}): terse; preserve technical terms; normal code/security.`;
}

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase();

    const statsMatch = /^\/caveman(?::caveman)?-stats(?:\s+(.*))?$/.exec(prompt);
    if (statsMatch) {
      const tailArgs = (statsMatch[1] || '').trim().split(/\s+/).filter(Boolean);
      try {
        const argv = [path.join(__dirname, 'caveman-stats.js')];
        if (data.transcript_path) argv.push('--session-file', data.transcript_path);
        if (tailArgs.includes('--share')) argv.push('--share');
        if (tailArgs.includes('--all')) argv.push('--all');
        const sinceIdx = tailArgs.indexOf('--since');
        if (sinceIdx !== -1 && tailArgs[sinceIdx + 1]) {
          argv.push('--since', tailArgs[sinceIdx + 1]);
        }
        const out = execFileSync(process.execPath, argv, { encoding: 'utf8', timeout: 5000 });
        process.stdout.write(JSON.stringify({ decision: 'block', reason: out.trim() }));
      } catch (_) {
        process.stdout.write(JSON.stringify({
          decision: 'block',
          reason: 'caveman-stats: could not run stats script.\nTry manually: node hooks/caveman-stats.js'
        }));
      }
      return;
    }

    const change = parseMode(prompt);
    if (change === 'off') removeFlag();
    else if (change) safeWriteFlag(flagPath, change);

    const activeMode = readFlag(flagPath);
    if (activeMode && !INDEPENDENT_MODES.has(activeMode)) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext: reinforcement(activeMode),
        }
      }));
    }
  } catch (_) {}
});
