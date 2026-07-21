#!/usr/bin/env node
/**
 * select-install.mjs — plain-text checkbox selector for the WianVDM/skills bundle.
 *
 * Why this exists: the Vercel `skills` CLI interactive picker has no usable
 * per-skill selection indicator and disables search when groups exist
 * (upstream: vercel-labs/skills#439, #992). This script replaces ONLY the
 * selection screen; install/remove/update are still executed by the official
 * CLI. Delete it when the CLI picker grows real checkboxes.
 *
 * Catalog source (hybrid): skills.json from GitHub raw (fast, structured,
 * grouped by bundle), with fallbacks: --source <path>, ./skills.json in cwd,
 * or parsing `npx skills add WianVDM/skills --list`.
 *
 * Installed state and all mutations go through the CLI:
 *   skills list --json | skills add --skill ... | skills remove ...
 *
 * Usage:
 *   node select-install.mjs                 # install mode, prompts for scope
 *   node select-install.mjs -g              # install, global scope
 *   node select-install.mjs --remove -g     # remove mode
 *   node select-install.mjs --update -g     # refresh installed bundle skills + install missing deps
 *   node select-install.mjs --update --clean -g  # remove-first clean update
 *   node select-install.mjs --print -g      # print the CLI command, don't run
 *   node select-install.mjs --source ../skills/skills.json
 *
 * Selector input: numbers (3), ranges (12-15), bundle names (main, blocks,
 * setup), 'a' = all, 'n' = none. Each token toggles. Empty line = done.
 */

import { spawn } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { homedir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import * as readline from 'node:readline';

const REPO = 'WianVDM/skills';
const RAW = `https://raw.githubusercontent.com/${REPO}/main`;
const CLI = 'skills@latest';

// ─── args ────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const flags = {
  global: args.includes('-g') || args.includes('--global'),
  project: args.includes('-p') || args.includes('--project'),
  remove: args.includes('--remove'),
  update: args.includes('--update'),
  clean: args.includes('--clean'),
  withOptional: args.includes('--with-optional'),
  noRecommended: args.includes('--no-recommended'),
  print: args.includes('--print'),
  yes: args.includes('-y') || args.includes('--yes'),
  help: args.includes('-h') || args.includes('--help'),
  source: null,
  agents: [],
};
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--source') flags.source = args[++i];
  if (args[i] === '-a' || args[i] === '--agent') flags.agents.push(args[++i]);
}

if (flags.clean && !flags.update) {
  console.error('--clean only makes sense with --update.');
  process.exit(1);
}
if (flags.update && flags.remove) {
  console.error('--update and --remove are mutually exclusive.');
  process.exit(1);
}

if (flags.help) {
  console.log(`select-install — checkbox selector wrapping the Vercel skills CLI

  node scripts/select-install.mjs [options]

Options:
  -g, --global       Global scope (~/<agent>/skills)
  -p, --project      Project scope (./<agent>/skills)
  --remove           Remove selected skills instead of installing
  --update           Refresh installed bundle skills and install missing
                     dependencies (required + recommended). No selector.
  --clean            With --update: remove installed bundle skills first,
                     then reinstall (clears files deleted upstream)
  --with-optional    With --update: also install optional dependencies
  --no-recommended   With --update: required dependencies only
  -a, --agent <name> Target agent (repeatable), passed to the CLI
  --print            Print the CLI command without running it
  -y, --yes          Skip the final run confirmation
  --source <path>    Load catalog from a local skills.json
  -h, --help         This help

Selector input: numbers (3), ranges (12-15), bundle names (main, blocks,
setup), 'a' = all, 'n' = none. Each token toggles. Empty line = done.`);
  process.exit(0);
}

// ─── helpers ─────────────────────────────────────────────────────────────────

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const lineIter = rl[Symbol.asyncIterator]();
// EOF-safe prompt: returns null when stdin closes (piped input exhausted).
const ask = async (q) => {
  process.stdout.write(q);
  const { value, done } = await lineIter.next();
  return done ? null : value;
};

function run(cmd, { quiet = false } = {}) {
  return new Promise((res) => {
    const child = spawn(cmd, { shell: true, stdio: ['inherit', 'pipe', 'pipe'] });
    let out = '';
    const cap = (d) => {
      const s = d.toString();
      out += s;
      if (!quiet) process.stdout.write(s);
    };
    child.stdout.on('data', cap);
    child.stderr.on('data', cap);
    child.on('close', (code) => res({ code, out }));
    child.on('error', () => res({ code: 1, out }));
  });
}

