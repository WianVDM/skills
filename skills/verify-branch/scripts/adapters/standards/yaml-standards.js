#!/usr/bin/env node
/**
 * yaml-standards adapter
 *
 * Reads standards from YAML sources and applies lightweight heuristic checks
 * to changed files. Returns the normalized adapter output expected by
 * scripts/run-gate.js.
 */

const { runStandardsCheck } = require("../../lib/standards-engine");

async function main() {
  let input = "";
  process.stdin.setEncoding("utf-8");
  process.stdin.on("data", (chunk) => {
    input += chunk;
  });
  process.stdin.on("end", () => {
    try {
      const parsed = input.trim() ? JSON.parse(input.trim()) : {};
      const result = runStandardsCheck(parsed);
      console.log(JSON.stringify(result, null, 2));
    } catch (err) {
      console.log(
        JSON.stringify(
          {
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
            summary: `yaml-standards adapter error: ${err.message}`,
          },
          null,
          2
        )
      );
    }
  });
}

main();
