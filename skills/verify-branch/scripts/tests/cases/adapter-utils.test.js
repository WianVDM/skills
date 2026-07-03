const assert = require("assert");
const path = require("path");
const { runCommand, shellQuote, statusFromFindings } = require("../../adapters/lib/adapter-utils");

const PROJECT_ROOT = path.join(__dirname, "..", "..", "..");

function test(name, fn) {
  return fn()
    .then(() => console.log(`  ✓ ${name}`))
    .catch((err) => {
      console.error(`  ✗ ${name}: ${err.message}`);
      process.exitCode = 1;
    });
}

async function main() {
  console.log("adapter-utils tests");

  await test("runCommand executes array arguments", async () => {
    const result = await runCommand("node", ["-e", "console.log('hello')"], PROJECT_ROOT, 10000);
    assert.strictEqual(result.exitCode, 0, `expected exit 0, got ${result.exitCode}`);
    assert(result.stdout.includes("hello"), `expected stdout to include hello, got ${result.stdout}`);
  });

  await test("runCommand executes legacy string command", async () => {
    const result = await runCommand("node -e \"console.log('legacy')\"", PROJECT_ROOT, 10000);
    assert.strictEqual(result.exitCode, 0, `expected exit 0, got ${result.exitCode}`);
    assert(result.stdout.includes("legacy"), `expected stdout to include legacy, got ${result.stdout}`);
  });

  await test("runCommand does not allow shell injection through arguments", async () => {
    const injected = "foo; echo injected";
    const result = await runCommand(
      "node",
      ["-e", "console.log(process.argv[1])", injected],
      PROJECT_ROOT,
      10000
    );
    assert.strictEqual(result.exitCode, 0, `expected exit 0, got ${result.exitCode}`);
    assert.strictEqual(result.stderr.trim(), "", `expected no stderr, got ${result.stderr}`);
    assert(result.stdout.includes(injected), `expected stdout to include literal argument, got ${result.stdout}`);
  });

  await test("runCommand forwards env", async () => {
    const result = await runCommand(
      "node",
      ["-e", "console.log(process.env.VB_TEST_VAR)"],
      PROJECT_ROOT,
      10000,
      { VB_TEST_VAR: "verify-branch" }
    );
    assert.strictEqual(result.exitCode, 0, `expected exit 0, got ${result.exitCode}`);
    assert(result.stdout.includes("verify-branch"), `expected stdout to include env value, got ${result.stdout}`);
  });

  await test("runCommand times out and kills the process", async () => {
    try {
      await runCommand("node", ["-e", "setTimeout(()=>{}, 10000)"], PROJECT_ROOT, 50);
      assert.fail("expected timeout rejection");
    } catch (err) {
      assert(err.message.includes("timed out"), `expected timeout message, got ${err.message}`);
    }
  });

  await test("shellQuote escapes shell metacharacters", async () => {
    assert.strictEqual(shellQuote("hello"), "hello");
    assert.strictEqual(shellQuote("foo'bar"), "'foo'\\''bar'");
    assert.strictEqual(shellQuote("foo; bar"), "'foo; bar'");
  });

  await test("statusFromFindings maps findings and exit codes correctly", async () => {
    assert.strictEqual(statusFromFindings([], 0), "PASS");
    assert.strictEqual(statusFromFindings([{ severity: "error" }], 0), "FAIL");
    assert.strictEqual(statusFromFindings([], 1), "ERROR");
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
