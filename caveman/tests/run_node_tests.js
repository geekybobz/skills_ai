#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const installerDir = path.join(__dirname, 'installer');
const files = fs.readdirSync(installerDir)
  .filter(name => name.endsWith('.test.mjs'))
  .sort()
  .map(name => path.join(installerDir, name));

files.push(path.join(__dirname, 'test_caveman_math.js'));

for (const file of files) {
  const relative = path.relative(root, file);
  process.stdout.write(`\n== ${relative} ==\n`);
  const result = spawnSync(process.execPath, ['--test', file], {
    cwd: root,
    stdio: 'inherit',
  });
  if (result.status !== 0) process.exit(result.status || 1);
}