// Known CLI bug (vercel-labs/skills#1352): a global install without -a expands
// to all agents, including project-only agents like PromptScript that have no
// global skills dir. The CLI prints a per-skill ✗ for those targets — noise,
// not failure. Update mode avoids it by targeting the user's current agents;
// these helpers classify whatever failure lines remain.
function splitFailureLines(out) {
  const failures = stripAnsi(out)
    .split('\n')
    .filter((l) => /✗|✖|×/.test(l));
  return {
    noise: failures.filter((l) => l.includes('does not support global skill installation')),
    real: failures.filter((l) => !l.includes('does not support global skill installation')),
  };
}

function explainNoise(noise) {
  console.warn(
    `\n! The ${noise.length} red ✗ line(s) above — "… does not support global skill installation" —\n` +
      '  are a known CLI bug (vercel-labs/skills#1352), not real failures. The skills\n' +
      '  installed fine for your agents. Verify with: npx skills list',
  );
}

function parseInvalidAgents(out) {
  const m = stripAnsi(out).match(/Invalid agents: ([^\n]+)/);
  if (!m) return [];
  return m[1].split(',').map((s) => s.trim()).filter(Boolean);
}

// Handle the outcome of a mutation command (add/remove). Real failures exit;
// PromptScript noise is explained; noise-induced non-zero exits are tolerated.
function handleMutationOutcome({ code, out }) {
  const { noise, real } = splitFailureLines(out);
  if (real.length) {
    console.error('\nFailed for these skills/agents:');
    for (const l of real) console.error(`  ${l.trim()}`);
    process.exit(code || 1);
  }
  if (noise.length) explainNoise(noise);
  if (code !== 0 && noise.length === 0) process.exit(code ?? 1);
}

const stripAnsi = (s) => s.replace(/\x1b\[[0-9;]*m/g, '');
const truncate = (s, n) => (s && s.length > n ? s.slice(0, n - 1) + '…' : s || '');

// ─── catalog loading ─────────────────────────────────────────────────────────

async function loadCatalog() {
  // 1. explicit local source, 2. ./skills.json, 3. GitHub raw, 4. CLI --list parse
  const localPath = flags.source || (existsSync('./skills.json') ? './skills.json' : null);
  if (localPath) {
    try {
      const indexPath = join(dirname(resolve(localPath)), 'docs', 'skill-capability-index.json');
      const index = existsSync(indexPath) ? JSON.parse(readFileSync(indexPath, 'utf-8')) : null;
      return fromSkillsJson(JSON.parse(readFileSync(localPath, 'utf-8')), index);
    } catch {
      console.warn(`Could not read ${localPath}, trying network…`);
    }
  }
  try {
    const [sjRes, ixRes] = await Promise.all([
      fetch(`${RAW}/skills.json`),
      fetch(`${RAW}/docs/skill-capability-index.json`),
    ]);
    if (!sjRes.ok) throw new Error(`HTTP ${sjRes.status}`);
    const skillsJson = await sjRes.json();
    const index = ixRes.ok ? await ixRes.json() : null;
    return fromSkillsJson(skillsJson, index);
  } catch (err) {
    console.warn(`Fetch failed (${err.message}); falling back to parsing CLI --list…`);
    return fromCliList();
  }
}

function fromSkillsJson(skillsJson, capabilityIndex) {
  const desc = {};
  for (const s of capabilityIndex?.skills ?? []) desc[s.name] = s.description;
  const bundles = (skillsJson.bundles ?? []).map((b) => ({
    name: b.name,
    skills: b.skills.map((n) => ({ name: n, description: desc[n] ?? '' })),
  }));
  const inBundles = new Set(bundles.flatMap((b) => b.skills.map((s) => s.name)));
  const all = skillsJson.skills.map((p) => basename(p));
  const other = all.filter((n) => !inBundles.has(n));
  if (other.length) bundles.push({ name: 'other', skills: other.map((n) => ({ name: n, description: desc[n] ?? '' })) });
  return { bundles, deps: skillsJson.skill_dependencies ?? {}, allNames: new Set(all) };
}

async function fromCliList() {
  const { code, out } = await run(`npx -y ${CLI} add ${REPO} --list`, { quiet: true });
  if (code !== 0) throw new Error('Could not load the catalog from any source.');
  const lines = stripAnsi(out).split('\n');
  const skills = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^│    ([a-z][a-z0-9-]*)\s*$/);
    if (m) {
      const d = lines[i + 1]?.match(/^│\s+(\S.*)$/);
      skills.push({ name: m[1], description: d ? d[1].trim() : '' });
    }
  }
  return { bundles: [{ name: 'all', skills }], deps: null, allNames: new Set(skills.map((s) => s.name)) };
}

