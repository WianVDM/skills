const assert = require("assert");
const path = require("path");
const { spawn } = require("child_process");

const PROJECT_ROOT = path.join(__dirname, "..", "..", "..");
const PYTHON_DIR = path.join(PROJECT_ROOT, "scripts", "tests", "python");

function runPythonTests() {
  return new Promise((resolve) => {
    const child = spawn(
      "python",
      ["-m", "unittest", "discover", "-s", PYTHON_DIR, "-p", "test_*.py"],
      {
        cwd: PROJECT_ROOT,
        env: process.env,
        stdio: ["ignore", "pipe", "pipe"],
      }
    );

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("close", (code) => {
      resolve({ code, stdout, stderr });
    });
  });
}

async function main() {
  console.log("python-scripts tests");
  const result = await runPythonTests();
  if (result.code !== 0) {
    console.error("  ✗ python unit tests failed");
    console.error(result.stdout);
    console.error(result.stderr);
    process.exitCode = 1;
    return;
  }
  console.log("  ✓ python unit tests passed");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
