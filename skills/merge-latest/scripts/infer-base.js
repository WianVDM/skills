#!/usr/bin/env node
/**
 * infer-base.js — score base-branch candidates for a target branch.
 *
 * Uses git history (merge-base and divergence counts) plus name similarity.
 * Optionally reads project config for default_base_branch and protected_branches.
 *
 * Usage:
 *   node infer-base.js [--target <branch>] [--remote <remote>] [--config <path>]
 *
 * Outputs JSON to stdout:
 *   {
 *     target: "SHB-317",
 *     candidates: [
 *       {
 *         branch: "SHB-315",
 *         mergeBase: "abc123...",
 *         aheadTarget: 7,
 *         aheadCandidate: 0,
 *         nameSimilarity: 0.92,
 *         relationship: "ancestor",
 *         score: 0.96,
 *         confidence: "high",
 *         reason: "Candidate is an ancestor of the target and has a strongly related name"
 *       },
 *       ...
 *     ],
 *     inferred: "SHB-315",
 *     confidence: "high"
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
    result[key] = value;
  }
  return result;
}

function loadConfig(configPath) {
  const defaultPath = path.join(process.cwd(), '.agents', 'config', 'merge-latest.yaml');
  const target = configPath || defaultPath;
  if (!fs.existsSync(target)) {
    return {};
  }
  const raw = fs.readFileSync(target, 'utf8');
  const config = {};
  let currentKey = null;
  for (const line of raw.split('\n')) {
    const match = line.match(/^(\w+):\s*(.*)$/);
    if (match) {
      currentKey = match[1];
      const value = match[2].trim();
      if (value) {
        config[currentKey] = value;
      } else {
        config[currentKey] = [];
      }
    } else if (currentKey && Array.isArray(config[currentKey])) {
      const item = line.match(/^\s*-\s*(.+)$/);
      if (item) config[currentKey].push(item[1].trim());
    }
  }
  return config;
}

function normalizeName(name) {
  return name
    .replace(/^[^/]+\//, '')
    .replace(/^refs\/heads\//, '')
    .replace(/^refs\/remotes\//, '')
    .toLowerCase();
}

function parseTicketKey(name) {
  const match = name.match(/^([a-z]+)[-_]?(\d+)$/i);
  if (!match) return null;
  return { prefix: match[1].toLowerCase(), number: parseInt(match[2], 10) };
}

function ticketSimilarity(a, b) {
  const ta = parseTicketKey(normalizeName(a));
  const tb = parseTicketKey(normalizeName(b));
  if (!ta || !tb) return null;
  if (ta.prefix !== tb.prefix) return 0;
  const diff = Math.abs(ta.number - tb.number);
  // Same prefix and close numbers strongly suggest a stacked relationship.
  if (diff === 0) return 1.0;
  if (diff <= 5) return 0.95;
  if (diff <= 20) return 0.85;
  if (diff <= 100) return 0.7;
  return 0.5;
}

function nameSimilarity(a, b) {
  const na = normalizeName(a);
  const nb = normalizeName(b);
  if (na === nb) return 1.0;

  const ticketSim = ticketSimilarity(a, b);
  if (ticketSim !== null) return ticketSim;

  if (na.includes(nb) || nb.includes(na)) return 0.7;

  const tokensA = new Set(na.split(/[^a-z0-9]+/).filter(Boolean));
  const tokensB = new Set(nb.split(/[^a-z0-9]+/).filter(Boolean));
  if (tokensA.size === 0 && tokensB.size === 0) return 0;

  const intersection = new Set([...tokensA].filter(t => tokensB.has(t)));
  const union = new Set([...tokensA, ...tokensB]);
  return intersection.size / union.size;
}

const COMMON_BASE_NAMES = new Set([
  'main',
  'master',
  'development',
  'origin/main',
  'origin/master',
  'origin/development',
]);

function isCommonBase(name) {
  return COMMON_BASE_NAMES.has(normalizeName(name));
}

function gatherCandidates(target, config) {
  const candidates = new Set();

  if (config.default_base_branch) {
    candidates.add(config.default_base_branch);
  }

  const locals = runSilent('git branch --format="%(refname:short)"')
    .split('\n')
    .filter(Boolean);
  for (const b of locals) {
    if (b !== target) candidates.add(b);
  }

  const remotes = runSilent('git branch -r --format="%(refname:short)"')
    .split('\n')
    .filter(b => b && !b.endsWith('/HEAD'));
  for (const b of remotes) {
    const short = b.replace(/^[^/]+\//, '');
    if (short === target) continue;
    candidates.add(b);
  }

  const headSym = runSilent('git rev-parse --abbrev-ref origin/HEAD');
  if (headSym && headSym !== 'origin/HEAD') {
    candidates.add(headSym);
  }

  return [...candidates];
}

function isAncestor(candidate, base) {
  // Returns true if `candidate` is an ancestor of `base`.
  try {
    run(`git merge-base --is-ancestor ${quote(candidate)} ${quote(base)}`);
    return true;
  } catch (err) {
    return false;
  }
}

function determineRelationship(aheadCandidate, aheadTarget) {
  if (aheadCandidate === 0 && aheadTarget === 0) return 'same';
  if (aheadCandidate === 0 && aheadTarget > 0) return 'ancestor';
  if (aheadCandidate > 0 && aheadTarget === 0) return 'descendant';
  return 'diverged';
}

function scoreCandidate(candidate, target, config, targetTimestamp) {
  let mergeBase = '';
  let aheadTarget = Infinity;
  let aheadCandidate = Infinity;

  try {
    mergeBase = run(`git merge-base ${quote(target)} ${quote(candidate)}`);
    aheadTarget = parseInt(
      run(`git rev-list --count ${quote(mergeBase)}..${quote(target)}`),
      10
    );
    aheadCandidate = parseInt(
      run(`git rev-list --count ${quote(mergeBase)}..${quote(candidate)}`),
      10
    );
  } catch (err) {
    return null;
  }

  const mergeBaseTimestamp = parseInt(
    runSilent(`git log -1 --format=%ct ${quote(mergeBase)}`),
    10
  ) || 0;
  const ageSeconds = targetTimestamp - mergeBaseTimestamp;
  // Normalize age: assume 90 days is "old". More recent split points are
  // stronger evidence that this candidate is the branch the target was based on.
  const maxAge = 90 * 24 * 3600;
  const recencyScore = Math.max(0, Math.min(1, 1 - ageSeconds / maxAge));

  const relationship = determineRelationship(aheadCandidate, aheadTarget);
  if (relationship === 'same') return null;

  const ns = nameSimilarity(candidate, target);
  const commonBase = isCommonBase(candidate);
  const defaultBaseName = config.default_base_branch || '';
  const defaultBase = defaultBaseName
    ? normalizeName(candidate) === normalizeName(defaultBaseName)
    : false;

  // A candidate that is an ancestor of both the target and the default base
  // branch is likely an old feature branch that was merged into the default
  // base, not the target's own base. Penalize it so the default base wins.
  const candidateIsAncestorOfDefaultBase =
    defaultBaseName && relationship === 'ancestor'
      ? isAncestor(candidate, defaultBaseName)
      : false;

  let baseScore = 0;
  const reasonParts = [];

  switch (relationship) {
    case 'ancestor':
      if (candidateIsAncestorOfDefaultBase) {
        // Old feature branch merged into default base; only win if no better
        // candidate exists.
        baseScore = 0.45;
        reasonParts.push('ancestor but also merged into default base branch');
      } else if (ns >= 0.8) {
        // Candidate is an ancestor of the target. This is the classic base-branch
        // relationship. Strong name similarity makes stacked features very likely.
        baseScore = 0.98;
        reasonParts.push('ancestor with strongly related name');
      } else if (ns >= 0.5) {
        baseScore = 0.85;
        reasonParts.push('ancestor with related name');
      } else if (commonBase || defaultBase) {
        baseScore = 0.82;
        reasonParts.push('ancestor and default/common base branch');
      } else {
        baseScore = 0.55;
        reasonParts.push('ancestor but weakly related name');
      }
      break;

    case 'descendant':
      // Candidate contains the target; it is downstream, not a base.
      baseScore = 0.05;
      reasonParts.push('candidate is downstream of target');
      break;

    case 'diverged':
      // Both branches have unique commits. They are siblings or parallel work.
      if (commonBase || defaultBase) {
        baseScore = 0.78;
        reasonParts.push('diverged from common/default base branch');
      } else {
        baseScore = 0.15;
        reasonParts.push('diverged parallel branch');
      }
      break;
  }

  if (defaultBase) {
    baseScore = Math.min(1, baseScore + 0.08);
    reasonParts.push('matches configured default base branch');
  }

  if (candidate.includes('/')) {
    reasonParts.push('remote tracking branch');
  }

  // Combine scores. Relationship dominates; recency and name similarity break ties.
  const totalScore = baseScore * 0.75 + ns * 0.15 + recencyScore * 0.10;

  let confidence = 'low';
  if (totalScore >= 0.85) {
    confidence = 'high';
  } else if (totalScore >= 0.55) {
    confidence = 'medium';
  }

  return {
    branch: candidate,
    mergeBase,
    aheadTarget,
    aheadCandidate,
    nameSimilarity: parseFloat(ns.toFixed(3)),
    recencyScore: parseFloat(recencyScore.toFixed(3)),
    relationship,
    score: parseFloat(totalScore.toFixed(3)),
    confidence,
    reason: reasonParts.join('; ') || 'candidate considered',
  };
}

function main() {
  const args = parseArgs();
  const config = loadConfig(args.config);

  let target = args.target;
  if (!target) {
    target = run('git rev-parse --abbrev-ref HEAD');
  }

  const targetTimestamp = parseInt(
    runSilent(`git log -1 --format=%ct ${quote(target)}`),
    10
  ) || Math.floor(Date.now() / 1000);

  const rawCandidates = gatherCandidates(target, config);
  const scored = rawCandidates
    .map(c => scoreCandidate(c, target, config, targetTimestamp))
    .filter(Boolean)
    .sort((a, b) => b.score - a.score);

  if (scored.length === 0) {
    console.error('infer-base failed: no candidates found');
    process.exit(1);
  }

  const top = scored[0];
  const runnerUp = scored[1];

  let inferred = top.branch;
  let confidence = top.confidence;
  let handledAsTwin = false;

  // If the top candidate has a remote tracking twin at the same commit,
  // prefer the remote ref for freshness and do not treat it as ambiguity.
  if (runnerUp && runnerUp.score >= top.score - 0.12) {
    const topNorm = normalizeName(top.branch);
    const runnerNorm = normalizeName(runnerUp.branch);
    const sameNormalizedName = topNorm === runnerNorm;
    const sameCommit = top.mergeBase === runnerUp.mergeBase &&
      top.aheadTarget === runnerUp.aheadTarget &&
      top.aheadCandidate === runnerUp.aheadCandidate;

    if (sameNormalizedName && sameCommit) {
      inferred = top.branch.includes('/') ? top.branch : runnerUp.branch;
      confidence = 'high';
      handledAsTwin = true;
    }
  }

  // The configured default base branch is an explicit user preference. If it
  // wins with a reasonable score, trust it so the skill can proceed.
  const defaultBaseName = config.default_base_branch || '';
  const topIsDefaultBase = defaultBaseName &&
    normalizeName(top.branch) === normalizeName(defaultBaseName);
  if (topIsDefaultBase && top.score >= 0.6) {
    confidence = 'high';
  } else if (!handledAsTwin && runnerUp && runnerUp.score >= top.score - 0.12 && confidence === 'high') {
    confidence = 'medium';
  }

  const result = {
    target,
    candidates: scored,
    inferred,
    confidence,
  };

  console.log(JSON.stringify(result, null, 2));
}

main();
