#!/usr/bin/env node
/**
 * Adapter: snyk
 *
 * Runs `snyk test --json` and reports security findings.
 */

const {
  readInput,
  validateInput,
  runCommand,
  resolveCwd,
  createResult,
} = require("./lib/adapter-utils");

function parseSnykResults(parsed) {
  const findings = [];
  const vulnerabilities = Array.isArray(parsed.vulnerabilities) ? parsed.vulnerabilities : [];
  for (const vuln of vulnerabilities) {
    findings.push({
      file: vuln.from ? vuln.from.join(" > ") : "package.json",
      line: 0,
      rule: `snyk:${vuln.severity || "unknown"}`,
      severity: vuln.severity === "critical" || vuln.severity === "high" ? "error" : "warning",
      message: `${vuln.title || "Vulnerability"} in ${vuln.packageName || "?"}@${vuln.version || "?"}`,
      introduced: true,
    });
  }
  return findings;
}

async function main() {
  const input = validateInput(await readInput());
  const { project_root, config } = input;

  const command = config.command || ["snyk", "test", "--json"];
  const cwd = resolveCwd(project_root, config.cwd);
  const timeoutMs = (config.timeout || 300) * 1000;

  const [cmd, ...args] = Array.isArray(command) ? command : [command];

  let stdout, stderr, exitCode;
  try {
    const result = await runCommand(cmd, args, cwd, timeoutMs);
    stdout = result.stdout;
    stderr = result.stderr;
    exitCode = result.exitCode;
  } catch (err) {
    if (err.message.includes("timed out")) {
      console.log(JSON.stringify(createResult(
        "ERROR",
        [],
        "snyk test timed out.",
        err.message
      )));
      return;
    }
    console.log(JSON.stringify(createResult(
      "SKIPPED",
      [],
      `snyk could not run: ${err.message}`,
      err.message
    )));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(stdout || "{}");
  } catch (err) {
    // Snyk may print non-JSON error messages.
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `Invalid JSON from snyk: ${err.message}`,
      stdout + stderr
    )));
    return;
  }

  const findings = parseSnykResults(parsed);

  // Snyk exits non-zero when vulnerabilities are found. If no vulnerabilities
  // were parsed and the exit code was non-zero, the scan itself failed and
  // should be reported as ERROR rather than silently skipped.
  let status;
  if (findings.length > 0) {
    status = "FAIL";
  } else if (exitCode === 0) {
    status = "PASS";
  } else {
    status = "ERROR";
  }

  const summary = findings.length > 0
    ? `${findings.length} vulnerability(ies) found by snyk.`
    : status === "ERROR"
    ? `snyk test failed with exit code ${exitCode}: ${stderr || stdout}`.trim()
    : "No vulnerabilities reported by snyk.";

  console.log(JSON.stringify(createResult(status, findings, summary, stdout + stderr)));
}

main().catch((err) => {
  console.log(JSON.stringify(createResult("ERROR", [], `Adapter error: ${err.message}`, err.stack || "")));
  process.exit(0);
});
