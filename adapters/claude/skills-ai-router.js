#!/usr/bin/env node
// Claude UserPromptSubmit adapter for the shared Skills AI runtime.

'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');


function argument(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}


function stripFrontmatter(content) {
  return content.replace(/^---[\s\S]*?---\s*/, '');
}


function contextText(decision, root) {
  const context = decision.context;
  const lines = [
    'Skills AI shared response context:',
    `operation=${context.operation}`,
    `domain=${context.domain}`,
    `requested_access=${context.requested_access}`,
    `voice=${context.output.voice}`,
    `shape=${context.output.shape}`,
    `contract=${context.response_contract.join(' ')}`,
  ];
  if (decision.result !== 'MATCH') {
    lines.push('No local skill matched. Continue normally using the response context above.');
    return lines.join('\n');
  }
  const rootPath = path.resolve(root);
  const skillPath = path.resolve(rootPath, decision.skill.path);
  if (skillPath !== rootPath && !skillPath.startsWith(rootPath + path.sep)) {
    throw new Error('selected skill escaped the Skills AI root');
  }
  const body = stripFrontmatter(fs.readFileSync(skillPath, 'utf8'));
  lines.push(`Selected local skill: ${decision.skill.id}`);
  lines.push(body);
  return lines.join('\n\n');
}


let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input || '{}');
    const prompt = typeof data.prompt === 'string' ? data.prompt : '';
    if (!prompt.trim()) return;
    const root = argument('--root') || process.env.SKILLS_AI_ROOT;
    if (!root) throw new Error('Skills AI root is required');
    const python = process.env.SKILLS_AI_PYTHON || 'python3';
    const router = path.join(root, 'scripts', 'route_skill.py');
    const output = execFileSync(python, [router], {
      input: JSON.stringify({ query: prompt }),
      encoding: 'utf8',
      timeout: 5000,
      maxBuffer: 1024 * 1024,
      env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
    });
    const decision = JSON.parse(output);
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'UserPromptSubmit',
        additionalContext: contextText(decision, root),
      },
    }));
  } catch (_) {
    // Fail open. A router or adapter error must never block the user's task.
  }
});


module.exports = { contextText, stripFrontmatter };
