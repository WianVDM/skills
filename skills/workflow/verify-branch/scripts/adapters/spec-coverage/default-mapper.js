#!/usr/bin/env node
/**
 * Adapter: spec-coverage/default-mapper
 *
 * Maps changed source files to their expected spec files and reports whether
 * those specs exist and were modified in the current change set.
 *
 * Input (JSON via stdin):
 *   {
 *     "changed_files": [{ "path": "src/app/billing.ts", "status": "M", "oldPath": null }],
 *     "base_branch": "origin/main",
 *     "config": {
 *       "mappings": [
 *         { "source_pattern": "src/app/*.ts", "spec_pattern": "{dir}/{name}.spec.ts", "area": "frontend" }
 *       ],
 *       "exemptions": [
 *         { "pattern": "*.d.ts", "reason": "type definition" }
 *       ]
 *     },
 *     "project_root": "/path/to/project"
 *   }
 *
 * Output (JSON to stdout):
 *   {
 *     "status": "PASS|FAIL",
 *     "findings": [
 *       { "file": "src/app/billing.ts", "line": 0, "rule": "missing_spec", "severity": "error", "message": "...", "introduced": true }
 *     ],
 *     "summary": "...",
 *     "raw_output": "..."
 *   }
 *
 * Rules:
 *   - Read-only; does not modify project files.
 *   - Deterministic for the same input and project state.
 *   - Exits 0 when the adapter itself ran successfully, even if findings exist.
 *   - Exits non-zero only on hard adapter errors.
 */

const fs = require("fs");
const path = require("path");

const DEFAULT_MAPPINGS = [
  { source_pattern: "src/**/*.ts", spec_pattern: "{dir}/{name}.spec.ts", area: "typescript" },
  { source_pattern: "src/**/*.js", spec_pattern: "{dir}/{name}.spec.js", area: "javascript" },
  { source_pattern: "src/**/*.py", spec_pattern: "tests/{dir}/{name}_test.py", area: "python" },
  { source_pattern: "**/*.go", spec_pattern: "{dir}/{name}_test.go", area: "go" },
];

const DEFAULT_EXEMPTIONS = [
  { pattern: "**/*.spec.ts", reason: "is a spec file" },
  { pattern: "**/*.test.ts", reason: "is a test file" },
  { pattern: "**/*.spec.js", reason: "is a spec file" },
  { pattern: "**/*.test.js", reason: "is a test file" },
  { pattern: "**/*_test.py", reason: "is a test file" },
  { pattern: "**/*_test.go", reason: "is a test file" },
  { pattern: "**/*.d.ts", reason: "type definition" },
  { pattern: "**/test/**", reason: "test directory" },
  { pattern: "**/tests/**", reason: "test directory" },
  { pattern: "**/__tests__/**", reason: "test directory" },
  { pattern: "**/node_modules/**", reason: "dependency directory" },
];

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

