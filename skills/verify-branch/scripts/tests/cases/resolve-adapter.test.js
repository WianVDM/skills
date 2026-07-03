const assert = require("assert");
const path = require("path");
const {
  buildAdapterSearchPath,
  resolveAdapter,
  resolveAdapterWithDiagnostics,
} = require("../../lib/resolve-adapter");

const PROJECT_ROOT = path.join(__dirname, "..", "..", ".."); // skill root

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}: ${err.message}`);
    process.exitCode = 1;
  }
}

test("buildAdapterSearchPath includes project paths, skill adapters, and legacy dirs", () => {
  const dirs = buildAdapterSearchPath({ project_root: "/tmp/proj" });
  const dirList = dirs.map((d) => d.replace(/\\/g, "/"));
  assert(dirList.some((d) => d.includes("/tmp/proj/.agents/verify-branch/adapters")), "project adapter dir missing");
  assert(dirList.some((d) => d.includes("/scripts/adapters/test")), "legacy test dir missing");
  assert(dirList.some((d) => d.includes("/scripts/adapters/static-analysis/dead-code")), "legacy static-analysis dir missing");
});

test("resolveAdapter finds built-in npm-test adapter", () => {
  const adapterPath = resolveAdapter("npm-test", { gate: "test", project_root: PROJECT_ROOT });
  assert(adapterPath, "adapter not found");
  assert(adapterPath.endsWith("npm-test.js"), `unexpected path: ${adapterPath}`);
});

test("resolveAdapter finds built-in knip adapter via flat name", () => {
  const adapterPath = resolveAdapter("knip", { gate: "dead-code", project_root: PROJECT_ROOT });
  assert(adapterPath, "adapter not found");
  assert(adapterPath.endsWith("knip.js"), `unexpected path: ${adapterPath}`);
});

test("resolveAdapterWithDiagnostics returns error for unknown adapter", () => {
  const result = resolveAdapterWithDiagnostics("does-not-exist", { gate: "test", project_root: PROJECT_ROOT });
  assert.strictEqual(result.path, null);
  assert(result.error, "expected error message");
  assert(result.searched.length > 0, "expected searched dirs");
});

test("resolveAdapter resolves custom adapter from project adapter path", () => {
  const fs = require("fs");
  const os = require("os");
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "vb-test-"));
  const projDir = path.join(tmpDir, "project");
  const adapterDir = path.join(projDir, ".agents", "verify-branch", "adapters");
  fs.mkdirSync(adapterDir, { recursive: true });
  fs.writeFileSync(path.join(adapterDir, "my-adapter.js"), "module.exports = {};");

  try {
    const adapterPath = resolveAdapter("my-adapter", { gate: "custom", project_root: projDir });
    assert(adapterPath, "custom adapter not found");
    assert(adapterPath.endsWith("my-adapter.js"), `unexpected path: ${adapterPath}`);
  } finally {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
});

console.log("resolve-adapter tests");
