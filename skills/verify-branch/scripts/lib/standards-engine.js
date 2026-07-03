const fs = require("fs");
const path = require("path");

let yaml;
try {
  yaml = require("js-yaml");
} catch {
  yaml = null;
}

function parseYaml(text) {
  if (yaml) {
    return yaml.load(text);
  }

  // Fallback: shell out to Python for YAML parsing.
  const { execSync } = require("child_process");
  try {
    const json = execSync(
      "python -c \"import yaml, sys, json; print(json.dumps(yaml.safe_load(sys.stdin.read()), default=str))\"",
      {
        input: text,
        encoding: "utf-8",
        timeout: 5000,
      }
    );
    return JSON.parse(json);
  } catch (err) {
    throw new Error(`Failed to parse YAML (js-yaml missing and Python fallback failed): ${err.message}`);
  }
}

function parseFrontmatter(text) {
  if (!text.startsWith("---")) {
    return { frontmatter: {}, body: text };
  }
  const end = text.indexOf("---", 3);
  if (end === -1) {
    return { frontmatter: {}, body: text };
  }
  const frontmatterText = text.slice(3, end).trim();
  const body = text.slice(end + 3).trimStart();
  const frontmatter = frontmatterText ? parseYaml(frontmatterText) : {};
  return { frontmatter, body };
}

function loadSource(source, projectRoot) {
  const filePath = path.isAbsolute(source.path)
    ? source.path
    : path.join(projectRoot, source.path);

  if (!fs.existsSync(filePath)) {
    throw new Error(`Standards source not found: ${source.path}`);
  }

  const text = fs.readFileSync(filePath, "utf-8");
  const type = source.type || "yaml";

  if (type === "yaml") {
    return parseYaml(text);
  }

  if (type === "markdown-frontmatter") {
    const { frontmatter } = parseFrontmatter(text);
    return frontmatter;
  }

  throw new Error(`Unknown standards source type: ${type}`);
}

function applyOverrides(rules, overrides) {
  if (!Array.isArray(overrides)) {
    return rules;
  }

  const byId = new Map(rules.map((r) => [r.id, r]));
  for (const override of overrides) {
    if (!override.id) continue;
    const rule = byId.get(override.id);
    if (!rule) continue;
    if (override.severity !== undefined) {
      rule.severity = override.severity;
    }
    if (override.threshold !== undefined) {
      rule.threshold = override.threshold;
    }
    if (override.reason) {
      rule._override_reason = override.reason;
    }
  }
  return Array.from(byId.values());
}

function gatherRules(sources, projectRoot) {
  const all = [];
  for (const source of sources) {
    const data = loadSource(source, projectRoot);
    const rules = Array.isArray(data?.rules) ? data.rules : [];
    for (const rule of rules) {
      if (rule && rule.id) {
        all.push(rule);
      }
    }
  }
  return all;
}

function getLines(content) {
  return content.split(/\r?\n/);
}

function findFunctions(content) {
  // Very rough function/method boundary detection for brace-based languages.
  const functions = [];
  const lines = getLines(content);
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const match = line.match(
      /^(\s*)(?:async\s+|static\s+|private\s+|protected\s+|public\s+)*([\w$\_]+)\s*\([^)]*\)\s*(:\s*\w+)?\s*\{/
    );
    if (match) {
      const start = i;
      let depth = 0;
      let j = i;
      for (; j < lines.length; j++) {
        for (const ch of lines[j]) {
          if (ch === "{") depth++;
          if (ch === "}") {
            depth--;
            if (depth === 0) {
              j++;
              break;
            }
          }
        }
        if (depth === 0) break;
      }
      functions.push({ name: match[2], startLine: start + 1, endLine: j, body: lines.slice(start, j).join("\n") });
      i = j;
      continue;
    }
    i++;
  }
  return functions;
}

function checkNestingDepth(content, threshold) {
  const findings = [];
  const functions = findFunctions(content);
  for (const fn of functions) {
    const lines = getLines(fn.body);
    let maxDepth = 0;
    let currentDepth = 0;
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith("//")) continue;
      // Increase depth for every block opener not in a string.
      const opens = (line.match(/\{/g) || []).length;
      const closes = (line.match(/\}/g) || []).length;
      currentDepth += opens - closes;
      maxDepth = Math.max(maxDepth, currentDepth);
    }
    if (maxDepth > threshold) {
      findings.push({
        line: fn.startLine,
        message: `Function \`${fn.name}\` has nesting depth ${maxDepth}, exceeding threshold ${threshold}.`,
      });
    }
  }
  return findings;
}

function checkMethodLength(content, threshold) {
  const findings = [];
  const functions = findFunctions(content);
  for (const fn of functions) {
    const lineCount = fn.endLine - fn.startLine + 1;
    if (lineCount > threshold) {
      findings.push({
        line: fn.startLine,
        message: `Function \`${fn.name}\` is ${lineCount} lines, exceeding threshold ${threshold}.`,
      });
    }
  }
  return findings;
}