// ─── installed state (via CLI) ───────────────────────────────────────────────

async function loadInstalled(scopeFlag) {
  const { code, out } = await run(`npx -y ${CLI} list --json${scopeFlag}`, { quiet: true });
  if (code !== 0) return { installed: new Set(), entries: [], ok: false };
  try {
    const entries = JSON.parse(out);
    return { installed: new Set(entries.map((s) => s.name)), entries, ok: true };
  } catch {
    return { installed: new Set(), entries: [], ok: false };
  }
}

// CLI agent ids are kebab-case; `skills list --json` reports display names
// ("Claude Code"). Slugify maps them back (claude-code, gemini-cli, pi, …).
function deriveAgentIds(entries) {
  const set = new Set();
  for (const e of entries) {
    for (const a of e.agents ?? []) {
      const id = a.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
      if (id) set.add(id);
    }
  }
  return [...set].sort();
}

// ─── update mode ─────────────────────────────────────────────────────────────

// The CLI's lock file records which source repo each installed skill came from,
// which lets us tell bundle skills apart from third-party installs.
function loadLockSources(scope) {
  const base = scope === 'global' ? homedir() : process.cwd();
  const lockPath = join(base, '.agents', '.skill-lock.json');
  if (!existsSync(lockPath)) return { sources: null, lockPath };
  try {
    const lock = JSON.parse(readFileSync(lockPath, 'utf-8'));
    const sources = new Map();
    for (const [name, entry] of Object.entries(lock.skills ?? {})) {
      sources.set(name, entry.source);
    }
    return { sources, lockPath };
  } catch {
    return { sources: null, lockPath };
  }
}

// Transitive dependency closure over the catalog's skill_dependencies.
// Effective tier is the weakest link along the path: a required dep of a
// recommended dep is itself recommended. Optional is only walked when asked.
function computeClosure(roots, deps, { recommended, optional }) {
  const rank = { required: 0, recommended: 1, optional: 2 };
  const best = new Map();
  const queue = roots.map((name) => ({ name, tier: 'required' }));
  while (queue.length) {
    const { name, tier } = queue.shift();
    const entry = deps[name];
    if (!entry) continue;
    const tiers = ['required'];
    if (recommended) tiers.push('recommended');
    if (optional) tiers.push('optional');
    for (const t of tiers) {
      for (const d of entry[t] ?? []) {
        const eff = rank[t] >= rank[tier] ? t : tier;
        if (!best.has(d) || rank[eff] < rank[best.get(d)]) {
          best.set(d, eff);
          queue.push({ name: d, tier: eff });
        }
      }
    }
  }
  best.forEach((_, k) => { if (roots.includes(k)) best.delete(k); });
  return best;
}

