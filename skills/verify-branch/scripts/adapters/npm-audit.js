#!/usr/bin/env node
/**
 * Adapter: npm-audit
 *
 * Runs `npm audit --json` and reports known vulnerabilities.
 */

const {
  readInput,
  validateInput,
  runCommand,
  resolveCwd,
  createResult,
} = require("./lib/adapter-utils");

function parseAuditResults(parsed) {
  const findings = [];
  const vulns = parsed.vulnerabilities || {};
  for (const [packageName, info] of Object.entries(vulns)) {
    const severity = info.severity || "moderate";
    const via = Array.isArray(info.via) ? info.via : [info.via];
    for (const source of via) {
      if (typeof source !== "object") continue;
      findings.push({
        file: "package.json",
        line: 0,
        rule: `npm-audit:${severity}`,
        severity: severity === "critical" || severity === "high" ? "error" : "warning",
        message: `${packageName}@${info.range || "?"}: ${source.title || "Vulnerability detected"}`,
        introduced: true,
      });
    }
  }
  return findings;
}

async function main() {
  const input = validateInput(await readInput());
  const { project_root, config } = input;

  const command = config.command || ["npm", "audit", "--json"];
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
        "npm audit timed out.",
        err.message
      )));
      return;
    }
    console.log(JSON.stringify(createResult(
      "SKIPPED",
      [],
      `npm audit could not run: ${err.message}`,
      err.message
    )));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(stdout || "{}");
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `Invalid JSON from npm audit: ${err.message}`,
      stdout + stderr
    )));
    return;
  }

  const findings = parseAuditResults(parsed);

  // npm audit exits non-zero when vulnerabilities exist. If we parsed no
  // vulnerabilities and the tool itself failed, report ERROR rather than
  // SKIPPED so that real audit failures (e.g. registry unreachable, malformed
  // config) are not masked.
  let status;
  if (findings.length > 0) {
    status = "FAIL";
  } else if (exitCode === 0) {
    status = "PASS";
  } else {
    const knownBenign = stderr && /npm.*audit.*(fix|update)/i.test(stderr);
    status = knownBenign ? "PASS" : "ERROR";
  }

  const summary = findings.length > 0
    ? `${findings.length} vulnerability(ies) found by npm audit.`
    : status === "ERROR"
    ? `npm audit failed with exit code ${exitCode}: ${stderr || stdout}`.trim()
    : "No vulnerabilities reported by npm audit.";

  console.log(JSON.stringify(createResult(status, findings, summary, stdout + stderr)));
}

main().catch((err) => {
  console.log(JSON.stringify(createResult("ERROR", [], `Adapter error: ${err.message}`, err.stack || "")));
  process.exit(0);
});
