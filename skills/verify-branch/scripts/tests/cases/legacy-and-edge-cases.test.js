const assert = require("assert");
const path = require("path");
const { resolveAdapter } = require("../../lib/resolve-adapter");
const { runStandardsCheck } = require("../../lib/standards-engine");
const fs = require("fs");

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

console.log("legacy and edge-case tests");

test("resolves legacy static-analysis/complexity adapter layout", () => {
  const adapterPath = resolveAdapter("eslint-sonarjs", {
    gate: "static-analysis/complexity",
    project_root: PROJECT_ROOT,
  });
  assert(adapterPath, "expected adapter path to be found");
  assert(adapterPath.includes("eslint-sonarjs.js"), `unexpected path: ${adapterPath}`);
});

test("handles very large changed_files list in standards engine", () => {
  const tmpDir = fs.mkdtempSync(path.join(__dirname, "tmp-large-diff-"));
  fs.writeFileSync(
    path.join(tmpDir, "standards.yaml"),
    `rules:\n  - id: no-any\n    category: types\n    severity: violation\n    description: "Avoid using any."\n`
  );

  const changedFiles = [];
  for (let i = 0; i < 500; i++) {
    const fileName = `file-${i}.ts`;
    fs.writeFileSync(path.join(tmpDir, fileName), `const value${i}: string = "${i}";\n`);
    changedFiles.push(fileName);
  }

  const result = runStandardsCheck({
    project_root: tmpDir,
    base_branch: "origin/main",
    changed_files: changedFiles,
    config: {
      sources: [{ type: "yaml", path: "standards.yaml" }],
      overrides: [],
    },
  });

  assert.strictEqual(result.status, "PASS", `expected PASS, got ${result.status}`);
  assert.strictEqual(result.findings.length, 0, `expected no findings, got ${result.findings.length}`);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});

test("handles many changed files with violations", () => {
  const tmpDir = fs.mkdtempSync(path.join(__dirname, "tmp-large-violations-"));
  fs.writeFileSync(
    path.join(tmpDir, "standards.yaml"),
    `rules:\n  - id: no-any\n    category: types\n    severity: violation\n    description: "Avoid using any."\n`
  );

  const changedFiles = [];
  for (let i = 0; i < 50; i++) {
    const fileName = `bad-${i}.ts`;
    fs.writeFileSync(path.join(tmpDir, fileName), `const value${i}: any = ${i};\n`);
    changedFiles.push(fileName);
  }

  const result = runStandardsCheck({
    project_root: tmpDir,
    base_branch: "origin/main",
    changed_files: changedFiles,
    config: {
      sources: [{ type: "yaml", path: "standards.yaml" }],
      overrides: [],
    },
  });

  assert.strictEqual(result.status, "FAIL", `expected FAIL, got ${result.status}`);
  assert(result.findings.length >= 50, `expected at least 50 findings, got ${result.findings.length}`);

  fs.rmSync(tmpDir, { recursive: true, force: true });
});
