const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { loadState, loadStateForBranch } = require("../../lib/load-state");

const TEST_DIR = fs.mkdtempSync(path.join(__dirname, "tmp-state-"));

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}: ${err.message}`);
    process.exitCode = 1;
  }
}

console.log("load-state tests");

test("returns null state when file is missing", () => {
  const result = loadState(path.join(TEST_DIR, "missing-state.md"));
  assert.strictEqual(result.exists, false);
  assert.strictEqual(result.state, null);
  assert.strictEqual(result.error, null);
});

test("parses valid state file frontmatter", () => {
  const statePath = path.join(TEST_DIR, "feature-x-state.md");
  fs.writeFileSync(
    statePath,
    `---
skill: verify-branch
version: 4
branch: feature-x
base: origin/main
updated_at: 2026-07-01T12:00:00Z
---

## Gate checklist

- [x] test
- [ ] standards
`
  );
  const result = loadState(statePath);
  assert.strictEqual(result.exists, true);
  assert.strictEqual(result.error, null);
  assert(result.state);
  assert.strictEqual(result.state.skill, "verify-branch");
  assert.strictEqual(result.state.version, 4);
  assert(result.state.body.includes("Gate checklist"));
});

test("returns error for corrupted state file", () => {
  const statePath = path.join(TEST_DIR, "corrupt-state.md");
  fs.writeFileSync(
    statePath,
    `---
skill: verify-branch
unclosed: [
---

body
`
  );
  const result = loadState(statePath);
  assert.strictEqual(result.exists, true);
  assert.strictEqual(result.state, null);
  assert(result.error);
});

test("loadStateForBranch constructs the correct path", () => {
  const contextDir = path.join(TEST_DIR, ".agents", "context", "verify-branch");
  fs.mkdirSync(contextDir, { recursive: true });
  const statePath = path.join(contextDir, "feature_OC-1234-state.md");
  fs.writeFileSync(
    statePath,
    `---
skill: verify-branch
version: 4
branch: feature/OC-1234
base: origin/main
updated_at: 2026-07-01T12:00:00Z
---
`
  );
  const result = loadStateForBranch(TEST_DIR, "feature/OC-1234");
  assert.strictEqual(result.exists, true);
  assert.strictEqual(result.state.branch, "feature/OC-1234");
});

fs.rmSync(TEST_DIR, { recursive: true, force: true });
