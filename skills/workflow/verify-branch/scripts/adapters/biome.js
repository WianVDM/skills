#!/usr/bin/env node
/**
 * Adapter: biome
 *
 * Runs `npx @biomejs/biome check --reporter=json` on changed files and reports
 * lint and format findings.
 */

const {
  readInput,
  validateInput,
  runCommand,
  resolveCwd,
  createResult,
  normalizeFilePath,
  isChangedFile,
} = require("./lib/adapter-utils");

function flattenBiomeFindings(parsed) {
  const findings = [];
  const files = parsed.files || [];
  for (const file of files) {
    for (const diag of file.diagnostics || []) {
      findings.push({
        filePath: file.path || "",
        line: diag.location?.line || 0,
        rule: diag.category || "biome:unknown",
        severity: diag.severity === "error" ? "error" : "warning",
        message: diag.description || diag.message || "Biome issue",
      });
    }
  }
  return findings;
}

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, project_root, config } = input;

  const filePaths = changed_files
    .map((f) => (typeof f === "string" ? f : f.path))
    .filter((f) => f.endsWith(".js") || f.endsWith(".jsx") || f.endsWith(".ts") || f.endsWith(".tsx"));

  const command = config.command || ["npx", "--yes", "@biomejs/biome", "check", "--reporter=json", ...(filePaths.length ? filePaths : ["."])];
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
      console.log(JSON.stringify(createResult("ERROR", [], "biome timed out.", err.message)));
      return;
    }
    console.log(JSON.stringify(createResult("SKIPPED", [], `biome could not run: ${err.message}`, err.message)));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(stdout || "{}");
  } catch (err) {
    console.log(JSON.stringify(createResult("ERROR", [], `Invalid JSON from biome: ${err.message}`, stdout + stderr)));
    return;
  }

  const candidates = flattenBiomeFindings(parsed);
  const findings = [];
  for (const item of candidates) {
    const filePath = normalizeFilePath(item.filePath, project_root);
    if (filePath && !isChangedFile(filePath, changed_files, project_root)) continue;
    findings.push({
      file: filePath || "",
      line: item.line,
      rule: item.rule,
      severity: item.severity,
      message: item.message,
      introduced: true,
    });
  }

  const status = findings.length > 0 ? "FAIL" : "PASS";
  const summary = findings.length > 0 ? `${findings.length} Biome finding(s) in changed files.` : "No Biome findings in changed files.";

  console.log(JSON.stringify(createResult(status, findings, summary, stdout + stderr)));
}

main().catch((err) => {
  console.log(JSON.stringify(createResult("ERROR", [], `Adapter error: ${err.message}`, err.stack || "")));
  process.exit(0);
});
