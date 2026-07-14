const assert = require("assert");
const { evaluateVerdict, DEFAULT_POLICY } = require("../../lib/evaluate-verdict");

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}: ${err.message}`);
    process.exitCode = 1;
  }
}

console.log("evaluate-verdict tests");

test("all_required: PASS when all required gates pass", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "spec", status: "PASS", importance: "required", findings: [] },
  ];
  const { verdict, reason } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "PASS");
  assert(reason.includes("All required gates passed"));
});

test("all_required: PASS when a required gate is explicitly disabled", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "legacy", status: "SKIPPED", importance: "required", reason: "gate is disabled", findings: [] },
  ];
  const { verdict } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "PASS");
});

test("all_required: FAIL when a required gate is skipped for a reason other than disabled", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "legacy", status: "SKIPPED", importance: "required", reason: "tool not found", findings: [] },
  ];
  const { verdict, reason } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "FAIL");
  assert(reason.includes("skipped"));
});

test("all_required: FAIL when a required gate fails", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "spec", status: "FAIL", importance: "required", findings: [] },
  ];
  const { verdict, reason } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "FAIL");
  assert(reason.includes("1 required gate(s) failed"));
});

test("all_required: FAIL when a required gate errors", () => {
  const results = [
    { gate: "test", status: "ERROR", importance: "required", findings: [] },
  ];
  const { verdict, reason } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "FAIL");
  assert(reason.includes("errored"));
});

test("optional gate failures do not fail by default", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "style", status: "FAIL", importance: "optional", findings: [{ severity: "violation" }] },
  ];
  const { verdict } = evaluateVerdict(results, DEFAULT_POLICY);
  assert.strictEqual(verdict, "PASS");
});

test("threshold: PASS within limits", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "style", status: "FAIL", importance: "required", findings: [{ severity: "violation" }] },
  ];
  const policy = { mode: "threshold", threshold: { max_failures: 1, max_violations: 1 } };
  const { verdict } = evaluateVerdict(results, policy);
  assert.strictEqual(verdict, "PASS");
});

test("threshold: FAIL when violations exceed limit", () => {
  const results = [
    { gate: "test", status: "PASS", importance: "required", findings: [] },
    { gate: "style", status: "FAIL", importance: "required", findings: [{ severity: "violation" }, { severity: "violation" }] },
  ];
  const policy = { mode: "threshold", threshold: { max_violations: 1 } };
  const { verdict } = evaluateVerdict(results, policy);
  assert.strictEqual(verdict, "FAIL");
});

test("any_required: PASS if at least one required gate passes", () => {
  const results = [
    { gate: "test", status: "FAIL", importance: "required", findings: [] },
    { gate: "spec", status: "PASS", importance: "required", findings: [] },
  ];
  const policy = { mode: "any_required" };
  const { verdict } = evaluateVerdict(results, policy);
  assert.strictEqual(verdict, "PASS");
});

test("unknown mode returns FAIL", () => {
  const results = [{ gate: "test", status: "PASS", importance: "required", findings: [] }];
  const { verdict } = evaluateVerdict(results, { mode: "weird" });
  assert.strictEqual(verdict, "FAIL");
});
