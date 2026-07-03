#!/usr/bin/env node
/**
 * Shared utilities for verify-branch static-analysis adapters.
 *
 * All adapters in this skill consume the same input contract and emit the
 * same output shape. This module centralizes input parsing, command running,
 * path normalization, and result formatting so that individual adapters stay
 * focused on tool-specific parsing.
 *
 * Adapter input contract:
 * {
 *   "changed_files": [{ "path": "src/app.ts", "status": "M", "oldPath?": "..." }],
 *   "base_branch": "origin/main",
 *   "config": { ...sub-gate config from verify-branch.yaml... },
 *   "project_root": "/path/to/project"
 * }
 *
 * Adapter output contract:
 * {
 *   "status": "PASS|FAIL|ERROR|NOT_APPLICABLE|SKIPPED",
 *   "findings": [
 *     { "file": "...", "line": 1, "rule": "...", "severity": "error|warning|info",
 *       "message": "...", "introduced": true }
 *   ],
 *   "summary": "...",
 *   "raw_output": "..."
 * }
 */
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const DEFAULT_TIMEOUT_MS = 300000;

/**
 * Quote a single argument for legacy shell string construction. This is a
 * conservative fallback used only when the caller supplies a full shell
 * command string. Prefer passing arguments as an array to runCommand() so they
 * are executed directly without invoking a shell.
 */
function shellQuote(arg) {
  if (typeof arg !== "string") return "";
  if (arg === "") return "''";
  if (/^[a-zA-Z0-9_+\-.,/@:=]+$/.test(arg)) {
    return arg;
  }
  return "'" + arg.replace(/'/g, "'\\''") + "'";
}

/**
 * On Windows, Node's child_process.spawn with shell: false requires the
 * executable to include the correct extension (e.g. .cmd). This helper searches
 * PATH and the literal command path for common extensions and returns the first
 * match. On non-Windows platforms it returns the command unchanged.
 */
function resolveWindowsCommand(command) {
  if (process.platform !== "win32") return command;
  if (!command || typeof command !== "string") return command;

  const extensions = (process.env.PATHEXT || ".EXE;.CMD;.BAT;.PS1").split(";").map((e) => e.toLowerCase());

  // Try the command itself with appended extensions, which handles relative or
  // absolute paths such as node_modules/.bin/eslint on Windows.
  if (!path.extname(command)) {
    for (const ext of extensions) {
      const candidate = command + ext;
      if (fs.existsSync(candidate)) return candidate;
    }
  }

  // Search the PATH environment variable for the command.
  const dirs = (process.env.PATH || "").split(path.delimiter);
  for (const dir of dirs) {
    if (!dir) continue;
    const base = path.join(dir, command);
    if (path.extname(command) && fs.existsSync(base)) return base;
    for (const ext of extensions) {
      const candidate = base + ext;
      if (fs.existsSync(candidate)) return candidate;
    }
  }

  return command;
}

/**
 * Read and parse JSON input from stdin or the last CLI argument.
 */
function readInput() {
  return new Promise((resolve, reject) => {
    const chunks = [];
    process.stdin.on("data", (chunk) => chunks.push(chunk));
    process.stdin.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf-8").trim();
      if (raw) {
        try {
          resolve(JSON.parse(raw));
        } catch (err) {
          reject(new Error(`Invalid JSON from stdin: ${err.message}`));
        }
      } else {
        const lastArg = process.argv[process.argv.length - 1];
        if (lastArg && lastArg.startsWith("{")) {
          try {
            resolve(JSON.parse(lastArg));
          } catch (err) {
            reject(new Error(`Invalid JSON from argument: ${err.message}`));
          }
        } else {
          reject(new Error("No JSON input provided via stdin or argument"));
        }
      }
    });
  });
}

/**
 * Validate the adapter input contract. Throws on missing required fields.
 */
function validateInput(input) {
  if (!input || typeof input !== "object") {
    throw new Error("Input must be an object");
  }
  if (!Array.isArray(input.changed_files)) {
    throw new Error("Input must include 'changed_files' array");
  }
  if (typeof input.base_branch !== "string") {
    throw new Error("Input must include 'base_branch' string");
  }
  if (typeof input.project_root !== "string") {
    throw new Error("Input must include 'project_root' string");
  }
  input.config = input.config || {};
  return input;
}

/**
 * Resolve a path relative to the project root.
 */
function resolveCwd(projectRoot, configCwd) {
  return path.resolve(projectRoot, configCwd || ".");
}

/**
 * Normalize a file path to a forward-slash path relative to the project root.
 */
function normalizeFilePath(filePath, projectRoot) {
  if (!filePath || typeof filePath !== "string") return "";
  const abs = path.resolve(projectRoot, filePath);
  return path.relative(projectRoot, abs).replace(/\\/g, "/");
}

