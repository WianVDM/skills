#!/usr/bin/env node
/**
 * Adapter: knip
 * Category: static-analysis/dead-code
 *
 * Runs `npx knip --production --no-exit-code` (or a configured override) and
 * parses the JSON output for unused dependencies, exports, and files.
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

function flattenKnipIssues(parsed) {
  const findings = [];
  for (const [category, issues] of Object.entries(parsed)) {
    if (!Array.isArray(issues)) continue;
    for (const issue of issues) {
      let filePath = "";
      let line = 0;
      let message = "";
      let rule = `knip:${category}`;

      if (typeof issue === "string") {
        message = `${category}: ${issue}`;
      } else {
        filePath = issue.file || issue.path || issue.posixPath || "";
        line = issue.line || issue.lineNumber || 0;
        message = issue.message || issue.name || issue.symbol || `${category} issue`;
        rule = issue.rule || rule;
      }

      findings.push({
        filePath,
        line,
        rule,
        message,
      });
    }
  }
  return findings;
}

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, config, project_root } = input;

  const command = (config && config.command) || [
    "npx",
    "--yes",
    "knip",
    "--production",
    "--no-exit-code",
    "--reporter",
    "json",
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
      `knip could not run: ${err.message}`,
      err.message
    )));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(rawOutput || "{}");
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `Invalid JSON from knip: ${err.message}`,
      rawOutput
    )));
    return;
  }

  const candidates = Array.isArray(parsed)
    ? parsed
    : flattenKnipIssues(parsed);

  const findings = [];
  for (const item of candidates) {
    const filePath = (item.filePath || item.file || "").replace(/\\/g, "/");
    if (filePath && !isChangedFile(filePath, changed_files, project_root)) continue;

    findings.push({
      file: filePath,
      line: item.line || 0,
      rule: item.rule || "unused",
      severity: item.severity || "error",
      message: item.message || "Unused code detected by knip",
      introduced: true,
    });
  }

  const status = statusFromFindings(findings, exitCode);
  const summary = findings.length > 0
    ? `${findings.length} introduced dead-code finding(s) from knip`
    : (status === "ERROR" ? "knip exited with an error" : "No introduced dead-code findings from knip");

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
