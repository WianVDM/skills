#!/usr/bin/env node
/**
 * conflict-brief.js — build a brief for a conflicted file.
 *
 * Extracts the base, target (ours), and upstream (theirs) versions of the file,
 * identifies conflict blocks in the working tree copy, and gathers authorship
 * and commit context for each side.
 *
 * Usage:
 *   node conflict-brief.js --file <path> --base <commit> --target <ref> --upstream <ref>
 *
 * Outputs JSON to stdout:
 *   {
 *     file: "src/app/foo.ts",
 *     base: { commit: "abc...", content: "..." },
 *     target: { commit: "def...", content: "..." },
 *     upstream: { commit: "ghi...", content: "..." },
 *     conflictBlocks: [
 *       {
 *         startLine: 42,
 *         endLine: 67,
 *         targetAuthors: ["Alice <alice@example.com>"],
 *         upstreamAuthors: ["Bob <bob@example.com>"],
 *         targetCommits: [{ hash: "def...", subject: "..." }],
 *         upstreamCommits: [{ hash: "ghi...", subject: "..." }]
 *       }
 *     ],
 *     targetCommits: [...],
 *     upstreamCommits: [...],
 *     recommendation: "ask"
 *   }
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function quote(str) {
  return '"' + String(str).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
}

function run(cmd, opts = {}) {
  return execSync(cmd, { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'], ...opts }).trim();
}

function runSilent(cmd) {
  try {
    return run(cmd);
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

function getVersion(ref, file) {
  try {
    return run(`git show ${quote(ref)}:${quote(file)}`);
  } catch (err) {
    return null;
  }
}

function getCommits(base, head, file) {
  const output = runSilent(
    `git log --format='%H%x09%s%x09%ae' ${quote(base)}..${quote(head)} -- ${quote(file)}`
  );
  if (!output) return [];
  return output.split('\n').map(line => {
    const [hash, ...rest] = line.split('\t');
    const email = rest.pop() || '';
    const subject = rest.join('\t');
    return { hash, subject, email };
  });
}

function getAuthors(commits) {
  const authors = new Set();
  for (const c of commits) {
    if (c.email) authors.add(`<${c.email}>`);
  }
  return [...authors];
}

const MARKER_START = /^\u003c\u003c\u003c\u003c\u003c\u003c\u003c /;
const MARKER_SEP = /^=======/;
const MARKER_END = /^\u003e\u003e\u003e\u003e\u003e\u003e\u003e /;

function parseConflictBlocks(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    if (MARKER_START.test(lines[i])) {
      const startLine = i + 1;
      i++;
      while (i < lines.length && !MARKER_SEP.test(lines[i]) && !MARKER_END.test(lines[i])) {
        i++;
      }

      if (!MARKER_SEP.test(lines[i])) {
        i = startLine;
        continue;
      }
      i++;

      while (i < lines.length && !MARKER_END.test(lines[i])) {
        i++;
      }

      if (i >= lines.length) break;
      const endLine = i + 1;

      blocks.push({ startLine, endLine });
    }
    i++;
  }

  return blocks;
}

function hasUpstreamSignal(commits) {
  return commits.some(c => {
    const s = c.subject.toLowerCase();
    return (
      s.includes('fix') ||
      s.includes('revert') ||
      s.includes('hotfix') ||
      s.includes('security') ||
      s.includes('patch')
    );
  });
}

function inferRecommendation(targetCommits, upstreamCommits) {
  const upstreamSignal = hasUpstreamSignal(upstreamCommits);
  const targetSignal = hasUpstreamSignal(targetCommits);

  if (upstreamSignal && !targetSignal) return 'accept-upstream';
  if (targetSignal && !upstreamSignal) return 'accept-target';
  return 'ask';
}

function main() {
  const args = parseArgs();
  if (!args.file || !args.base || !args.target || !args.upstream) {
    console.error(
      'Usage: node conflict-brief.js --file <path> --base <commit> --target <ref> --upstream <ref>'
    );
    process.exit(1);
  }

  const filePath = path.resolve(args.file);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  try {
    const baseVersion = getVersion(args.base, args.file);
    const targetVersion = getVersion(args.target, args.file);
    const upstreamVersion = getVersion(args.upstream, args.file);

    const targetCommits = getCommits(args.base, args.target, args.file);
    const upstreamCommits = getCommits(args.base, args.upstream, args.file);
    const targetAuthors = getAuthors(targetCommits);
    const upstreamAuthors = getAuthors(upstreamCommits);

    const rawBlocks = parseConflictBlocks(filePath);
    const conflictBlocks = rawBlocks.map(block => ({
      startLine: block.startLine,
      endLine: block.endLine,
      targetAuthors,
      upstreamAuthors,
      targetCommits,
      upstreamCommits,
    }));

    const result = {
      file: args.file,
      base: { commit: args.base, content: baseVersion },
      target: { commit: args.target, content: targetVersion },
      upstream: { commit: args.upstream, content: upstreamVersion },
      conflictBlocks,
      targetCommits,
      upstreamCommits,
      recommendation: inferRecommendation(targetCommits, upstreamCommits),
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('conflict-brief failed:', err.stderr || err.message);
    process.exit(1);
  }
}

main();
