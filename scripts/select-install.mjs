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
 *   node select-install.mjs --print -g      # print the CLI command, don't run
 *   node select-install.mjs --source ../skills/skills.json
 *
 * Selector input: numbers (3), ranges (12-15), bundle names (main, blocks,
 * setup), 'a' = all, 'n' = none. Each token toggles. Empty line = done.
 */

import { spawn } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
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

if (flags.help) {
  console.log(`select-install — checkbox selector wrapping the Vercel skills CLI

  node scripts/select-install.mjs [options]

Options:
  -g, --global       Global scope (~/<agent>/skills)
  -p, --project      Project scope (./<agent>/skills)
  --remove           Remove selected skills instead of installing
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
    const child = spawn(cmd, { shell: true, stdio: quiet ? 'pipe' : 'inherit' });
    let out = '';
    if (quiet) child.stdout.on('data', (d) => (out += d));
    child.on('close', (code) => res({ code, out }));
    child.on('error', () => res({ code: 1, out }));
  });
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
  return { bundles };
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
  return { bundles: [{ name: 'all', skills }] };
}

// ─── installed state (via CLI) ───────────────────────────────────────────────

async function loadInstalled(scopeFlag) {
  const { code, out } = await run(`npx -y ${CLI} list --json${scopeFlag}`, { quiet: true });
  if (code !== 0) return { installed: new Set(), ok: false };
  try {
    return { installed: new Set(JSON.parse(out).map((s) => s.name)), ok: true };
  } catch {
    return { installed: new Set(), ok: false };
  }
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

const mode = flags.remove ? 'remove' : 'install';

let scope = flags.global ? 'global' : flags.project ? 'project' : null;
if (!scope) {
  const ans = await ask('Scope — [g]lobal or [p]roject? ');
  scope = ans && ans.trim().toLowerCase().startsWith('g') ? 'global' : 'project';
}
const scopeFlag = scope === 'global' ? ' -g' : '';

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
const { code } = await run(cmd);
process.exit(code ?? 0);
