#!/usr/bin/env node
/**
 * Adapter: eslint
 *
 * Runs `npx eslint --format json` on changed files and reports lint findings.
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

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, project_root, config } = input;

  const filePaths = changed_files
    .map((f) => typeof f === "string" ? f : f.path)
    .filter((f) => f.endsWith(".js") || f.endsWith(".jsx") || f.endsWith(".ts") || f.endsWith(".tsx"));

  const command = config.command || ["npx", "--yes", "eslint", "--format", "json", ...(filePaths.length ? filePaths : ["."])];
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
      console.log(JSON.stringify(createResult("ERROR", [], "eslint timed out.", err.message)));
      return;
    }
    console.log(JSON.stringify(createResult("SKIPPED", [], `eslint could not run: ${err.message}`, err.message)));
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(stdout || "[]");
  } catch (err) {
    console.log(JSON.stringify(createResult("ERROR", [], `Invalid JSON from eslint: ${err.message}`, stdout + stderr)));
    return;
  }

  const results = Array.isArray(parsed) ? parsed : [];
  const findings = [];
  for (const fileResult of results) {
    const filePath = normalizeFilePath(fileResult.filePath, project_root);
    if (filePath && !isChangedFile(filePath, changed_files, project_root)) continue;

    for (const msg of fileResult.messages || []) {
      findings.push({
        file: filePath || "",
        line: msg.line || 0,
        rule: `eslint:${msg.ruleId || "unknown"}`,
        severity: msg.severity === 2 ? "error" : "warning",
        message: msg.message || "ESLint issue",
        introduced: true,
      });
    }
  }

  const status = findings.length > 0 ? "FAIL" : "PASS";
  const summary = findings.length > 0
    ? `${findings.length} ESLint finding(s) in changed files.`
    : "No ESLint findings in changed files.";

  console.log(JSON.stringify(createResult(status, findings, summary, stdout + stderr)));
}

main().catch((err) => {
  console.log(JSON.stringify(createResult("ERROR", [], `Adapter error: ${err.message}`, err.stack || "")));
  process.exit(0);
});
