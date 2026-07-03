#!/usr/bin/env node
/**
 * Adapter: custom-command
 *
 * General-purpose test adapter that runs any configured shell command and
 * reports PASS/FAIL following the verify-branch adapter contract.
 *
 * Input (JSON via stdin or arguments):
 *   {
 *     "changed_files": [{ "path": "src/app/billing.ts", "status": "M", "oldPath": null }],
 *     "base_branch": "origin/main",
 *     "config": {
 *       "command": ["npm", "run", "test:ci"],
 *       "cwd": ".",
 *       "timeout": 300,
 *       "env": { "NODE_ENV": "test" }
 *     },
 *     "project_root": "/path/to/project"
 *   }
 *
 * Output (JSON to stdout):
 *   {
 *     "status": "PASS|FAIL|ERROR",
 *     "findings": [...],
 *     "summary": "...",
 *     "raw_output": "..."
 *   }
 *
 * Rules:
 *   - Read-only; does not modify project files.
 *   - Deterministic for the same input and project state.
 *   - Exits 0 when the adapter itself ran successfully, even if the command failed.
 *   - Exits non-zero only on hard adapter errors (invalid input, I/O, etc.).
 */

const path = require("path");
const { runCommand } = require("../lib/adapter-utils");

const DEFAULT_TIMEOUT_SECONDS = 300;
const MAX_OUTPUT_LINES = 100;

function parseInput() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => {
      if (!data.trim()) {
        reject(new Error("No input provided on stdin"));
        return;
      }
      try {
        resolve(JSON.parse(data.trim()));
      } catch (err) {
        reject(new Error("Invalid JSON on stdin: " + err.message));
      }
    });
  });
}

function truncateOutput(output) {
  const lines = output.split("\n");
  if (lines.length <= MAX_OUTPUT_LINES) {
    return output;
  }
  return lines.slice(0, MAX_OUTPUT_LINES).join("\n") + "\n... [output truncated]";
}

function buildCommand(config) {
  const raw = config.command;
  if (Array.isArray(raw)) {
    if (raw.length === 0 || typeof raw[0] !== "string") {
      throw new Error("config.command array must start with an executable string");
    }
    return { command: raw[0], args: raw.slice(1) };
  }
  if (typeof raw === "string") {
    // Legacy trusted string path. This is the only place where an arbitrary
    // shell command string is accepted, and it must come from a trusted config.
    return { command: raw, args: [] };
  }
  throw new Error("config.command is required and must be a string or array");
}

async function runCustomCommand(command, args, cwd, timeoutMs, env, projectRoot) {
  const resolvedCwd = path.resolve(projectRoot || process.cwd(), cwd || ".");
  try {
    const result = await runCommand(command, args, resolvedCwd, timeoutMs, { ...process.env, CI: "true", ...(env || {}) });
    return {
      exitCode: result.exitCode,
      signal: null,
      timedOut: false,
      output: truncateOutput((result.stdout + "\n" + result.stderr).trim()),
    };
  } catch (err) {
    if (err.message.includes("timed out")) {
      return {
        exitCode: null,
        signal: "SIGTERM",
        timedOut: true,
        output: truncateOutput(err.message),
      };
    }
    throw err;
  }
}

async function execute(input) {
  const { changed_files, base_branch, config, project_root } = input || {};

  let commandInfo;
  try {
    commandInfo = buildCommand(config || {});
  } catch (err) {
    return {
      status: "ERROR",
      findings: [
        {
          file: null,
          line: 0,
          rule: "invalid_config",
          severity: "error",
          message: err.message,
          introduced: true,
        },
      ],
      summary: "Invalid adapter config: missing or invalid command",
      raw_output: "",
    };
  }

  const cwd = config.cwd || ".";
  const timeoutMs = (config.timeout || DEFAULT_TIMEOUT_SECONDS) * 1000;
  const env = config.env || {};

  const result = await runCustomCommand(commandInfo.command, commandInfo.args, cwd, timeoutMs, env, project_root);
  const status = result.timedOut ? "FAIL" : result.exitCode === 0 ? "PASS" : "FAIL";

  const findings = [];
  if (status === "FAIL") {
    findings.push({
      file: null,
      line: 0,
      rule: result.timedOut ? "command_timeout" : "command_failure",
      severity: "error",
      message: result.timedOut
        ? `Command timed out after ${timeoutMs / 1000}s: ${command}`
        : `Command failed with exit code ${result.exitCode}: ${command}`,
      introduced: true,
    });
  }

  const summary = result.timedOut
    ? `Command timed out after ${timeoutMs / 1000}s: ${commandInfo.command}${commandInfo.args.length > 0 ? " " + commandInfo.args.join(" ") : ""}`
    : status === "PASS"
    ? `Command passed: ${commandInfo.command}${commandInfo.args.length > 0 ? " " + commandInfo.args.join(" ") : ""}`
    : `Command failed with exit code ${result.exitCode}: ${commandInfo.command}${commandInfo.args.length > 0 ? " " + commandInfo.args.join(" ") : ""}`;

  return {
    status,
    findings,
    summary,
    raw_output: result.output,
  };
}

async function main() {
  try {
    const input = await parseInput();
    const output = await execute(input);
    console.log(JSON.stringify(output, null, 2));
    process.exit(0);
  } catch (err) {
    const output = {
      status: "ERROR",
      findings: [
        {
          file: null,
          line: 0,
          rule: "adapter_error",
          severity: "error",
          message: err.message,
          introduced: true,
        },
      ],
      summary: "Adapter failed to run",
      raw_output: err.stack || err.message,
    };
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
} else {
  module.exports = { parseInput, execute, runCustomCommand };
}
