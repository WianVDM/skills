const assert = require("assert");
const path = require("path");
const { spawn } = require("child_process");

const RUN_GATE = path.join(__dirname, "..", "..", "run-gate.js");
const PROJECT_ROOT = path.join(__dirname, "..", "..", ".."); // skill root

function runGate(input, cliAdapter = null) {
  return new Promise((resolve) => {
    const args = [RUN_GATE];
    if (cliAdapter) {
      args.push("--gate", "test", "--adapter", cliAdapter);
    } else {
      args.push("--gate", "test");
    }
    const child = spawn("node", args, {
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
  console.log("run-gate tests");

  await test("run-gate executes custom-command that echoes and passes", async () => {
    const result = await runGate({
      project_root: PROJECT_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        command: "echo hello",
        cwd: ".",
        timeout: 10,
      },
    }, "custom-command");
    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "PASS", `expected PASS, got ${result.output.status}`);
  });

  await test("run-gate returns ERROR when adapter is missing", async () => {
    const result = await runGate({
      project_root: PROJECT_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        adapter: "does-not-exist",
        cwd: ".",
        timeout: 10,
      },
    });
    assert.strictEqual(result.code, 1, `expected exit 1, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "ERROR", `expected ERROR, got ${result.output.status}`);
  });

  await test("run-gate uses fallback adapters", async () => {
    const result = await runGate({
      project_root: PROJECT_ROOT,
      base_branch: "origin/main",
      changed_files: [],
      config: {
        adapter: "does-not-exist",
        fallback_adapters: ["custom-command"],
        command: "echo fallback",
        cwd: ".",
        timeout: 10,
      },
    });
    assert.strictEqual(result.code, 0, `expected exit 0, got ${result.code}`);
    assert(result.output, "expected parsed output");
    assert.strictEqual(result.output.status, "PASS", `expected PASS, got ${result.output.status}`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
