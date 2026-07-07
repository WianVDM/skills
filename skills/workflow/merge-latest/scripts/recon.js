#!/usr/bin/env node
/**
 * recon.js — gather merge context without modifying the working tree.
 *
 * Uses resolved remote refs so the preview reflects the latest fetched state.
 *
 * Usage:
 *   node recon.js --upstream origin/development --target my-branch [--remote origin]
 *
 * Outputs JSON to stdout with merge metadata and a conflict preview.
 */

const { execSync } = require('child_process');

function quote(str) {
  return '"' + String(str).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
}

function run(cmd, opts = {}) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], ...opts }).trim();
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];
    result[key] = value;
  }
  return result;
}

function resolveBranches(args) {
  if (!args.upstream) {
    throw new Error('--upstream is required');
  }
  const upstream = args.upstream;
  const target = args.target || run('git rev-parse --abbrev-ref HEAD');
  const remote = args.remote || detectRemote();
  return { upstream, target, remote };
}

function detectRemote() {
  const remotes = run('git remote').split('\n').filter(Boolean);
  if (remotes.includes('origin')) return 'origin';
  if (remotes.length === 1) return remotes[0];
  return null;
}

function getCommits(base, head) {
  const output = run(`git log --format='%H%x09%s' --first-parent ${quote(base)}..${quote(head)}`);
  if (!output) return [];
  return output.split('\n').map(line => {
    const [hash, ...subjectParts] = line.split('\t');
    return { hash, subject: subjectParts.join('\t') };
  });
}

function getFiles(base, head) {
  const output = run(`git diff --name-only --merge-base ${quote(base)} ${quote(head)}`);
  if (!output) return [];
  return output.split('\n').filter(Boolean);
}

function getConflictPreview(upstream, target) {
  const base = run(`git merge-base ${quote(upstream)} ${quote(target)}`);
  let treeOutput;
  try {
    treeOutput = run(`git merge-tree --write-tree --no-messages ${quote(base)} ${quote(upstream)} ${quote(target)}`);
  } catch (err) {
    // Older git or other failure; fall back to traditional merge-tree.
    treeOutput = run(`git merge-tree ${quote(base)} ${quote(upstream)} ${quote(target)}`);
  }

  const lines = treeOutput.split('\n').filter(Boolean);
  const conflictedFiles = [];

  for (const line of lines) {
    // Modern git merge-tree --write-tree emits lines like:
    //   conflict <path>
    if (line.startsWith('conflict ')) {
      conflictedFiles.push(line.replace('conflict ', ''));
      continue;
    }
    // Traditional merge-tree emits conflict markers in diff hunks.
    // We detect the file path from lines like "+++ <path>".
    const match = line.match(/^\+\+\+ ([^\s]+)/);
    if (match && treeOutput.includes(`<<<<<<< ${match[1]}`)) {
      conflictedFiles.push(match[1]);
    }
  }

  return {
    mergeBase: base,
    wouldConflict: conflictedFiles.length > 0,
    conflictedFiles: [...new Set(conflictedFiles)],
  };
}

function main() {
  const args = parseArgs();
  const { upstream, target, remote } = resolveBranches(args);

  try {
    const preview = getConflictPreview(upstream, target);
    const upstreamCommits = getCommits(preview.mergeBase, upstream);
    const targetCommits = getCommits(preview.mergeBase, target);
    const upstreamFiles = getFiles(preview.mergeBase, upstream);
    const targetFiles = getFiles(preview.mergeBase, target);

    const result = {
      upstream,
      target,
      remote,
      upstreamCommit: run(`git rev-parse ${upstream}`),
      targetCommit: run(`git rev-parse ${target}`),
      mergeBase: preview.mergeBase,
      upstreamCommits,
      targetCommits,
      upstreamFiles,
      targetFiles,
      conflictPreview: {
        wouldConflict: preview.wouldConflict,
        conflictedFiles: preview.conflictedFiles,
      },
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('recon failed:', err.stderr || err.message);
    process.exit(1);
  }
}

main();
