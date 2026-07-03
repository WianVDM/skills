#!/usr/bin/env node
/**
 * Adapter: npm-test
 *
 * Thin wrapper around the custom-command adapter that runs an npm script.
 *
 * Input (JSON via stdin):
 *   {
 *     "changed_files": [...],
 *     "base_branch": "origin/main",
 *     "config": {
 *       "script": "test:ci",
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
    const script = config.script || "test";
    input.config = {
      ...config,
      command: config.command || `npm run ${script}`,
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
      summary: "npm-test adapter failed to run",
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
