const assert = require("assert");
const path = require("path");
const { renderReport } = require("../../lib/render-report");

const REPORT_DATA = {
  branch: "feature/OC-1234",
  base: "origin/main",
  commit: "abc1234",
  generated_at: "2026-07-01T12:00:00Z",
  verdict: "FAIL",
  verdict_reason: "1 required gate failed.",
  verdict_details: { requiredFailed: 1 },
  required_gates_passed: 1,
  required_gates_total: 2,
  optional_gates_passed: 1,
  optional_gates_total: 1,
  gate_results: [
    {
      gate: "test",
      importance: "required",
      status: "PASS",
      adapter: "npm-test",
      summary: "All tests passed.",
      findings: [],
      raw_output: "",
    },
    {
      gate: "standards",
      importance: "required",
      status: "FAIL",
      adapter: "yaml-standards",
      summary: "1 violation found.",
      findings: [
        { file: "src/example.ts", line: 42, rule: "no-any", severity: "error", message: "Uses any" },
      ],
      raw_output: "",
    },
    {
      gate: "security",
      importance: "optional",
      status: "PASS",
      adapter: "npm-audit",
      summary: "No vulnerabilities.",
      findings: [],
      raw_output: "",
    },
  ],
  fresh_context: [{ path: ".agents/context/baseline/OC-1234.md", skill: "baseline", summary: "Bug reproduced" }],
  stale_context: [],
};

function test(name, fn) {
  return fn()
    .then(() => console.log(`  ✓ ${name}`))
    .catch((err) => {
      console.error(`  ✗ ${name}: ${err.message}`);
      process.exitCode = 1;
    });
}

async function main() {
  console.log("render-report tests");

  await test("default template renders gate summary and findings", async () => {
    const report = renderReport(REPORT_DATA, "default");
    assert(report.includes("# Branch Verification: feature/OC-1234"));
    assert(report.includes("| test | required | PASS"));
    assert(report.includes("| standards | required | FAIL"));
    assert(report.includes("| src/example.ts | 42 | no-any | error | Uses any"));
    assert(report.includes("verdict: FAIL"));
  });

  await test("compact template is concise", async () => {
    const report = renderReport(REPORT_DATA, "compact");
    assert(report.includes("feature/OC-1234 — FAIL"));
    assert(!report.includes("## Findings"));
    assert(report.includes("Uses any"));
  });

  await test("detailed template includes raw output", async () => {
    const report = renderReport(REPORT_DATA, "detailed");
    assert(report.includes("## Raw details"));
    assert(report.includes("All tests passed."));
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