async function runUpdate(scope, scopeFlag) {
  const catalog = await loadCatalog();
  const { installed, entries, ok } = await loadInstalled(scopeFlag);
  if (!ok) {
    console.error('Could not read installed skills from the CLI. Is `npx skills` working?');
    process.exit(1);
  }

  // Which installed skills belong to this bundle?
  const warnings = [];
  const { sources } = loadLockSources(scope);
  let bundleInstalled;
  if (sources) {
    bundleInstalled = [...installed].filter((n) => sources.get(n) === REPO);
  } else {
    bundleInstalled = [...installed].filter((n) => catalog.allNames.has(n));
    warnings.push('No CLI lock file found; matched bundle skills by name only. Orphan detection is off.');
  }

  if (bundleInstalled.length === 0) {
    console.log(`No installed ${REPO} skills found in ${scope} scope. Nothing to update.`);
    process.exit(0);
  }

  const refresh = bundleInstalled.filter((n) => catalog.allNames.has(n)).sort();
  const orphans = bundleInstalled.filter((n) => !catalog.allNames.has(n)).sort();

  // Missing dependencies of the refresh set.
  let missing = new Map();
  if (catalog.deps) {
    const closure = computeClosure(refresh, catalog.deps, {
      recommended: !flags.noRecommended,
      optional: flags.withOptional,
    });
    for (const [name, tier] of closure) {
      if (!installed.has(name) && catalog.allNames.has(name)) missing.set(name, tier);
    }
    const unmapped = refresh.filter((n) => !(n in catalog.deps));
    if (unmapped.length) warnings.push(`No dependency entry for: ${unmapped.join(', ')} — assuming none.`);
  } else {
    warnings.push('Catalog has no dependency data (CLI --list fallback); refreshing without dependency resolution.');
  }

  const byTier = { required: [], recommended: [], optional: [] };
  for (const [name, tier] of [...missing].sort()) byTier[tier].push(name);
  const toInstall = [...missing.keys()];

  // Target the agents from the current install (or explicit -a). This keeps
  // links exactly where they are and sidesteps the PromptScript global-install
  // bug, which only fires when the CLI expands to all agents on its own.
  const agentIds = flags.agents.length ? flags.agents : deriveAgentIds(entries);
  const addCmdFor = (agents) =>
    `npx -y ${CLI} add ${REPO} ${addSet.map((n) => `--skill ${n}`).join(' ')}${scopeFlag}${agents.map((a) => ` -a ${a}`).join('')} -y`;

  console.log(`\nUpdate plan (${scope} scope) — ${REPO}`);
  console.log(`  Agents: ${agentIds.length ? agentIds.join(', ') : 'all detected by the CLI'}`);
  console.log(`  Refresh (${refresh.length}): ${refresh.join(', ')}`);
  if (toInstall.length) {
    console.log('  Install missing dependencies:');
    for (const t of ['required', 'recommended', 'optional']) {
      if (byTier[t].length) console.log(`    ${t}: ${byTier[t].join(', ')}`);
    }
  } else if (catalog.deps) {
    console.log('  Dependencies: all satisfied.');
  }
  if (orphans.length) {
    console.log(`  Orphans (${orphans.length}): ${orphans.join(', ')} — no longer in the catalog; ${flags.clean ? 'will be removed' : 'left installed (use --remove to uninstall)'}.`);
  }
  warnings.push('Local edits to installed skill files will be overwritten.');
  for (const w of warnings) console.log(`  ! ${w}`);

  const addSet = [...new Set([...refresh, ...toInstall])];
  const removeSet = flags.clean ? [...new Set([...refresh, ...orphans])] : [];
  const removeCmd = flags.clean ? `npx -y ${CLI} remove ${removeSet.join(' ')}${scopeFlag} -y` : null;
  const addCmd = addCmdFor(agentIds);

  console.log('\nCommand(s):');
  if (removeCmd) console.log(`  ${removeCmd}`);
  console.log(`  ${addCmd}\n`);

  if (flags.print) process.exit(0);
  if (!flags.yes) {
    const go = await ask('Run it? [Y/n] ');
    if (go === null || go.trim().toLowerCase() === 'n') {
      console.log('Aborted; no changes made.');
      process.exit(0);
    }
  }
  rl.close();

  if (removeCmd) {
    const res = await run(removeCmd);
    const { noise, real } = splitFailureLines(res.out);
    if (real.length || (res.code !== 0 && noise.length === 0)) {
      console.error('Remove failed; aborting before reinstall. Re-run to retry.');
      process.exit(res.code || 1);
    }
    if (noise.length) explainNoise(noise);
  }
  let outcome = await run(addCmd);
  const invalid = parseInvalidAgents(outcome.out);
  if (invalid.length) {
    const keep = agentIds.filter((a) => !invalid.includes(a));
    console.warn(
      `\n! The CLI rejected agent id(s): ${invalid.join(', ')} — retrying without them.\n` +
      '  If one of your agents was dropped, re-run with its correct id via -a.',
    );
    outcome = await run(addCmdFor(keep));
  }
  handleMutationOutcome(outcome);

  console.log('\nDone. Follow-up:');
  console.log('  1. Re-run /setup-wian-skills in your agent — config keys may have been added; reinstalling does not reset existing config.');
  console.log('  2. Restart your agent harness so it reloads the skill files.');
  process.exit(0);
}

// ─── selector UI ─────────────────────────────────────────────────────────────