function checkNoCommentedCode(content) {
  const findings = [];
  const lines = getLines(content);
  let runStart = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith("//") || line.startsWith("#")) {
      if (runStart === null) runStart = i;
    } else if (runStart !== null) {
      const runLength = i - runStart;
      if (runLength >= 5) {
        findings.push({ line: runStart + 1, message: `${runLength} consecutive lines of commented-out code.` });
      }
      runStart = null;
    }
  }
  if (runStart !== null) {
    const runLength = lines.length - runStart;
    if (runLength >= 5) {
      findings.push({ line: runStart + 1, message: `${runLength} consecutive lines of commented-out code at end of file.` });
    }
  }
  return findings;
}

function checkNoAny(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /:\s*any\b|as\s+any\b/;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (re.test(line)) {
      findings.push({ line: i + 1, message: "Avoid using `any` in TypeScript code." });
    }
  }
  return findings;
}

function checkNoIPrefixInterfaces(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /interface\s+I[A-Z]/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      findings.push({ line: i + 1, message: "Do not prefix TypeScript interfaces with `I`." });
    }
  }
  return findings;
}

function checkBooleanNaming(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /(?:const|let|var)\s+([a-z][A-Za-z0-9_]*)\s*:\s*boolean\b/;
  for (let i = 0; i < lines.length; i++) {
    const match = re.exec(lines[i]);
    if (match) {
      const name = match[1];
      if (!/^(is|has|should|can|was|were|did|will|needs|allows|supports|exists|enabled|disabled|valid|ready)/i.test(name)) {
        findings.push({ line: i + 1, message: `Boolean variable \`${name}\` should read as a predicate.` });
      }
    }
  }
  return findings;
}

function checkAngularOnPush(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /changeDetection\s*:\s*ChangeDetectionStrategy\.Default/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      findings.push({ line: i + 1, message: "Consider using ChangeDetectionStrategy.OnPush for new components." });
    }
  }
  return findings;
}

function checkAngularSignalInputs(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /@Input\(\)\s/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      findings.push({ line: i + 1, message: "Prefer signal-based inputs (`input()`) over `@Input()`." });
    }
  }
  return findings;
}

function checkAngularServiceInject(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /constructor\s*\([^)]*private\s+\w+\s*:\s*\w+/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      findings.push({ line: i + 1, message: "Consider using `inject()` for dependency injection." });
    }
  }
  return findings;
}

function checkExplicitReturnTypes(content) {
  const findings = [];
  const lines = getLines(content);
  // Match public function declarations without return type annotations.
  const re = /^(\s*)(?:export\s+)?(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\([^)]*\)\s*\{/;
  for (let i = 0; i < lines.length; i++) {
    const match = re.exec(lines[i]);
    if (match && !lines[i].includes(": ")) {
      findings.push({ line: i + 1, message: `Consider adding an explicit return type to \`${match[2]}\`.` });
    }
  }
  return findings;
}

function checkNoBareExcept(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /except\s*:/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i])) {
      findings.push({ line: i + 1, message: "Do not use bare `except:` clauses. Catch specific exceptions." });
    }
  }
  return findings;
}

function checkPep8Naming(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /def\s+([A-Za-z0-9_$]+)\s*\(/;
  for (let i = 0; i < lines.length; i++) {
    const match = re.exec(lines[i]);
    if (match) {
      const name = match[1];
      if (/[A-Z]/.test(name)) {
        findings.push({ line: i + 1, message: `Function \`${name}\` should use snake_case per PEP 8.` });
      }
    }
  }
  return findings;
}

function checkTypeHints(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /def\s+([A-Za-z0-9_$]+)\s*\(([^)]*)\)\s*:/;
  for (let i = 0; i < lines.length; i++) {
    const match = re.exec(lines[i]);
    if (match) {
      const params = match[2];
      // Skip self/cls-only or empty signatures.
      if (!params.trim() || params.replace(/\bself\b/g, "").replace(/\bcls\b/g, "").trim() === "") {
        continue;
      }
      if (!params.includes(":")) {
        findings.push({ line: i + 1, message: `Function \`${match[1]}\` is missing type hints on parameters.` });
      }
    }
  }
  return findings;
}

function checkExplicitReturnNone(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /return\s*$/;
  for (let i = 0; i < lines.length; i++) {
    if (re.test(lines[i].trim())) {
      findings.push({ line: i + 1, message: "Return `None` explicitly when no result is found." });
    }
  }
  return findings;
}

function checkDocstringsPublic(content) {
  const findings = [];
  const lines = getLines(content);
  const re = /^(\s*)(def|class)\s+([A-Za-z0-9_$]+)/;
  for (let i = 0; i < lines.length; i++) {
    const match = re.exec(lines[i]);
    if (match && !match[3].startsWith("_")) {
      // Check next non-empty line for docstring.
      let j = i + 1;
      while (j < lines.length && lines[j].trim() === "") j++;
      if (j < lines.length && !lines[j].trim().startsWith('"""') && !lines[j].trim().startsWith("'''")) {
        findings.push({ line: i + 1, message: `Public ${match[2]} \`${match[3]}\` should have a docstring.` });
      }
    }
  }
  return findings;
}

