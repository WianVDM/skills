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
 *
 * Conflict preview requires git >= 2.38 (two-commit `git merge-tree --write-tree`
 * form). On older git the preview degrades explicitly: `status: "degraded"`,
 * `wouldConflict: null`. Callers must treat a degraded preview as "conflicts
 * possible" and use no-commit mode.
 */

const { execFileSync } = require('child_process');

function git(args, opts = {}) {
  return execFileSync('git', args, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], ...opts }).trim();
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
  const target = args.target || git(['rev-parse', '--abbrev-ref', 'HEAD']);
  const remote = args.remote || detectRemote();
  return { upstream, target, remote };
}

function detectRemote() {
  const remotes = git(['remote']).split('\n').filter(Boolean);
  if (remotes.includes('origin')) return 'origin';
  if (remotes.length === 1) return remotes[0];
  return null;
}

function getCommits(base, head) {
  const output = git(['log', '--format=%H%x09%s', '--first-parent', `${base}..${head}`]);
  if (!output) return [];
  return output.split('\n').map(line => {
    const [hash, ...subjectParts] = line.split('\t');
    return { hash, subject: subjectParts.join('\t') };
  });
}

function getFiles(base, head) {
  const output = git(['diff', '--name-only', '--merge-base', base, head]);
  if (!output) return [];
  return output.split('\n').filter(Boolean);
}

/**
 * Conflict preview via `git merge-tree --write-tree --no-messages --name-only
 * <upstream> <target>` (git >= 2.38).
 *
 * Exit 0: clean merge, stdout is the would-be tree OID.
 * Exit 1: conflicts, stdout is the tree OID followed by conflicted file paths.
 * Exit 129 (usage error) or other spawn failure: git is too old or the form is
 * unsupported — degrade explicitly instead of guessing.
 */
function getConflictPreview(upstream, target) {
  const base = git(['merge-base', upstream, target]);
  const args = ['merge-tree', '--write-tree', '--no-messages', '--name-only', upstream, target];
  try {
    git(args);
    return { mergeBase: base, status: 'clean', wouldConflict: false, conflictedFiles: [] };
  } catch (err) {
    if (err.status === 1) {
      const lines = String(err.stdout || '').split('\n').map(l => l.trim()).filter(Boolean);
      // First line is the tree OID; the rest are conflicted file paths.
      const conflictedFiles = lines.slice(1);
      return {
        mergeBase: base,
        status: 'conflicts',
        wouldConflict: true,
        conflictedFiles: [...new Set(conflictedFiles)],
      };
    }
    if (err.status === 129 || err.code === 'ENOENT') {
      return {
        mergeBase: base,
        status: 'degraded',
        degradedReason: 'conflict preview requires git >= 2.38 (merge-tree --write-tree two-commit form)',
        wouldConflict: null,
        conflictedFiles: [],
      };
    }
    throw err;
  }
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
      upstreamCommit: git(['rev-parse', upstream]),
      targetCommit: git(['rev-parse', target]),
      mergeBase: preview.mergeBase,
      upstreamCommits,
      targetCommits,
      upstreamFiles,
      targetFiles,
      conflictPreview: {
        status: preview.status,
        degradedReason: preview.degradedReason,
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
