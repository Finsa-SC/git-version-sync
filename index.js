#!/usr/bin/env node

const { spawn } = require('child_process');

const child = spawn('git-version-sync', process.argv.slice(2), {
  stdio: 'inherit',
  shell: true
});

child.on('error', (err) => {
  if (err.code === 'ENOENT') {
    console.error('[git-version-sync] Error: Command "git-version-sync" tidak ditemukan.');
    console.error('Pastikan Python (>=3.10) dan pip terinstall dengan benar di sistem kamu.');
  } else {
    console.error('[git-version-sync] Error:', err.message);
  }
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});