#!/usr/bin/env node
// Claude lifecycle context adapter for the shared Skills AI runtime.
// skills-ai-managed: claude-context

'use strict';

const path = require('path');
const { spawnSync } = require('child_process');


const MAX_HOOK_INPUT_BYTES = 1024 * 1024;
const MAX_ROUTER_OUTPUT_BYTES = 1024 * 1024;
const DEFAULT_CHILD_TIMEOUT_MS = 1000;
const DEFAULT_ADAPTER_TIMEOUT_MS = 2500;
// Reserved inside the whole-run budget for reading the shared core and writing the reply after the child returns.
const DEADLINE_RESERVE_MS = 250;


function argument(name) {
  const index = process.argv.indexOf(name);
  return index >= 0 ? process.argv[index + 1] : null;
}


function elapsedMs(started) {
  return Number(process.hrtime.bigint() - started) / 1e6;
}


function positiveInteger(value, fallback) {
  const parsed = Number.parseInt(value || '', 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}


class AdapterError extends Error {
  constructor(reason, message) {
    super(message || reason);
    this.reason = reason;
  }
}


function diagnostic(reason, started) {
  const elapsed = Math.round(elapsedMs(started));
  process.stderr.write(`[skills-ai-context] fail-open adapter=claude reason=${reason} elapsed_ms=${elapsed}\n`);
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


function terminateGroup(pid) {
  // The child leads its own process group, so this also reaps anything an
  // interpreter shim left behind. ESRCH means the group is already gone.
  if (!pid) return;
  try {
    process.kill(-pid, 'SIGKILL');
  } catch (error) {
    if (!error || error.code !== 'ESRCH') throw error;
  }
}


function runRouter(python, args, request, timeout) {
  const result = spawnSync(python, args, {
    input: request,
    encoding: 'utf8',
    timeout,
    killSignal: 'SIGTERM',
    maxBuffer: MAX_ROUTER_OUTPUT_BYTES,
    stdio: ['pipe', 'pipe', 'pipe'],
    detached: true,
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: '1' },
  });
  if (result.error) {
    terminateGroup(result.pid);
    throw result.error;
  }
  if (result.status !== 0) {
    terminateGroup(result.pid);
    throw new AdapterError('ADAPTER_ERROR', 'the shared router exited without a decision');
  }
  return result.stdout;
}


function contextText(decision, root) {
  if (decision.schema !== 'skills-ai/context/1' || typeof decision.additional_context !== 'string' ||
      Buffer.byteLength(decision.additional_context) > 65536) {
    throw new AdapterError('ADAPTER_UNSUPPORTED_PROTOCOL');
  }
  return decision.additional_context;
}

function runAdapter(input, started, budgetMs) {
  const budget = positiveInteger(budgetMs, DEFAULT_ADAPTER_TIMEOUT_MS);
  const remaining = () => budget - elapsedMs(started);
  const data = parseHookInput(input);
  const event = data.hook_event_name || 'UserPromptSubmit';
  if (!['SessionStart', 'UserPromptSubmit'].includes(event)) return;
  if (data.session_id !== undefined && (typeof data.session_id !== 'string' || !/^[A-Za-z0-9_-]{1,128}$/.test(data.session_id))) throw new AdapterError('ADAPTER_INVALID_INPUT');
  const root = argument('--root') || process.env.SKILLS_AI_ROOT;
  if (!root) throw new Error('Skills AI root is required');
  const python = process.env.SKILLS_AI_PYTHON || 'python3';
  const router = path.join(root, 'scripts', 'orchestrate.py');
  // The child budget is whatever is left of the whole-run budget after the
  // reserve, so slow host input shortens the child instead of overrunning the
  // hook deadline. A blocking child cannot be interrupted by a JS timer.
  const configuredChildTimeout = positiveInteger(
    process.env.SKILLS_AI_ROUTER_TIMEOUT_MS,
    DEFAULT_CHILD_TIMEOUT_MS,
  );
  const childBudget = Math.floor(remaining() - DEADLINE_RESERVE_MS);
  if (childBudget < 1) {
    throw new AdapterError('ADAPTER_DEADLINE_EXCEEDED', 'no run budget remained for the shared router');
  }
  const childTimeout = Math.min(configuredChildTimeout, childBudget);
  const projectRoot = typeof data.cwd === 'string' && path.isAbsolute(data.cwd) ? data.cwd : null;
  const args = [router, 'context', '--format', 'json', '--defer-marker', '--delivery', event === 'SessionStart' ? 'bootstrap' : 'continuation',
    ...(projectRoot ? ['--project-root', projectRoot] : []),
    ...(data.session_id ? ['--session', data.session_id] : [])];
  // The context command never receives task prose or interprets user controls.
  const output = runRouter(python, args, '', childTimeout);
  const decision = JSON.parse(output);
  const additionalContext = contextText(decision, root);
  // A stalled core read cannot be pre-empted, so re-check the budget
  // rather than injecting context the host has already stopped waiting for.
  if (remaining() <= 0) {
    throw new AdapterError('ADAPTER_DEADLINE_EXCEEDED', 'run budget expired before the reply was written');
  }
  if (!additionalContext) return;
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: event,
      additionalContext,
    },
  }), error => {
    // A failed or cancelled write must not suppress the next delivery. This
    // acknowledges emitted output only; the host still owns context recovery.
    if (error || !data.session_id || remaining() < 1) return;
    try {
      runRouter(python, [router, 'ack-context', '--session', data.session_id,
        '--revision', JSON.stringify(decision.revision)], '', Math.max(1, Math.floor(remaining())));
    } catch (failure) {
      diagnostic('CONTEXT_ACK_FAILED', started);
    }
  });
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

  // One budget covers the whole run. The timer can only fire while the event
  // loop is free, so it bounds the input phase; runAdapter enforces the same
  // deadline around its blocking child and skill-body read.
  const watchdog = setTimeout(() => failOpen('ADAPTER_INPUT_TIMEOUT'), adapterTimeout);
  watchdog.unref();

  // Host cancellation is only observable while the event loop is free, which is
  // the input phase. Once the child is running it enforces its own deadline.
  for (const signal of ['SIGTERM', 'SIGINT']) {
    process.on(signal, () => failOpen('ADAPTER_CANCELLED'));
  }

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
      runAdapter(input, started, adapterTimeout);
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
  terminateGroup,
};
