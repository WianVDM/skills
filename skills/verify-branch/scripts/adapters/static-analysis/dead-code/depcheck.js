#!/usr/bin/env node
/**
 * Adapter: depcheck
 * Category: static-analysis/dead-code
 *
 * Runs `npx depcheck --json` (or a configured override) and parses the JSON
 * output for unused dependencies and missing dependencies.
 *
 * Input contract:  { changed_files, base_branch, config, project_root }
 * Output contract: { status, findings, summary, raw_output }
 */
const fs = require("fs");
const path = require("path");
const {
  readInput,
  validateInput,
  runCommand,
  resolveCwd,
  createResult,
  isChangedFile,
  normalizeFilePath,
  statusFromFindings,
} = require("../../lib/adapter-utils");

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, config, project_root } = input;

  const command = (config && config.command) || ["npx", "--yes", "depcheck", "--json"];

  const [cmd, ...args] = Array.isArray(command) ? command : [command];

  let rawOutput;
  let exitCode;
  try {
    const cwd = resolveCwd(project_root, config && config.cwd);
    const timeout = (config && config.timeout ? config.timeout : 120) * 1000;
    const result = await runCommand(cmd, args, cwd, timeout);
    rawOutput = result.stdout;
    exitCode = result.exitCode;
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `depcheck could not run: ${err.message}`,
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
      `Invalid JSON from depcheck: ${err.message}`,
      rawOutput
    )));
    return;
  }

  const changedPaths = new Set(changed_files.map((f) =>
    normalizeFilePath(typeof f === "string" ? f : f.path, project_root)
  ));
  const packageChanged = changedPaths.has("package.json");
  const manifestPath = fs.existsSync(path.join(project_root, "package.json"))
    ? "package.json"
    : "";

  const findings = [];

  for (const dep of (parsed.dependencies || [])) {
    if (!packageChanged) continue;
    findings.push({
      file: manifestPath,
      line: 0,
      rule: "unused_dependency",
      severity: "error",
      message: `Dependency "${dep}" is unused`,
      introduced: true,
    });
  }

  for (const dep of (parsed.devDependencies || [])) {
    if (!packageChanged) continue;
    findings.push({
      file: manifestPath,
      line: 0,
      rule: "unused_dev_dependency",
      severity: "warning",
      message: `Dev dependency "${dep}" is unused`,
      introduced: true,
    });
  }

  for (const [dep, files] of Object.entries(parsed.missing || {})) {
    for (const filePath of (Array.isArray(files) ? files : [files])) {
      if (!isChangedFile(filePath, changed_files, project_root)) continue;
      findings.push({
        file: filePath,
        line: 0,
        rule: "missing_dependency",
        severity: "error",
        message: `Dependency "${dep}" is used but not declared`,
        introduced: true,
      });
    }
  }

  for (const filePath of Object.keys(parsed.invalidFiles || {})) {
    if (!isChangedFile(filePath, changed_files, project_root)) continue;
    findings.push({
      file: filePath,
      line: 0,
      rule: "invalid_file",
      severity: "error",
      message: `depcheck could not parse ${filePath}`,
      introduced: true,
    });
  }

  const status = statusFromFindings(findings, exitCode);
  const summary = findings.length > 0
    ? `${findings.length} introduced dependency finding(s)`
    : (status === "ERROR" ? "depcheck exited with an error" : "No introduced dependency findings");

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
