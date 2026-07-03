#!/usr/bin/env node
/**
 * Adapter: ts-unused
 * Category: static-analysis/dead-code
 *
 * Uses the TypeScript compiler API to detect unused locals, imports, and
 * parameters in changed .ts files. This is a zero-external-dependency adapter
 * that loads the project's own TypeScript installation from node_modules.
 *
 * Input contract:  { changed_files, base_branch, config, project_root }
 * Output contract: { status, findings, summary, raw_output }
 */
const fs = require("fs");
const path = require("path");
const {
  readInput,
  validateInput,
  createResult,
  isChangedFile,
} = require("../../lib/adapter-utils");

const RELEVANT_CODES = new Set([6133, 6138, 6196]);

const IGNORED_MESSAGE_PATTERNS = [
  /'_\w+' is declared but (its value is )?never read/,
];

function isIgnoredMessage(message) {
  return IGNORED_MESSAGE_PATTERNS.some((re) => re.test(message));
}

function codeToRule(code) {
  if (code === 6133) return "unused_local";
  if (code === 6138) return "unused_parameter";
  if (code === 6196) return "unused_export";
  return "unused_identifier";
}

function resolveTsconfig(projectRoot) {
  const candidate = path.join(projectRoot, "tsconfig.json");
  if (fs.existsSync(candidate)) return candidate;

  let dir = projectRoot;
  while (dir !== path.dirname(dir)) {
    const p = path.join(dir, "tsconfig.json");
    if (fs.existsSync(p)) return p;
    dir = path.dirname(dir);
  }
  return null;
}

async function main() {
  const input = validateInput(await readInput());
  const { changed_files, project_root } = input;

  const changedTsFiles = changed_files
    .map((f) => (typeof f === "string" ? f : f.path))
    .filter((p) => p.endsWith(".ts") && !p.endsWith(".d.ts"));

  if (changedTsFiles.length === 0) {
    console.log(JSON.stringify(createResult(
      "NOT_APPLICABLE",
      [],
      "No changed .ts files to analyze"
    )));
    return;
  }

  const configPath = resolveTsconfig(project_root);
  if (!configPath) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      "Could not find tsconfig.json",
      ""
    )));
    return;
  }

  let ts;
  try {
    const tsPath = require.resolve("typescript", { paths: [project_root] });
    ts = require(tsPath);
  } catch {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      "typescript is not available in node_modules",
      ""
    )));
    return;
  }

  const configDir = path.dirname(configPath);
  const configFile = ts.readConfigFile(configPath, ts.sys.readFile);
  const parsedConfig = ts.parseJsonConfigFileContent(
    configFile.config,
    ts.sys,
    configDir
  );

  const compilerOptions = {
    ...parsedConfig.options,
    noUnusedLocals: true,
    noUnusedParameters: true,
    noEmit: true,
  };

  const absoluteFiles = changedTsFiles.map((f) => path.resolve(project_root, f));

  let program;
  let diagnostics;
  try {
    program = ts.createProgram(absoluteFiles, compilerOptions);
    diagnostics = ts.getPreEmitDiagnostics(program);
  } catch (err) {
    console.log(JSON.stringify(createResult(
      "ERROR",
      [],
      `TypeScript error: ${err.message}`,
      err.stack || ""
    )));
    return;
  }

  const findings = [];
  const rawLines = [];

  for (const diagnostic of diagnostics) {
    if (!diagnostic.file || diagnostic.start === undefined) continue;

    const fileName = diagnostic.file.fileName;
    const relativePath = path.relative(project_root, fileName).replace(/\\/g, "/");

    if (!isChangedFile(relativePath, changed_files, project_root)) continue;

    const code = diagnostic.code;
    if (!RELEVANT_CODES.has(code)) continue;

    const message = ts.flattenDiagnosticMessageText(diagnostic.messageText, "\n");
    if (isIgnoredMessage(message)) continue;

    const line = diagnostic.file.getLineAndCharacterOfPosition(diagnostic.start).line + 1;

    findings.push({
      file: relativePath,
      line,
      rule: codeToRule(code),
      severity: "error",
      message,
      introduced: true,
    });

    rawLines.push(`${relativePath}:${line} TS${code}: ${message}`);
  }

  const status = findings.length > 0 ? "FAIL" : "PASS";
  const summary = findings.length > 0
    ? `${findings.length} introduced dead-code finding(s)`
    : "No introduced dead-code findings";

  console.log(JSON.stringify(createResult(
    status,
    findings,
    summary,
    rawLines.join("\n")
  )));
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
