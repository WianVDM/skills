#!/usr/bin/env node
/**
 * Adapter: go-test
 *
 * Thin wrapper around the custom-command adapter that runs Go tests.
 *
 * Input (JSON via stdin):
 *   {
 *     "changed_files": [...],
 *     "base_branch": "origin/main",
 *     "config": {
 *       "command": "go test ./...",
 *       "cwd": ".",
 *       "timeout": 300,
 *       "env": {}
 *     },
 *     "project_root": "..."
 *   }
 *
 * Output: standard adapter contract JSON.
 */

const { parseInput, execute } = require("./custom-command");

async function main() {
  try {
    const input = await parseInput();
    const config = input.config || {};
    input.config = {
      ...config,
      command: config.command || "go test ./...",
      cwd: config.cwd || ".",
      timeout: config.timeout || 300,
    };
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
      summary: "go-test adapter failed to run",
      raw_output: err.stack || err.message,
    };
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
} else {
  module.exports = { main };
}
