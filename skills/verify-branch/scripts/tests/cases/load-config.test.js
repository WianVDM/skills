const assert = require("assert");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { loadConfig, deepMerge } = require("../../lib/load-config");

const TEST_DIR = fs.mkdtempSync(path.join(__dirname, "tmp-config-"));

function setupConfig(content, shared = null) {
  const configDir = path.join(TEST_DIR, ".agents", "config");
  fs.mkdirSync(configDir, { recursive: true });
  if (shared !== null) {
    fs.writeFileSync(path.join(configDir, "shared.yaml"), shared);
  }
  fs.writeFileSync(path.join(configDir, "verify-branch.yaml"), content);
}

function clearConfig() {
  const configDir = path.join(TEST_DIR, ".agents", "config");
  fs.rmSync(configDir, { recursive: true, force: true });
}

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}: ${err.message}`);
    process.exitCode = 1;
  }
}

console.log("load-config tests");

test("loads valid verify-branch config", () => {
  clearConfig();
  setupConfig(`
preferences:
  fail_fast: true
  gates:
    test:
      enabled: true
`);
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.errors.length, 0, `unexpected errors: ${result.errors.join(", ")}`);
  assert(result.config);
  assert.strictEqual(result.config.preferences.fail_fast, true);
  assert(result.config.preferences.gates.test);
});

test("merges shared.yaml", () => {
  clearConfig();
  setupConfig(
    `
preferences:
  gates:
    test:
      enabled: true
`,
    `
preferences:
  default_branch: main
  report_template: compact
`
  );
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.errors.length, 0);
  assert.strictEqual(result.config.preferences.default_branch, "main");
  assert.strictEqual(result.config.preferences.report_template, "compact");
  assert(result.config.preferences.gates.test);
});

test("verify-branch overrides shared.yaml", () => {
  clearConfig();
  setupConfig(
    `
preferences:
  report_template: detailed
`,
    `
preferences:
  report_template: compact
`
  );
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.errors.length, 0);
  assert.strictEqual(result.config.preferences.report_template, "detailed");
});

test("returns error for corrupted verify-branch.yaml", () => {
  clearConfig();
  setupConfig(`
preferences:
  fail_fast: true
  gates:
    test:
      enabled: true
  unclosed: [
`);
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.config, null);
  assert(result.errors.length > 0);
  assert(result.errors.some((e) => e.includes("verify-branch.yaml")));
});

test("returns error for corrupted shared.yaml", () => {
  clearConfig();
  setupConfig(
    `preferences:
  fail_fast: true
`,
    `preferences:
  report_template: compact
  unclosed: [
`
  );
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.config, null);
  assert(result.errors.some((e) => e.includes("shared.yaml")));
});

test("returns empty config when files are missing", () => {
  clearConfig();
  const result = loadConfig(TEST_DIR);
  assert.strictEqual(result.errors.length, 0);
  assert.deepStrictEqual(result.config, {});
});

test("merges user-level config", () => {
  clearConfig();
  const userDir = path.join(TEST_DIR, "user-home", ".agents", "config");
  fs.mkdirSync(userDir, { recursive: true });
  fs.writeFileSync(
    path.join(userDir, "shared.yaml"),
    `preferences:\n  default_branch: develop\n  report_template: compact\n`
  );
  setupConfig(`
preferences:
  gates:
    test:
      enabled: true
`);

  const originalHomedir = os.homedir;
  os.homedir = () => path.join(TEST_DIR, "user-home");
  const result = loadConfig(TEST_DIR);
  os.homedir = originalHomedir;

  assert.strictEqual(result.errors.length, 0);
  assert.strictEqual(result.config.preferences.default_branch, "develop");
  assert.strictEqual(result.config.preferences.report_template, "compact");
  assert(result.config.preferences.gates.test);
});

test("deepMerge merges nested objects", () => {
  const result = deepMerge(
    { preferences: { gates: { test: { enabled: false } }, report_template: "compact" } },
    { preferences: { gates: { test: { enabled: true } } } }
  );
  assert.strictEqual(result.preferences.gates.test.enabled, true);
  assert.strictEqual(result.preferences.report_template, "compact");
});

fs.rmSync(TEST_DIR, { recursive: true, force: true });
