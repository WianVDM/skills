const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const TEST_DIR = path.join(__dirname, "cases");

function runTestFile(filePath) {
  return new Promise((resolve) => {
    const child = spawn("node", [filePath], {
      cwd: process.cwd(),
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("close", (code) => {
      resolve({ file: filePath, code, stdout, stderr });
    });
  });
}

async function main() {
  const files = fs
    .readdirSync(TEST_DIR)
    .filter((f) => f.endsWith(".test.js"))
    .map((f) => path.join(TEST_DIR, f))
    .sort();

  if (files.length === 0) {
    console.log("No tests found.");
    process.exit(0);
  }

  const results = [];
  for (const file of files) {
    results.push(await runTestFile(file));
  }

  let passed = 0;
  let failed = 0;

  for (const result of results) {
    const name = path.basename(result.file);
    if (result.code === 0) {
      console.log(`✓ ${name}`);
      passed++;
    } else {
      console.log(`✗ ${name}`);
      console.log(result.stdout);
      console.error(result.stderr);
      failed++;
    }
  }

  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

main();
