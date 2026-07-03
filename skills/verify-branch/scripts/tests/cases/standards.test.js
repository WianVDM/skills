const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const ADAPTER_DIR = path.join(__dirname, "..", "..", "adapters", "standards");
const PROJECT_ROOT = path.join(__dirname, "..", "..", ".."); // skill root

function runAdapter(adapter, input) {
  return new Promise((resolve) => {
    const child = spawn("node", [path.join(ADAPTER_DIR, `${adapter}.js`)], {
      cwd: PROJECT_ROOT,
      env: process.env,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdin.write(JSON.stringify(input));
    child.stdin.end();

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("close", (code) => {
      try {
        const output = JSON.parse(stdout.trim());
        resolve({ code, output, stderr });
      } catch (err) {
        resolve({ code, output: null, raw: stdout, stderr, error: err.message });
      }
    });
  });
}

function test(name, fn) {
  return fn()
    .then(() => console.log(`  ✓ ${name}`))
    .catch((err) => {
      console.error(`  ✗ ${name}: ${err.message}`);
      process.exitCode = 1;
    });
}

async function main() {
  console.log("standards adapter tests");

  const tmpDir = fs.mkdtempSync(path.join(__dirname, "tmp-standards-"));

  await test("yaml-standards returns PASS when no violations", async () => {
    const standardsFile = path.join(tmpDir, "standards.yaml");
    fs.writeFileSync(
      standardsFile,
      `rules:
  - id: no-any
    category: types
    severity: violation
    description: "Avoid using any."
`
    );

    const sourceFile = path.join(tmpDir, "clean.ts");
    fs.writeFileSync(sourceFile, "const value: string = 'hello';\n");

    const result = await runAdapter("yaml-standards", {
      project_root: tmpDir,
      base_branch: "origin/main",
      changed_files: ["clean.ts"],
      config: {
        sources: [{ type: "yaml", path: "standards.yaml" }],
        overrides: [],
      },
    });

    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}; stderr: ${result.stderr}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "PASS", `expected PASS, got ${result.output.status}`);
  });

  await test("yaml-standards detects a violation", async () => {
    const standardsFile = path.join(tmpDir, "standards.yaml");
    fs.writeFileSync(
      standardsFile,
      `rules:
  - id: no-any
    category: types
    severity: violation
    description: "Avoid using any."
`
    );

    const sourceFile = path.join(tmpDir, "bad.ts");
    fs.writeFileSync(sourceFile, "const value: any = 1;\n");

    const result = await runAdapter("yaml-standards", {
      project_root: tmpDir,
      base_branch: "origin/main",
      changed_files: ["bad.ts"],
      config: {
        sources: [{ type: "yaml", path: "standards.yaml" }],
        overrides: [],
      },
    });

    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "FAIL", `expected FAIL, got ${result.output.status}`);
    assert(result.output.findings.length > 0, "expected at least one finding");
    assert(result.output.findings.some((f) => f.rule === "no-any"), "expected no-any finding");
  });

  await test("yaml-standards returns NOT_APPLICABLE when no sources", async () => {
    const result = await runAdapter("yaml-standards", {
      project_root: tmpDir,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        sources: [],
        overrides: [],
      },
    });

    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "NOT_APPLICABLE", `expected NOT_APPLICABLE, got ${result.output.status}`);
  });

  await test("markdown-frontmatter adapter loads rules from frontmatter", async () => {
    const standardsFile = path.join(tmpDir, "standards.md");
    fs.writeFileSync(
      standardsFile,
      `---
rules:
  - id: no-bare-except
    category: reliability
    severity: violation
    description: "Do not use bare except clauses."
---

# Standards

These are our standards.
`
    );

    const sourceFile = path.join(tmpDir, "bad.py");
    fs.writeFileSync(sourceFile, "try:\n    pass\nexcept:\n    pass\n");

    const result = await runAdapter("markdown-frontmatter", {
      project_root: tmpDir,
      base_branch: "origin/main",
      changed_files: ["bad.py"],
      config: {
        sources: [{ type: "markdown-frontmatter", path: "standards.md" }],
        overrides: [],
      },
    });

    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "FAIL", `expected FAIL, got ${result.output.status}`);
    assert(result.output.findings.some((f) => f.rule === "no-bare-except"), "expected no-bare-except finding");
  });

  // Cleanup
  fs.rmSync(tmpDir, { recursive: true, force: true });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