function globToRegex(pattern) {
  // Normalize common ** patterns so they match across path separators.
  const normalized = pattern
    .replace(/^\*\*\//g, "{LEADING_GLOB}")
    .replace(/\/\*\*\//g, "{MIDDLE_GLOB}")
    .replace(/\/\*\*$/g, "{TRAILING_GLOB}");

  let regex = "";
  for (const char of normalized) {
    if (char === "*") {
      regex += "[^/]*";
    } else if (char === "?") {
      regex += "[^/]";
    } else if (".+^${}()|[]\\".includes(char)) {
      regex += "\\" + char;
    } else {
      regex += char;
    }
  }

  regex = regex
    .replace(/\{LEADING_GLOB\}/g, "(?:.*/)?")
    .replace(/\{MIDDLE_GLOB\}/g, "(?:.*/)?")
    .replace(/\{TRAILING_GLOB\}/g, "(?:/.*)?");

  return new RegExp("^" + regex + "$");
}

function matchesGlob(filePath, pattern) {
  return globToRegex(pattern).test(filePath);
}

function applyTemplate(template, filePath) {
  const dir = path.dirname(filePath);
  const base = path.basename(filePath);
  const ext = path.extname(filePath);
  const name = path.basename(filePath, ext);

  return template
    .replace(/\{path\}/g, filePath)
    .replace(/\{dir\}/g, dir)
    .replace(/\{base\}/g, base)
    .replace(/\{name\}/g, name)
    .replace(/\{ext\}/g, ext);
}

function isExempt(filePath, exemptions) {
  for (const exemption of exemptions) {
    if (matchesGlob(filePath, exemption.pattern)) {
      return exemption;
    }
  }
  return null;
}

function findMapping(filePath, mappings) {
  for (const mapping of mappings) {
    if (matchesGlob(filePath, mapping.source_pattern)) {
      return mapping;
    }
  }
  return null;
}

async function execute(input) {
  const { changed_files, config, project_root } = input || {};
  const mappings = (config && config.mappings) || DEFAULT_MAPPINGS;
  const exemptions = (config && config.exemptions) || DEFAULT_EXEMPTIONS;

  const changedPaths = new Set((changed_files || []).map((f) => f.path));
  const findings = [];
  const mapped = [];
  const exempt = [];
  const skipped = [];

  for (const file of changed_files || []) {
    const filePath = file.path;
    const status = file.status || "";

    if (status.startsWith("D")) {
      // Deleted source files do not need new specs.
      skipped.push({ source: filePath, reason: "deleted source file" });
      continue;
    }

    const exemption = isExempt(filePath, exemptions);
    if (exemption) {
      exempt.push({ source: filePath, reason: exemption.reason });
      continue;
    }

    const mapping = findMapping(filePath, mappings);
    if (!mapping) {
      skipped.push({ source: filePath, reason: "no matching source-to-spec mapping" });
      continue;
    }

    const expectedSpec = applyTemplate(mapping.spec_pattern, filePath);
    const specExists = fs.existsSync(path.resolve(project_root || process.cwd(), expectedSpec));
    const specModified = changedPaths.has(expectedSpec);

    mapped.push({
      source: filePath,
      spec: expectedSpec,
      area: mapping.area || null,
      specExists,
      specModified,
    });

    if (!specExists) {
      findings.push({
        file: filePath,
        line: 0,
        rule: "missing_spec",
        severity: "error",
        message: `Expected spec file ${expectedSpec} for ${filePath} does not exist`,
        introduced: true,
      });
    } else if (!specModified) {
      findings.push({
        file: filePath,
        line: 0,
        rule: "unmodified_spec",
        severity: "error",
        message: `Expected spec file ${expectedSpec} for ${filePath} exists but was not modified`,
        introduced: true,
      });
    }
  }

  const missingCount = findings.filter((f) => f.rule === "missing_spec").length;
  const unmodifiedCount = findings.filter((f) => f.rule === "unmodified_spec").length;

  let summary;
  if (findings.length === 0) {
    summary = `All ${mapped.length} mapped specs exist and were modified`;
  } else {
    summary = `${missingCount} missing specs, ${unmodifiedCount} unmodified specs`;
  }

  const rawOutput = JSON.stringify(
    {
      mapped,
      exempt,
      skipped,
      mappings_applied: mappings.map((m) => ({
        source_pattern: m.source_pattern,
        spec_pattern: m.spec_pattern,
        area: m.area || null,
      })),
      exemptions_applied: exemptions.map((e) => e.pattern),
    },
    null,
    2
  );

  return {
    status: findings.length === 0 ? "PASS" : "FAIL",
    findings,
    summary,
    raw_output: rawOutput,
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
      summary: "spec-coverage/default-mapper adapter failed to run",
      raw_output: err.stack || err.message,
    };
    console.log(JSON.stringify(output, null, 2));
    process.exit(1);
  }
}

if (require.main === module) {
  main();
} else {
  module.exports = { parseInput, execute, globToRegex, matchesGlob, applyTemplate };
}
