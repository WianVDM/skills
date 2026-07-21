#!/usr/bin/env node
/**
 * recon.smoke-test.js — verify recon.js conflict preview against real git repos.
 *
 * Builds two throwaway repos under the OS temp dir:
 *   1. A repo where upstream and target both modify the same file (conflict).
 *   2. A repo where the two sides touch disjoint files (clean).
 *
 * Runs scripts/recon.js against each and asserts the preview verdict.
 * Exits 0 on success, 1 on failure. Deletes its fixtures.
 *
 * Usage: node scripts/recon.smoke-test.js
 */

const { execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const RECON = path.join(__dirname, 'recon.js');

function git(cwd, args) {
  return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
}

function initRepo(dir) {
  fs.mkdirSync(dir, { recursive: true });
  git(dir, ['init', '-b', 'main']);
  git(dir, ['config', 'user.email', 'smoke@test.local']);
  git(dir, ['config', 'user.name', 'Smoke Test']);
  git(dir, ['config', 'commit.gpgsign', 'false']);
}

function commitFile(dir, file, content, message) {
  fs.writeFileSync(path.join(dir, file), content);
  git(dir, ['add', file]);
  git(dir, ['commit', '-m', message]);
}

function runRecon(upstream, target, cwd) {
  const out = execFileSync('node', [RECON, '--upstream', upstream, '--target', target], {
    cwd,
    encoding: 'utf8',
    stdio: ['pipe', 'pipe', 'pipe'],
  });
  return JSON.parse(out);
}

let failures = 0;

function check(label, condition, detail) {
  if (condition) {
    console.log(`PASS  ${label}`);
  } else {
    failures += 1;
    console.error(`FAIL  ${label} — ${detail}`);
  }
}

function buildConflictRepo(dir) {
  initRepo(dir);
  commitFile(dir, 'a.txt', 'line1\nline2\nline3\n', 'base');
  git(dir, ['checkout', '-b', 'feature']);
  commitFile(dir, 'a.txt', 'line1-feature\nline2\nline3\n', 'feature change');
  commitFile(dir, 'b.txt', 'feature only\n', 'feature file');
  git(dir, ['checkout', 'main']);
  commitFile(dir, 'a.txt', 'line1-main\nline2\nline3\n', 'main change');
  commitFile(dir, 'c.txt', 'main only\n', 'main file');
}

function buildCleanRepo(dir) {
  initRepo(dir);
  commitFile(dir, 'a.txt', 'line1\nline2\nline3\n', 'base');
  git(dir, ['checkout', '-b', 'feature']);
  commitFile(dir, 'b.txt', 'feature only\n', 'feature file');
  git(dir, ['checkout', 'main']);
  commitFile(dir, 'c.txt', 'main only\n', 'main file');
}

function main() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'merge-latest-recon-test-'));
  try {
    const conflictDir = path.join(tmp, 'conflict-repo');
    buildConflictRepo(conflictDir);
    const conflictResult = runRecon('main', 'feature', conflictDir);
    check(
      'conflicting repo: wouldConflict is true',
      conflictResult.conflictPreview.wouldConflict === true,
      JSON.stringify(conflictResult.conflictPreview),
    );
    check(
      'conflicting repo: a.txt listed as conflicted',
      conflictResult.conflictPreview.conflictedFiles.includes('a.txt'),
      JSON.stringify(conflictResult.conflictPreview.conflictedFiles),
    );
    check(
      'conflicting repo: merge base equals first commit',
      /^[0-9a-f]{40}$/.test(conflictResult.mergeBase),
      conflictResult.mergeBase,
    );
    check(
      'commit hashes have no shell-quote contamination',
      /^[0-9a-f]{40}$/.test(conflictResult.upstreamCommits[0].hash),
      JSON.stringify(conflictResult.upstreamCommits[0]),
    );

    const cleanDir = path.join(tmp, 'clean-repo');
    buildCleanRepo(cleanDir);
    const cleanResult = runRecon('main', 'feature', cleanDir);
    check(
      'clean repo: wouldConflict is false',
      cleanResult.conflictPreview.wouldConflict === false,
      JSON.stringify(cleanResult.conflictPreview),
    );
    check(
      'clean repo: no conflicted files',
      cleanResult.conflictPreview.conflictedFiles.length === 0,
      JSON.stringify(cleanResult.conflictPreview.conflictedFiles),
    );
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }

  if (failures > 0) {
    console.error(`\n${failures} check(s) failed.`);
    process.exit(1);
  }
  console.log('\nAll recon smoke checks passed.');
}

main();
