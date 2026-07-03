#!/usr/bin/env node
/**
 * resolve-trivial.js — attempt safe, deterministic conflict resolutions.
 *
 * Only resolves conflicts where:
 *   - one side made no change to the region (the other side is the full change), or
 *   - both sides added independent, non-overlapping content to an empty base region.
 *
 * Anything ambiguous is left untouched.
 *
 * Usage:
 *   node resolve-trivial.js --file path/to/file.ts
 *
 * Outputs JSON describing attempted resolutions.
 */

const fs = require('fs');
const path = require('path');

const MARKER_START = /^<{7} /;
const MARKER_BASE = /^\|{7} /;
const MARKER_SEP = /^={7}$/;
const MARKER_END = /^>{7} /;

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

function readConflictBlocks(content) {
  const lines = content.split('\n');
  const blocks = [];
  let i = 0;

  while (i < lines.length) {
    if (MARKER_START.test(lines[i])) {
      const startIdx = i;
      const oursLabel = lines[i];
      i++;

      const ours = [];
      while (i < lines.length && !MARKER_BASE.test(lines[i]) && !MARKER_SEP.test(lines[i])) {
        ours.push(lines[i]);
        i++;
      }

      let base = [];
      if (MARKER_BASE.test(lines[i])) {
        i++;
        while (i < lines.length && !MARKER_SEP.test(lines[i])) {
          base.push(lines[i]);
          i++;
        }
      }

      if (!MARKER_SEP.test(lines[i])) {
        // Malformed conflict; skip.
        i = startIdx + 1;
        continue;
      }
      i++;

      const theirs = [];
      while (i < lines.length && !MARKER_END.test(lines[i])) {
        theirs.push(lines[i]);
        i++;
      }

      if (i >= lines.length) break;
      const theirsLabel = lines[i];
      const endIdx = i;

      blocks.push({
        start: startIdx,
        end: endIdx,
        oursLabel,
        theirsLabel,
        ours: ours.join('\n'),
        base: base.join('\n'),
        theirs: theirs.join('\n'),
      });
    }
    i++;
  }

  return blocks;
}

function isEmptyish(text) {
  return text.trim().length === 0;
}

function normalizeLines(text) {
  return text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
}

function isSubset(a, b) {
  const na = normalizeLines(a);
  const nb = normalizeLines(b);
  if (na.length === 0 || nb.length === 0) return false;
  return na.every(line => nb.includes(line));
}

function resolveBlock(block) {
  // One side did not change the region: accept the changed side.
  if (isEmptyish(block.ours) && !isEmptyish(block.theirs)) {
    return { resolved: true, content: block.theirs, reason: 'upstream-only-change' };
  }
  if (!isEmptyish(block.ours) && isEmptyish(block.theirs)) {
    return { resolved: true, content: block.ours, reason: 'target-only-change' };
  }

  // Both sides added independent content to an empty base region.
  if (isEmptyish(block.base)) {
    // If one side is a subset of the other, keep the superset to avoid duplication.
    if (isSubset(block.ours, block.theirs)) {
      return { resolved: true, content: block.theirs, reason: 'upstream-superset' };
    }
    if (isSubset(block.theirs, block.ours)) {
      return { resolved: true, content: block.ours, reason: 'target-superset' };
    }

    const combined = block.ours + '\n' + block.theirs;
    return { resolved: true, content: combined, reason: 'both-added-non-overlapping' };
  }

  return { resolved: false, reason: 'both-changed-base-content' };
}

function resolveFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const blocks = readConflictBlocks(content);
  if (blocks.length === 0) {
    return { file: filePath, resolved: 0, remaining: 0, resolutions: [] };
  }

  const lines = content.split('\n');
  const newLines = [];
  let lastEnd = 0;
  let resolvedCount = 0;
  let remainingCount = 0;
  const resolutions = [];

  for (const block of blocks) {
    // Add lines before this block.
    for (let i = lastEnd; i < block.start; i++) {
      newLines.push(lines[i]);
    }

    const result = resolveBlock(block);
    if (result.resolved) {
      newLines.push(result.content);
      resolvedCount++;
      resolutions.push({ reason: result.reason });
    } else {
      // Keep the conflict markers as-is.
      for (let i = block.start; i <= block.end; i++) {
        newLines.push(lines[i]);
      }
      remainingCount++;
      resolutions.push({ reason: result.reason, kept: true });
    }

    lastEnd = block.end + 1;
  }

  // Add trailing lines.
  for (let i = lastEnd; i < lines.length; i++) {
    newLines.push(lines[i]);
  }

  const newContent = newLines.join('\n');
  if (resolvedCount > 0) {
    fs.writeFileSync(filePath, newContent, 'utf8');
  }

  return {
    file: filePath,
    resolved: resolvedCount,
    remaining: remainingCount,
    resolutions,
  };
}

function main() {
  const args = parseArgs();
  if (!args.file) {
    console.error('Usage: node resolve-trivial.js --file <path>');
    process.exit(1);
  }

  const filePath = path.resolve(args.file);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  try {
    const result = resolveFile(filePath);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('resolve failed:', err.message);
    process.exit(1);
  }
}

main();
