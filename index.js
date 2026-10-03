#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

let binaryPath;

if (process.platform === 'linux') {
  binaryPath = path.join(
    __dirname,
    'bin',
    'linux-x64',
    'git-version-sync'
  );
} else if (process.platform === 'win32') {
  binaryPath = path.join(
    __dirname,
    'bin',
    'win-x64',
    'git-version-sync.exe'
  );
} else if (process.platform === 'darwin') {
  binaryPath = path.join(
    __dirname,
    'bin',
    'macos-arm64',
    'git-version-sync'
  );
} else {
  console.error(
    `[git-version-sync] Unsupported platform: ${process.platform}`
  );
  process.exit(1);
}

const child = spawn(binaryPath, process.argv.slice(2), {
  stdio: 'inherit'
});

child.on('error', (err) => {
  console.error(
    '[git-version-sync] Failed to start:',
    err.message
  );
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code ?? 1);
});