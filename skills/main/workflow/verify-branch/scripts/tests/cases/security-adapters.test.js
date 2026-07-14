const assert = require("assert");
const path = require("path");
const { spawn } = require("child_process");

const SKILL_ROOT = path.join(__dirname, "..", "..", "..");

function runAdapter(adapterName, input) {
  return new Promise((resolve) => {
    const adapterPath = path.join(SKILL_ROOT, "scripts", "adapters", `${adapterName}.js`);
    const child = spawn("node", [adapterPath], {
      cwd: SKILL_ROOT,
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
  console.log("security-adapter tests");

  await test("npm-audit returns ERROR when audit exits non-zero with no findings", async () => {
    const result = await runAdapter("npm-audit", {
      project_root: SKILL_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        command: [
          "node",
          "-e",
          "console.log(JSON.stringify({vulnerabilities:{}})); process.exit(1)",
        ],
        cwd: ".",
        timeout: 10,
      },
    });
    assert.strictEqual(result.code, 0, `adapter should exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "ERROR", `expected ERROR, got ${result.output.status}`);
  });

  await test("npm-audit returns FAIL when vulnerabilities are present", async () => {
    const result = await runAdapter("npm-audit", {
      project_root: SKILL_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        command: [
          "node",
          "-e",
          "console.log(JSON.stringify({vulnerabilities:{'lodash':{severity:'high',via:[{title:'Prototype pollution'}]}}})); process.exit(0)",
        ],
        cwd: ".",
        timeout: 10,
      },
    });
    assert.strictEqual(result.code, 0, `adapter should exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "FAIL", `expected FAIL, got ${result.output.status}`);
    assert(result.output.findings.length > 0, "expected findings");
  });

  await test("snyk returns ERROR when snyk exits non-zero with no findings", async () => {
    const result = await runAdapter("snyk", {
      project_root: SKILL_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        command: [
          "node",
          "-e",
          "console.log(JSON.stringify({vulnerabilities:[]})); process.exit(2)",
        ],
        cwd: ".",
        timeout: 10,
      },
    });
    assert.strictEqual(result.code, 0, `adapter should exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "ERROR", `expected ERROR, got ${result.output.status}`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
