const assert = require("assert");
const { planExecution, topologicalSort, filterByMode, filterByTags } = require("../../lib/plan-execution");

function test(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
  } catch (err) {
    console.error(`  ✗ ${name}: ${err.message}`);
    process.exitCode = 1;
  }
}

console.log("plan-execution tests");

test("runs all enabled gates in full mode", () => {
  const result = planExecution({
    preferences: {
      execution_mode: "full",
      gates: {
        test: { enabled: true, importance: "required" },
        standards: { enabled: true, importance: "required" },
        style: { enabled: true, importance: "optional" },
      },
    },
  });
  assert.deepStrictEqual(result.gates, ["test", "standards", "style"]);
  assert.strictEqual(result.errors.length, 0);
});

test("quick mode skips optional gates without fast tag", () => {
  const result = planExecution({
    preferences: {
      execution_mode: "quick",
      gates: {
        test: { enabled: true, importance: "required", tags: ["fast"] },
        standards: { enabled: true, importance: "required" },
        style: { enabled: true, importance: "optional" },
        security: { enabled: true, importance: "optional", tags: ["security"] },
      },
    },
  });
  assert(result.gates.includes("test"));
  assert(result.gates.includes("standards"));
  assert(!result.gates.includes("style"));
  assert(!result.gates.includes("security"));
  assert(result.skipped.some((s) => s.gate === "style"));
});

test("security-audit mode only includes security gates", () => {
  const result = planExecution({
    preferences: {
      execution_mode: "security-audit",
      gates: {
        test: { enabled: true, importance: "required" },
        security: { enabled: true, importance: "optional", tags: ["security"] },
        npm_audit: { enabled: true, importance: "optional", tags: ["security"] },
      },
    },
  });
  assert.deepStrictEqual(result.gates.sort(), ["npm_audit", "security"]);
  assert(result.skipped.some((s) => s.gate === "test"));
});

test("filters by required tags", () => {
  const result = planExecution({
    preferences: {
      tags: ["fast"],
      gates: {
        test: { enabled: true, tags: ["fast"] },
        style: { enabled: true, tags: ["style"] },
      },
    },
  });
  assert.deepStrictEqual(result.gates, ["test"]);
  assert(result.skipped.some((s) => s.gate === "style"));
});

test("orders gates by dependencies", () => {
  const result = planExecution({
    preferences: {
      gates: {
        deploy: { enabled: true, depends_on: ["test"] },
        test: { enabled: true, depends_on: ["lint"] },
        lint: { enabled: true },
      },
    },
  });
  assert.deepStrictEqual(result.gates, ["lint", "test", "deploy"]);
});

test("detects circular dependencies", () => {
  const result = planExecution({
    preferences: {
      gates: {
        a: { enabled: true, depends_on: ["b"] },
        b: { enabled: true, depends_on: ["a"] },
      },
    },
  });
  assert(result.errors.length > 0);
});

test("detects self-dependency", () => {
  const result = planExecution({
    preferences: {
      gates: {
        a: { enabled: true, depends_on: ["a"] },
      },
    },
  });
  assert(result.errors.some((e) => e.reason.includes("depends on itself")));
});

test("skips disabled gates", () => {
  const result = planExecution({
    preferences: {
      gates: {
        test: { enabled: true },
        style: { enabled: false },
      },
    },
  });
  assert.deepStrictEqual(result.gates, ["test"]);
  assert(result.skipped.some((s) => s.gate === "style" && s.reason === "gate is disabled"));
});
