#!/usr/bin/env node
// Claude Code SessionStart activation hook.

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag } = require('./caveman-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.caveman-active');
const settingsPath = path.join(claudeDir, 'settings.json');
const mode = getDefaultMode();

if (mode === 'off') {
  try { fs.unlinkSync(flagPath); } catch (_) {}
  process.stdout.write('OK');
  process.exit(0);
}

safeWriteFlag(flagPath, mode);

const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);

if (INDEPENDENT_MODES.has(mode)) {
  process.stdout.write(
    'CAVEMAN MODE ACTIVE - level: ' + mode +
    '. Behavior defined by /caveman-' + mode + ' skill.'
  );
  process.exit(0);
}

function readSkillBody(name) {
  // Source/plugin layout: <root>/src/hooks -> <root>/skills.
  // Standalone layout: <config>/hooks -> <config>/skills.
  const candidates = [
    path.join(__dirname, '..', '..', 'skills', name, 'SKILL.md'),
    path.join(__dirname, '..', 'skills', name, 'SKILL.md'),
  ];
  for (const candidate of candidates) {
    try {
      const raw = fs.readFileSync(candidate, 'utf8');
      return raw.replace(/^---[\s\S]*?---\s*/, '');
    } catch (_) {}
  }
  return '';
}

function filterBaseSkill(body, activeMode) {
  const modeLabel = activeMode === 'wenyan' ? 'wenyan-full' : activeMode;
  return body.split('\n').reduce((lines, line) => {
    const row = line.match(/^\|\s*\*\*(\S+?)\*\*\s*\|/);
    if (!row || row[1] === modeLabel) lines.push(line);
    return lines;
  }, []).join('\n');
}

function fallbackBase(activeMode) {
  const definitions = {
    lite: 'Remove filler and hedging. Keep full sentences and articles.',
    full: 'Drop articles. Fragments and short exact words allowed.',
    ultra: 'Use standard abbreviations and arrows. Never abbreviate identifiers or errors.',
    'wenyan-lite': 'Use light classical Chinese with readable grammar.',
    wenyan: 'Use maximum classical terseness while preserving exact meaning.',
    'wenyan-full': 'Use maximum classical terseness while preserving exact meaning.',
    'wenyan-ultra': 'Use extreme classical compression while preserving exact meaning.',
  };
  return [
    'Respond terse like smart caveman. Preserve all technical substance.',
    definitions[activeMode] || definitions.full,
    'Keep code, commands, paths, URLs, symbols, and quoted errors exact.',
    'Use normal prose for security, irreversible actions, or ambiguous step order.',
    'Persist until "stop caveman" or "normal mode".',
  ].join('\n');
}

function fallbackMath() {
  return [
    'Formula-first mathematical mode.',
    'Answer directly; define symbols; state governing equation; derive step by step.',
    'Use rendered LaTeX. Let equations carry argument; keep connective prose short.',
    'Give insight after derivation. Verify analytically first; use code only when requested.',
    'State assumptions and whether result is exact, approximate, restricted, or heuristic.',
  ].join('\n');
}

let output;
if (mode === 'math') {
  const body = readSkillBody('caveman-math') || fallbackMath();
  output = 'CAVEMAN MATH ACTIVE\n\n' + body;
} else {
  const modeLabel = mode === 'wenyan' ? 'wenyan-full' : mode;
  const body = readSkillBody('caveman');
  output = 'CAVEMAN MODE ACTIVE - level: ' + modeLabel + '\n\n' +
    (body ? filterBaseSkill(body, mode) : fallbackBase(mode));
}

// Plugin installs do not always configure a statusline. Keep the setup notice
// short and only emit it when no statusLine exists.
try {
  let hasStatusline = false;
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    hasStatusline = Boolean(settings.statusLine);
  }
  if (!hasStatusline) {
    const isWindows = process.platform === 'win32';
    const scriptName = isWindows ? 'caveman-statusline.ps1' : 'caveman-statusline.sh';
    const scriptPath = path.join(__dirname, scriptName);
    const command = isWindows
      ? `powershell -ExecutionPolicy Bypass -File "${scriptPath}"`
      : `bash "${scriptPath}"`;
    output += '\n\nSTATUSLINE SETUP NEEDED: add ' +
      JSON.stringify({ statusLine: { type: 'command', command } }) +
      ' to ' + settingsPath + '.';
  }
} catch (_) {}

process.stdout.write(output);