function checkRule(content, rule) {
  const id = rule.id;
  const threshold = rule.threshold;

  const handlers = {
    "nesting-depth": () => checkNestingDepth(content, threshold ?? 4),
    "method-length": () => checkMethodLength(content, threshold ?? 50),
    "no-commented-code": () => checkNoCommentedCode(content),
    "no-any": () => checkNoAny(content),
    "no-i-prefix-interfaces": () => checkNoIPrefixInterfaces(content),
    "boolean-naming": () => checkBooleanNaming(content),
    "angular-onpush": () => checkAngularOnPush(content),
    "angular-signal-inputs": () => checkAngularSignalInputs(content),
    "angular-service-inject": () => checkAngularServiceInject(content),
    "explicit-return-types": () => checkExplicitReturnTypes(content),
    "no-bare-except": () => checkNoBareExcept(content),
    "pep8-naming": () => checkPep8Naming(content),
    "type-hints": () => checkTypeHints(content),
    "explicit-return-None": () => checkExplicitReturnNone(content),
    "docstrings-public": () => checkDocstringsPublic(content),
  };

  const handler = handlers[id];
  if (handler) {
    return handler();
  }

  // No automated check available for this rule.
  return [];
}

function runStandardsCheck(input) {
  const projectRoot = input.project_root || process.cwd();
  const config = input.config || {};
  const sources = Array.isArray(config.sources) ? config.sources : [];
  const overrides = Array.isArray(config.overrides) ? config.overrides : [];
  const changedFiles = input.changed_files || [];

  if (sources.length === 0) {
    return {
      status: "NOT_APPLICABLE",
      findings: [],
      summary: "No standards sources configured; gate is not applicable.",
    };
  }

  let rules;
  try {
    const rawRules = gatherRules(sources, projectRoot);
    rules = applyOverrides(rawRules, overrides).filter((r) => r.severity !== "disabled");
  } catch (err) {
    return {
      status: "ERROR",
      findings: [
        {
          file: null,
          line: 0,
          rule: "source_load_error",
          severity: "error",
          message: `Could not load standards sources: ${err.message}`,
          introduced: true,
        },
      ],
      summary: `Failed to load standards sources: ${err.message}`,
    };
  }

  if (rules.length === 0) {
    return {
      status: "NOT_APPLICABLE",
      findings: [],
      summary: "No standards rules found in configured sources.",
    };
  }

  const findings = [];
  let filesChecked = 0;
  let uncheckedRuleIds = [];

  for (const file of changedFiles) {
    if (!file || typeof file !== "string") continue;
    const filePath = path.isAbsolute(file) ? file : path.join(projectRoot, file);
    if (!fs.existsSync(filePath)) continue;

    let content;
    try {
      content = fs.readFileSync(filePath, "utf-8");
    } catch {
      continue;
    }
    filesChecked++;

    for (const rule of rules) {
      const ruleFindings = checkRule(content, rule);
      for (const rf of ruleFindings) {
        findings.push({
          file: file,
          line: rf.line || 0,
          rule: rule.id,
          severity: rule.severity === "violation" ? "violation" : "consideration",
          message: rf.message,
          introduced: true,
        });
      }
      if (ruleFindings.length === 0) {
        uncheckedRuleIds.push(rule.id);
      }
    }
  }

  // Dedupe unchecked rule ids.
  uncheckedRuleIds = [...new Set(uncheckedRuleIds)];
  const autoCheckable = [
    "nesting-depth",
    "method-length",
    "no-commented-code",
    "no-any",
    "no-i-prefix-interfaces",
    "boolean-naming",
    "angular-onpush",
    "angular-signal-inputs",
    "angular-service-inject",
    "explicit-return-types",
    "no-bare-except",
    "pep8-naming",
    "type-hints",
    "explicit-return-None",
    "docstrings-public",
  ];
  const trulyUnchecked = uncheckedRuleIds.filter((id) => !autoCheckable.includes(id));

  if (trulyUnchecked.length > 0 && changedFiles.length > 0) {
    // Add a single consideration per unchecked rule to remind the project that
    // these rules exist but are not automatically enforced.
    for (const id of trulyUnchecked) {
      const rule = rules.find((r) => r.id === id);
      findings.push({
        file: changedFiles[0],
        line: 0,
        rule: id,
        severity: "consideration",
        message: `Rule \`${id}\` is not automatically checked by this adapter. Consider adding a custom adapter or manual review step.`,
        introduced: true,
      });
    }
  }

  const violations = findings.filter((f) => f.severity === "violation");
  const status = violations.length > 0 ? "FAIL" : "PASS";
  const summary =
    status === "PASS"
      ? `Checked ${filesChecked} changed file(s) against ${rules.length} rule(s). No violations found.`
      : `Checked ${filesChecked} changed file(s) against ${rules.length} rule(s). Found ${violations.length} violation(s).`;

  return { status, findings, summary };
}

module.exports = {
  runStandardsCheck,
  loadSource,
  applyOverrides,
  gatherRules,
  checkRule,
};
