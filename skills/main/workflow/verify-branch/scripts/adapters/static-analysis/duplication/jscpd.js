#!/usr/bin/env node
/**
 * Adapter: jscpd
 * Category: static-analysis/duplication
 *
 * Runs `npx jscpd --format json --min-lines 5 --sources .`
 * (or a configured override) and parses duplication findings for changed files.
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

  const minLines = (config && config.min_lines) || 5;
  const command = (config && config.command) || [
    "npx",
    "--yes",
    "jscpd",
    "--format",
    "json",
    "--min-lines",
    String(minLines),
    "--sources",
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
      `jscpd could not run: ${err.message}`,
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
      `Invalid JSON from jscpd: ${err.message}`,
      rawOutput
    )));
    return;
  }

  const findings = [];
  const duplicates = parsed.duplicates || parsed.clones || parsed.matches || [];

  for (const dup of duplicates) {
    const firstFile = (dup.firstFile && dup.firstFile.name) || dup.source || dup.first || "";
    const secondFile = (dup.secondFile && dup.secondFile.name) || dup.target || dup.second || "";
    const firstLine = (dup.firstFile && dup.firstFile.start) || dup.firstFileLine || dup.firstLine || 0;
    const secondLine = (dup.secondFile && dup.secondFile.start) || dup.secondFileLine || dup.secondLine || 0;
    const lines = dup.lines || dup.lineCount || 0;

    const relevant = isChangedFile(firstFile, changed_files, project_root) ||
      isChangedFile(secondFile, changed_files, project_root);

    if (!relevant) continue;

    findings.push({
      file: firstFile.replace(/\\/g, "/"),
      line: firstLine,
      rule: "duplicate_block",
      severity: "error",
      message: `Duplicate block of ${lines} lines also in ${secondFile.replace(/\\/g, "/")}:${secondLine}`,
      introduced: true,
    });
  }

  const status = statusFromFindings(findings, exitCode);
  const summary = findings.length > 0
    ? `${findings.length} introduced duplication finding(s) from jscpd`
    : (status === "ERROR" ? "jscpd exited with an error" : "No introduced duplication findings from jscpd");

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