/**
 * Determine whether a given file path is one of the changed files.
 */
function isChangedFile(filePath, changedFiles, projectRoot) {
  const normalized = normalizeFilePath(filePath, projectRoot);
  for (const item of changedFiles) {
    const p = normalizeFilePath(typeof item === "string" ? item : item.path, projectRoot);
    if (p === normalized) return true;
  }
  return false;
}

/**
 * Run a command safely in the given working directory with a timeout.
 *
 * Preferred signature: runCommand(file, args, cwd, timeoutMs)
 *   - file: executable name (e.g. "npx", "npm", "snyk")
 *   - args: array of argument strings (e.g. ["--yes", "eslint", "--format", "json", "."])
 *   - cwd: working directory
 *   - timeoutMs: maximum runtime in milliseconds
 *
 * Legacy signature: runCommand(shellCommand, cwd, timeoutMs)
 *   - shellCommand: full shell command string (e.g. "npm audit --json")
 *   - This path is preserved for user-supplied config.command strings. The command
 *     is treated as trusted input and should never be constructed from untrusted data.
 *
 * When an array of args is provided, the shell is still used (so Windows .cmd files
 * and npx work) but Node.js quotes each argument, preventing shell injection from
 * file paths and other variables.
 *
 * Returns { stdout, stderr, exitCode }. Rejects on spawn failure or timeout.
 */
function runCommand(command, args, cwd, timeoutMs, env) {
  // Legacy signature: runCommand(commandString, cwd, timeoutMs)
  if (args !== undefined && !Array.isArray(args)) {
    if (typeof args === "string") {
      timeoutMs = typeof cwd === "number" ? cwd : timeoutMs;
      cwd = args;
    }
    args = [];
  }
  if (args === undefined) {
    args = [];
  }
  cwd = cwd || process.cwd();
  timeoutMs = timeoutMs || DEFAULT_TIMEOUT_MS;
  const mergedEnv = env && typeof env === "object" ? { ...process.env, ...env } : process.env;

  const useShell = args.length === 0;

  return new Promise((resolve, reject) => {
    const child = useShell
      ? spawn(command, {
          cwd,
          shell: true,
          stdio: ["pipe", "pipe", "pipe"],
          env: mergedEnv,
        })
      : spawn(resolveWindowsCommand(command), args, {
          cwd,
          shell: false,
          stdio: ["pipe", "pipe", "pipe"],
          env: mergedEnv,
        });

    let stdout = "";
    let stderr = "";
    let killed = false;
    let killTimer = null;

    const timer = setTimeout(() => {
      killed = true;
      child.kill("SIGTERM");
      killTimer = setTimeout(() => child.kill("SIGKILL"), 5000);
    }, timeoutMs);

    child.stdout.on("data", (d) => {
      stdout += d.toString("utf-8");
    });
    child.stderr.on("data", (d) => {
      stderr += d.toString("utf-8");
    });

    child.on("error", (err) => {
      clearTimeout(timer);
      if (killTimer) clearTimeout(killTimer);
      reject(err);
    });

    child.on("close", (code) => {
      clearTimeout(timer);
      if (killTimer) clearTimeout(killTimer);
      if (killed) {
        const argsSummary = args.length > 0 ? args.join(" ") : "(shell command)";
        reject(new Error(`Command timed out after ${timeoutMs}ms: ${command} ${argsSummary}`));
        return;
      }
      resolve({ stdout, stderr, exitCode: code });
    });
  });
}

/**
 * Normalize a single finding to the adapter output contract.
 */
function normalizeFinding(finding) {
  return {
    file: finding.file || "",
    line: typeof finding.line === "number" ? finding.line : 0,
    rule: finding.rule || "unknown",
    severity: ["error", "warning", "info"].includes(finding.severity) ? finding.severity : "error",
    message: finding.message || "",
    introduced: finding.introduced === true,
  };
}

/**
 * Build the adapter output object.
 */
function createResult(status, findings, summary, rawOutput) {
  return {
    status,
    findings: Array.isArray(findings) ? findings.map(normalizeFinding) : [],
    summary: summary || "",
    raw_output: rawOutput || "",
  };
}

/**
 * Determine adapter status from command exit code and parsed findings.
 *
 * If findings exist, the gate FAILs. If no findings exist but the tool exited
 * non-zero, the tool itself errored and we return ERROR. Otherwise PASS.
 */
function statusFromFindings(findings, exitCode) {
  if (findings.length > 0) return "FAIL";
  if (exitCode !== 0) return "ERROR";
  return "PASS";
}

module.exports = {
  readInput,
  validateInput,
  resolveCwd,
  normalizeFilePath,
  isChangedFile,
  runCommand,
  shellQuote,
  createResult,
  statusFromFindings,
};
