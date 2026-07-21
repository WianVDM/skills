#!/usr/bin/env node
/**
 * change-summary.js — deterministic extraction for the pre-merge brief.
 *
 * Pulls the raw material for timelined change summaries out of git:
 * per-side commit timelines since merge-base, per-side file lists, the
 * file/directory overlap matrix, hotspot ranking, and UI-path signals.
 * No judgment lives here; `change-summarizer` turns this into narrative
 * and risk assessment.
 *
 * Usage:
 *   node change-summary.js --upstream origin/development --target my-branch
 *
 * Outputs JSON to stdout.
 */

const { execFileSync } = require('child_process');

const UI_PATH_PATTERN = /\.(css|scss|sass|less|styl|tsx|jsx|vue|svelte|html|storybook\.[jt]sx?)$|(^|\/)(styles?|theme|components?|pages?|views?|layouts?|ui)(\/|\.)/i;

function git(args, opts = {}) {
  return execFileSync('git', args, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], ...opts }).trim();
}

function gitSilent(args) {
  try {
    return git(args);
  } catch (err) {
    return '';
  }
}

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    const value = args[i + 1];
    if (value === undefined) {
      console.error(`Missing value for argument --${key}`);
      process.exit(1);
    }
    result[key] = value;
  }
  return result;
}

function getTimeline(base, head) {
  const output = gitSilent(['log', '--format=%H%x09%aI%x09%ae%x09%s', '--first-parent', `${base}..${head}`]);
  if (!output) return [];
  return output.split('\n').map(line => {
    const [hash, date, email, ...subjectParts] = line.split('\t');
    return { hash, date, email, subject: subjectParts.join('\t') };
  });
}

function getFiles(base, head) {
  const output = gitSilent(['diff', '--name-only', '--merge-base', base, head]);
  if (!output) return [];
  return output.split('\n').filter(Boolean);
}

function topDir(file) {
  const parts = file.split('/');
  return parts.length > 1 ? parts.slice(0, 2).join('/') : parts[0];
}

function buildOverlap(upstreamFiles, targetFiles) {
  const targetSet = new Set(targetFiles);
  const upstreamSet = new Set(upstreamFiles);
  const files = upstreamFiles.filter(f => targetSet.has(f));

  const dirMap = new Map();
  const allFiles = new Set([...upstreamFiles, ...targetFiles]);
  for (const f of allFiles) {
    const dir = topDir(f);
    if (!dirMap.has(dir)) {
      dirMap.set(dir, { path: dir, upstreamFiles: 0, targetFiles: 0, bothSides: false });
    }
    const entry = dirMap.get(dir);
    if (upstreamSet.has(f)) entry.upstreamFiles += 1;
    if (targetSet.has(f)) entry.targetFiles += 1;
  }
  const directories = [...dirMap.values()]
    .map(d => ({ ...d, bothSides: d.upstreamFiles > 0 && d.targetFiles > 0 }))
    .sort((a, b) => (b.upstreamFiles + b.targetFiles) - (a.upstreamFiles + a.targetFiles));

  return { files, directories };
}

function main() {
  const args = parseArgs();
  if (!args.upstream) {
    console.error('Usage: node change-summary.js --upstream <ref> [--target <ref>]');
    process.exit(1);
  }
  const upstream = args.upstream;
  const target = args.target || git(['rev-parse', '--abbrev-ref', 'HEAD']);

  try {
    const base = git(['merge-base', upstream, target]);
    const upstreamCommits = getTimeline(base, upstream);
    const targetCommits = getTimeline(base, target);
    const upstreamFiles = getFiles(base, upstream);
    const targetFiles = getFiles(base, target);
    const overlap = buildOverlap(upstreamFiles, targetFiles);

    const overlapSet = new Set(overlap.files);
    const uiFiles = [...overlapSet, ...upstreamFiles, ...targetFiles]
      .filter((f, i, arr) => arr.indexOf(f) === i)
      .filter(f => UI_PATH_PATTERN.test(f));

    const result = {
      upstream,
      target,
      mergeBase: base,
      upstreamCommit: git(['rev-parse', upstream]),
      targetCommit: git(['rev-parse', target]),
      upstreamCommits,
      targetCommits,
      upstreamFiles,
      targetFiles,
      overlap: {
        files: overlap.files,
        directories: overlap.directories,
      },
      hotspots: overlap.directories.filter(d => d.bothSides).slice(0, 10),
      uiFiles: {
        inOverlap: [...overlapSet].filter(f => UI_PATH_PATTERN.test(f)),
        all: uiFiles,
      },
      counts: {
        upstreamCommits: upstreamCommits.length,
        targetCommits: targetCommits.length,
        upstreamFiles: upstreamFiles.length,
        targetFiles: targetFiles.length,
        overlapFiles: overlap.files.length,
        bothSideDirs: overlap.directories.filter(d => d.bothSides).length,
      },
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('change-summary failed:', err.stderr || err.message);
    process.exit(1);
  }
}

main();