function render(rows, bundles, mode) {
  console.log(`\n${REPO} — ${mode === 'remove' ? 'select skills to REMOVE' : 'select skills to install'}`);
  console.log(`Toggle: numbers (3), ranges (12-15), bundle names (${bundles.map((b) => b.name).join(', ')}), a = all, n = none. Empty line = done.\n`);
  const width = Math.max(...rows.map((r) => r.name.length));
  for (const b of bundles) {
    console.log(b.name);
    for (const row of rows.filter((r) => r.bundle === b.name)) {
      const box = row.selected ? '[x]' : '[ ]';
      const num = String(row.index).padStart(3);
      console.log(`  ${box} ${num}  ${row.name.padEnd(width)}  ${truncate(row.description, 60)}`);
    }
    console.log();
  }
  console.log(`Selected: ${rows.filter((r) => r.selected).length}/${rows.length}`);
}

function applyToken(rows, bundles, token) {
  token = token.trim().toLowerCase();
  if (!token) return;
  if (token === 'a' || token === 'all') return rows.forEach((r) => (r.selected = true));
  if (token === 'n' || token === 'none') return rows.forEach((r) => (r.selected = false));
  if (bundles.some((b) => b.name === token)) {
    return rows.forEach((r) => { if (r.bundle === token) r.selected = !r.selected; });
  }
  const range = token.match(/^(\d+)-(\d+)$/);
  if (range) {
    const [lo, hi] = [+range[1], +range[2]];
    return rows.forEach((r) => { if (r.index >= lo && r.index <= hi) r.selected = !r.selected; });
  }
  if (/^\d+$/.test(token)) {
    const row = rows.find((r) => r.index === +token);
    if (row) row.selected = !row.selected;
  }
}

// ─── main ────────────────────────────────────────────────────────────────────

let scope = flags.global ? 'global' : flags.project ? 'project' : null;
if (!scope) {
  const ans = await ask('Scope — [g]lobal or [p]roject? ');
  scope = ans && ans.trim().toLowerCase().startsWith('g') ? 'global' : 'project';
}
const scopeFlag = scope === 'global' ? ' -g' : '';

if (flags.update) await runUpdate(scope, scopeFlag);

const mode = flags.remove ? 'remove' : 'install';

const catalog = await loadCatalog();
const { installed, ok } = await loadInstalled(scopeFlag);
if (!ok) console.warn('Could not read installed skills from the CLI; nothing pre-ticked.');

// Flatten with running numbers; pre-tick per mode.
let index = 0;
const rows = catalog.bundles.flatMap((b) =>
  b.skills.map((s) => ({
    index: ++index,
    bundle: b.name,
    name: s.name,
    description: s.description,
    selected: mode === 'install' ? installed.has(s.name) : false,
  }))
);

// Remove mode: restrict to installed bundle skills.
const activeRows = mode === 'remove' ? rows.filter((r) => installed.has(r.name)) : rows;
if (mode === 'remove' && activeRows.length === 0) {
  console.log('No installed bundle skills found in this scope. Nothing to remove.');
  process.exit(0);
}
// Re-number after filtering.
activeRows.forEach((r, i) => (r.index = i + 1));
const activeBundles = catalog.bundles.filter((b) => activeRows.some((r) => r.bundle === b.name));

render(activeRows, activeBundles, mode);
for (;;) {
  const input = await ask('> ');
  if (input === null || !input.trim()) break;
  for (const token of input.split(/[,\s]+/)) applyToken(activeRows, activeBundles, token);
  render(activeRows, activeBundles, mode);
}

const chosen = activeRows.filter((r) => r.selected).map((r) => r.name);
if (chosen.length === 0) {
  console.log('Nothing selected. Aborted; no changes made.');
  process.exit(0);
}

const cmd =
  mode === 'remove'
    ? `npx -y ${CLI} remove ${chosen.join(' ')}${scopeFlag} -y`
    : `npx -y ${CLI} add ${REPO} ${chosen.map((n) => `--skill ${n}`).join(' ')}${scopeFlag}${flags.agents.map((a) => ` -a ${a}`).join('')} -y`;

console.log(`\nCommand:\n  ${cmd}\n`);

if (flags.print) process.exit(0);
if (!flags.yes) {
  const go = await ask('Run it? [Y/n] ');
  if (go === null || go.trim().toLowerCase() === 'n') {
    console.log('Aborted; no changes made.');
    process.exit(0);
  }
}

rl.close();
handleMutationOutcome(await run(cmd));
process.exit(0);
