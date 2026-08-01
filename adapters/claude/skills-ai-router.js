#!/usr/bin/env node
// Claude UserPromptSubmit adapter for the shared Skills AI runtime.
// skills-ai-managed: claude-router

'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');


const MAX_HOOK_INPUT_BYTES = 1024 * 1024;
const MAX_ROUTER_OUTPUT_BYTES = 1024 * 1024;
const DEFAULT_CHILD_TIMEOUT_MS = 1000;
const DEFAULT_ADAPTER_TIMEOUT_MS = 2500;


function argument(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}


function positiveInteger(value, fallback) {
  const parsed = Number.parseInt(value || '', 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}


function stripFrontmatter(content) {
  return content.replace(/^---[\s\S]*?---\s*/, '');
}


class AdapterError extends Error {
  constructor(reason, message) {
    super(message || reason);
    this.reason = reason;
  }
}


function diagnostic(reason, started) {
  const elapsed = Math.round(Number(process.hrtime.bigint() - started) / 1e6);
  process.stderr.write(`[skills-ai-router] fail-open adapter=claude reason=${reason} elapsed_ms=${elapsed}\n`);
}


function classifyError(error) {
  // An explicitly tagged adapter failure keeps its own reason so that a broken
  // hook payload is never reported as a shared-router output failure.
  if (error && typeof error.reason === 'string') return error.reason;
  if (error && (error.code === 'ETIMEDOUT' || error.signal === 'SIGTERM' || error.killed)) {
    return 'ADAPTER_TIMEOUT';
  }
  if (error instanceof SyntaxError) return 'ROUTER_INVALID_OUTPUT';
  return 'ADAPTER_ERROR';
}


function parseHookInput(input) {
  try {
    return JSON.parse(input || '{}');
  } catch (error) {
    throw new AdapterError('ADAPTER_INVALID_INPUT', 'hook payload is not one JSON object');
  }
}


function contextText(decision, root) {
  const context = decision.context;
  const lines = [
    'Skills AI shared response context:',
    `operation=${context.operation}`,
    `domain=${context.domain}`,
    `requested_access=${context.requested_access}`,
    `interaction=${context.interaction.mode}`,
    `interaction_reason=${context.interaction.reason}`,
    `voice=${context.output.voice}`,
    `shape=${context.output.shape}`,
    `contract=${context.response_contract.join(' ')}`,
  ];
  if (context.skills_ai_change_boundary) {
    const boundary = context.skills_ai_change_boundary;
    lines.push(`Skills AI change boundary: ${boundary.rule}`);
    lines.push(`Request generator: ${boundary.request_command}`);
    lines.push(`Maintenance workspace: ${boundary.maintenance_workspace}`);
  }
  if (decision.registry) {
    const registry = decision.registry;
    lines.push(`Live Skills AI registry source: ${registry.source_hash.slice(0, 12)}`);
    for (const state of ['active', 'manual', 'off']) {
      const skills = registry.routes[state] || [];
      lines.push(`${state} skills (${skills.length}): ${skills.join(', ') || 'none'}`);
    }
    lines.push(registry.hidden_policy);
    lines.push('Answer from this live metadata. Do not substitute remembered skill names or load skill bodies.');
    return lines.join('\n');
  }
  if (decision.result !== 'MATCH') {
    lines.push('No local skill matched. Continue normally using the response context above.');
    return lines.join('\n');
  }
  const rootPath = fs.realpathSync(root);
  const requestedSkillPath = path.resolve(rootPath, decision.skill.path);
  if (requestedSkillPath !== rootPath && !requestedSkillPath.startsWith(rootPath + path.sep)) {
    throw new Error('selected skill escaped the Skills AI root');
  }
  const skillPath = fs.realpathSync(requestedSkillPath);
  if (skillPath !== rootPath && !skillPath.startsWith(rootPath + path.sep)) {
    throw new Error('selected skill escaped the Skills AI root through a symlink');
  }
  const body = stripFrontmatter(fs.readFileSync(skillPath, 'utf8'));
  // The context header stays one key per line on every path; only the skill
  // body is separated by a blank line.
  return `${lines.join('\n')}\n\nSelected local skill: ${decision.skill.id}\n\n${body}`;
}


function runAdapter(input, started) {
  const data = parseHookInput(input);
  const prompt = typeof data.prompt === 'string' ? data.prompt : '';
  if (!prompt.trim()) return;
  const root = argument('--root') || process.env.SKILLS_AI_ROOT;
  if (!root) throw new Error('Skills AI root is required');
  const python = process.env.SKILLS_AI_PYTHON || 'python3';
  const router = path.join(root, 'scripts', 'route_skill.py');
  const childTimeout = positiveInteger(process.env.SKILLS_AI_ROUTER_TIMEOUT_MS, DEFAULT_CHILD_TIMEOUT_MS);
  const request = JSON.stringify({
    protocol: 'skills-ai/1',
    client: 'claude',
    query: prompt,
  }) + '\n';
  const output = execFileSync(python, [router], {
    input: request,
    encoding: 'utf8',
    timeout: childTimeout,
    killSignal: 'SIGTERM',
    maxBuffer: MAX_ROUTER_OUTPUT_BYTES,
    stdio: ['pipe', 'pipe', 'pipe'],
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  const decision = JSON.parse(output);
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: 'UserPromptSubmit',
      additionalContext: contextText(decision, root),
    },
  }));
}


if (require.main === module) {
  const started = process.hrtime.bigint();
  const adapterTimeout = positiveInteger(process.env.SKILLS_AI_ADAPTER_TIMEOUT_MS, DEFAULT_ADAPTER_TIMEOUT_MS);
  let input = '';
  let inputBytes = 0;
  let finished = false;

  const failOpen = reason => {
    if (finished) return;
    finished = true;
    diagnostic(reason, started);
    process.stdin.destroy();
    process.exit(0);
  };

  const watchdog = setTimeout(() => failOpen('ADAPTER_INPUT_TIMEOUT'), adapterTimeout);
  watchdog.unref();

  process.stdin.on('data', chunk => {
    if (finished) return;
    inputBytes += Buffer.byteLength(chunk);
    if (inputBytes > MAX_HOOK_INPUT_BYTES) {
      failOpen('ADAPTER_INPUT_TOO_LARGE');
      return;
    }
    input += chunk;
  });
  process.stdin.on('end', () => {
    if (finished) return;
    clearTimeout(watchdog);
    try {
      runAdapter(input, started);
      finished = true;
    } catch (error) {
      finished = true;
      diagnostic(classifyError(error), started);
    }
  });
  process.stdin.on('error', () => failOpen('ADAPTER_INPUT_ERROR'));
}


module.exports = {
  AdapterError,
  classifyError,
  contextText,
  parseHookInput,
  positiveInteger,
  runAdapter,
  stripFrontmatter,
};
