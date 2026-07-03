const DEFAULT_POLICY = { mode: "all_required" };

/**
 * Evaluate the overall verdict from gate results and a verdict policy.
 *
 * @param {object[]} gateResults - array of gate results with { gate, status, importance, findings }
 * @param {object} policy - verdict policy from config
 * @returns {object} { verdict: "PASS" | "FAIL", reason: string, details: object }
 */
function evaluateVerdict(gateResults, policy) {
  const p = policy || DEFAULT_POLICY;
  const mode = p.mode || "all_required";

  const required = gateResults.filter((g) => g.importance === "required");
  const optional = gateResults.filter((g) => g.importance !== "required");

  // A gate that is explicitly disabled (enabled: false) should not be treated as
  // a failure, even when it is marked as required. The conductor may record it
  // as SKIPPED with a reason indicating it is disabled.
  function isDisabledGate(g) {
    return (
      g.status === "SKIPPED" &&
      g.reason &&
      g.reason.toLowerCase().includes("disabled")
    );
  }

  const requiredPassed = required.filter(
    (g) => g.status === "PASS" || g.status === "NOT_APPLICABLE" || isDisabledGate(g)
  ).length;
  const requiredFailed = required.filter((g) => g.status === "FAIL").length;
  const requiredErrors = required.filter((g) => g.status === "ERROR").length;
  const requiredSkipped = required.filter(
    (g) => g.status === "SKIPPED" && !isDisabledGate(g)
  ).length;
  const requiredDisabled = required.filter((g) => isDisabledGate(g)).length;

  const optionalPassed = optional.filter(
    (g) => g.status === "PASS" || g.status === "NOT_APPLICABLE"
  ).length;
  const optionalFailed = optional.filter((g) => g.status === "FAIL").length;

  const totalViolationCount = gateResults.reduce((sum, g) => {
    if (!Array.isArray(g.findings)) return sum;
    return sum + g.findings.filter((f) => f.severity === "violation" || f.severity === "error").length;
  }, 0);

  if (mode === "all_required") {
    if (requiredErrors > 0 || requiredSkipped > 0) {
      return {
        verdict: "FAIL",
        reason: `${requiredErrors} required gate(s) errored and ${requiredSkipped} required gate(s) skipped${requiredDisabled > 0 ? ` (${requiredDisabled} disabled gate(s) treated as not applicable)` : ""}.`,
        details: { requiredErrors, requiredSkipped, requiredDisabled },
      };
    }
    if (requiredFailed > 0) {
      return {
        verdict: "FAIL",
        reason: `${requiredFailed} required gate(s) failed.`,
        details: { requiredFailed },
      };
    }
    return {
      verdict: "PASS",
      reason: "All required gates passed.",
      details: { requiredPassed: required.length - requiredDisabled },
    };
  }

  if (mode === "any_required") {
    if (requiredPassed > 0 && requiredErrors === 0) {
      return {
        verdict: "PASS",
        reason: `${requiredPassed} required gate(s) passed with no errors.`,
        details: { requiredPassed, requiredDisabled },
      };
    }
    return {
      verdict: "FAIL",
      reason: "No required gate passed cleanly.",
      details: { requiredPassed, requiredFailed, requiredErrors, requiredSkipped },
    };
  }

  if (mode === "threshold") {
    const t = p.threshold || {};
    const maxFailures = t.max_failures ?? 0;
    const maxErrors = t.max_errors ?? 0;
    const maxViolations = t.max_violations ?? 0;

    if (requiredErrors > maxErrors) {
      return {
        verdict: "FAIL",
        reason: `Required gate errors (${requiredErrors}) exceed threshold (${maxErrors}).`,
        details: { requiredErrors, maxErrors },
      };
    }
    if (requiredFailed > maxFailures) {
      return {
        verdict: "FAIL",
        reason: `Required gate failures (${requiredFailed}) exceed threshold (${maxFailures}).`,
        details: { requiredFailed, maxFailures },
      };
    }
    if (totalViolationCount > maxViolations) {
      return {
        verdict: "FAIL",
        reason: `Total violations (${totalViolationCount}) exceed threshold (${maxViolations}).`,
        details: { totalViolationCount, maxViolations },
      };
    }
    return {
      verdict: "PASS",
      reason: "Within configured thresholds.",
      details: { requiredFailed, requiredErrors, totalViolationCount },
    };
  }

  return {
    verdict: "FAIL",
    reason: `Unknown verdict_policy mode: ${mode}`,
    details: { mode },
  };
}

module.exports = { evaluateVerdict, DEFAULT_POLICY };
