#!/usr/bin/env node
/**
 * Adapter: eslint-sonarjs
 * Category: static-analysis/complexity
 *
 * Runs `npx eslint --rule 'sonarjs/cognitive-complexity: [error, 15]' --format json`
 * (or a configured override) and parses ESLint JSON output for complexity
 * violations introduced on changed files.
 *
 * Input contract:  { changed_files, base_branch, config, project_root }
 * Output contract: { status, findings, summary, raw_output }
 */
const {
  readInput,
  validateInput,
  runCommand,
  resolveCwd,
  createResult,
  isChangedFile,
  statusFromFindings,
} = require("../../lib/adapter-utils");

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, config, project_root } = input;

  const threshold = (config && config.threshold) || 15;
  const command = (config && config.command) || [
    "npx",
    "--yes",
    "eslint",
    "--rule",
    `sonarjs/cognitive-complexity: [error, ${threshold}]`,
    "--format",
    "json",
    ".",
  ];

  const [cmd, ...args] = Array.isArray(command) ? command : [command];

  let rawOutput;
  let exitCode;
  try {
    const cwd = resolveCwd(project_root, config && config.cwd);
    const timeout = (config && config.timeout ? config.timeout : 300) * 1000;
    const result = await runCommand(cmd, args, cwd, timeout);
    rawOutput = result.stdout;
    exitCode = result.exitCode;
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `eslint could not run: ${err.message}`,
      err.message
    )));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(rawOutput || "[]");
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `Invalid JSON from eslint: ${err.message}`,
      rawOutput
    )));
    return;
  }

  const findings = [];
  for (const fileResult of parsed) {
    const filePath = (fileResult.filePath || "").replace(/\\/g, "/");
    for (const message of (fileResult.messages || [])) {
      if (!message.ruleId || !message.ruleId.includes("complexity")) continue;
      if (filePath && !isChangedFile(filePath, changed_files, project_root)) continue;

      findings.push({
        file: filePath,
        line: message.line || 0,
        rule: message.ruleId,
        severity: message.severity === 2 ? "error" : (message.severity === 1 ? "warning" : "error"),
        message: message.message || "Complexity rule violation",
        introduced: true,
      });
    }
  }

  const status = statusFromFindings(findings, exitCode);
  const summary = findings.length > 0
    ? `${findings.length} introduced complexity finding(s) from eslint`
    : (status === "ERROR" ? "eslint exited with an error" : "No introduced complexity findings from eslint");

  console.log(JSON.stringify(createResult(status, findings, summary, rawOutput)));
}

main().catch((err) => {
  console.log(JSON.stringify(createResult(
    "ERROR",
    [],
    `Adapter error: ${err.message}`,
    err.stack || ""
  )));
  process.exit(0);
});
