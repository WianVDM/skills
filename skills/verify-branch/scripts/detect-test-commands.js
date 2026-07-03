#!/usr/bin/env node
/**
 * Auto-detects test commands for the current project.
 *
 * Checks package.json files in the repo root and common subdirectories, then
 * picks the most CI-friendly test script using a priority list. Also inspects
 * CI configuration files and common task runners (Makefile, justfile,
 * Taskfile.yml) for additional test-related commands.
 *
 * Usage:
 *   node detect-test-commands.js
 *   node detect-test-commands.js --cwd /path/to/project
 *
 * Output: JSON array to stdout.
 * Each item: { name: string, cwd: string, command: string, script?: string }
 */

const fs = require("fs");
const path = require("path");

const TEST_SCRIPT_PRIORITY = [
  "test:ci",
  "test-headless",
  "test:unit",
  "test:unit:ci",
  "test",
];

const TEST_KEYWORDS = [
  "test", "tests", "jest", "vitest", "mocha", "jasmine", "karma",
  "pytest", "py.test", "unittest", "go test", "cargo test", "mvn test",
  "gradle test", "dotnet test", "npm test", "yarn test", "pnpm test",
];

const SUBDIRS_TO_CHECK = ["server", "backend", "api", "middleware", "packages/*"];

const CI_FILES = {
  ".gitlab-ci.yml": "GitLab CI",
  "azure-pipelines.yml": "Azure Pipelines",
  "azure-pipelines.yaml": "Azure Pipelines",
  ".circleci/config.yml": "CircleCI",
  "Jenkinsfile": "Jenkins",
};

function parseArgs() {
  const args = process.argv.slice(2);
  let cwd = process.cwd();
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--cwd" && i + 1 < args.length) {
      cwd = path.resolve(args[i + 1]);
      i++;
    }
  }
  return { cwd };
}

function readFileText(filePath) {
  try {
    return fs.readFileSync(filePath, "utf-8");
  } catch {
    return "";
  }
}

function readPackageJson(dir) {
  const p = path.join(dir, "package.json");
  if (!fs.existsSync(p)) return null;
  try {
    return JSON.parse(readFileText(p));
  } catch {
    return null;
  }
}

function isDummyScript(script) {
  if (!script) return true;
  const s = script.toLowerCase();
  return (
    s.includes('echo "error: no test specified"') ||
    (s.includes("exit 1") && s.length < 50) ||
    s.includes('echo "no test') ||
    s.includes('echo "not implemented"')
  );
}

function mightHang(script) {
  if (!script) return false;
  // ng test without --watch=false will hang in watch mode
  if (/ng\s+test/.test(script) && !/--watch\s*=\s*false/.test(script)) {
    return true;
  }
  // jest without --watchAll=false or --watch=false
  if (
    /jest\s/.test(script) &&
    !/--watch(All)?\s*=\s*false/.test(script) &&
    !/--no-watch/.test(script)
  ) {
    return true;
  }
  return false;
}

function pickBestTestCommand(pkg) {
  if (!pkg || !pkg.scripts) return null;

  for (const candidate of TEST_SCRIPT_PRIORITY) {
    const script = pkg.scripts[candidate];
    if (!script) continue;
    if (isDummyScript(script)) continue;
    return { scriptName: candidate, script };
  }

  return null;
}

function expandGlobDirs(baseDir, pattern) {
  if (!pattern.includes("*")) return [path.join(baseDir, pattern)];

  const parts = pattern.split("/*");
  const parent = path.join(baseDir, parts[0]);
  if (!fs.existsSync(parent)) return [];

  const entries = fs.readdirSync(parent, { withFileTypes: true });
  return entries
    .filter((e) => e.isDirectory())
    .map((e) => path.join(parent, e.name));
}

function detectForDir(dir, name, baseDir) {
  const pkg = readPackageJson(dir);
  if (!pkg) return null;

  const picked = pickBestTestCommand(pkg);
  if (!picked) return null;

  // Skip watch-mode commands unless they're the only option
  if (
    mightHang(picked.script) &&
    TEST_SCRIPT_PRIORITY.some((k) => k !== picked.scriptName && pkg.scripts[k])
  ) {
    return null;
  }

  const cwd = path.relative(baseDir, dir) || ".";
  return {
    name,
    cwd,
    command: `npm run ${picked.scriptName}`,
    script: picked.script,
  };
}

const METADATA_KEYS = new Set([
  "name", "uses", "needs", "with", "if", "env", "runs-on", "on",
  "jobs", "steps", "defaults", "strategy", "matrix", "branches",
  "permissions", "concurrency", "container", "services", "outputs",
  "description", "group", "working-directory", "shell", "timeout-minutes",
  "continue-on-error", "fail-fast", "max-parallel", "type", "stage",
  "when", "only", "except", "allow_failure", "artifacts", "cache",
  "variables", "image", "before_script", "after_script", "parameters",
  "trigger", "include", "extends", "dependencies", "resource_pool",
]);

const SHELL_NOISE_PREFIXES = new Set([
  "echo ", "printf ", "if ", "elif ", "else", "fi", "then ",
  "for ", "while ", "done ", "case ", "esac", "export ", "set ",
  "unset ", "local ", "declare ", "typeset ",
]);

function isShellNoise(command) {
  const cmdLower = command.trim().toLowerCase();
  for (const prefix of SHELL_NOISE_PREFIXES) {
    if (cmdLower.startsWith(prefix)) return true;
  }
  return false;
}

function isMetadataLine(line) {
  const match = line.match(/^([a-zA-Z0-9_-]+)\s*:/);
  return match !== null && METADATA_KEYS.has(match[1].toLowerCase());
}

function isTestCommandKeyword(keyword, command) {
  const lower = command.toLowerCase();
  if (lower.includes(keyword)) {
    if (keyword === "test") {
      return /(?:^|[\s\-:])test(?:[\s\-:]|$)/.test(lower);
    }
    return true;
  }
  return false;
}

function extractTestCommandsFromText(text) {
  const commands = [];
  const seen = new Set();
  const BLOCK_SCALARS = new Set(["|", ">", "|-", ">-", "|+", ">+"]);
  const lines = text.split(/\r?\n/);
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const stripped = line.trim();
    if (!stripped || stripped.startsWith("#")) {
      i += 1;
      continue;
    }

    // GitHub Actions / CircleCI run: command or run: | block
    const runMatch = line.match(/^(\s*)run:\s*(.*)$/);
    if (runMatch) {
      const runIndent = runMatch[1].length;
      const content = runMatch[2].trim();
      if (BLOCK_SCALARS.has(content)) {
        // Block scalar: collect following indented lines
        i += 1;
        while (i < lines.length) {
          const nextLine = lines[i];
          if (!nextLine.trim()) {
            i += 1;
            continue;
          }
          const nextIndent = nextLine.length - nextLine.trimStart().length;
          if (nextIndent > runIndent) {
            const nextStripped = nextLine.trim();
            if (nextStripped && !nextStripped.startsWith("#")) {
              commands.push(nextStripped);
            }
            i += 1;
          } else {
            break;
          }
        }
        continue;
      } else if (content && !isMetadataLine(content)) {
        commands.push(content);
      }
      i += 1;
      continue;
    }

    // List items (GitLab CI / Azure Pipelines script steps, CircleCI command)
    const itemMatch = line.match(/^\s*-\s*(.*)$/);
    if (itemMatch) {
      const content = itemMatch[1].trim();
      if (content && !isMetadataLine(content)) {
        commands.push(content);
      }
      i += 1;
      continue;
    }

    // Jenkins sh '...' / sh "..." blocks
    const jenkinsMatch = line.match(/\bsh\s+['"](.+?)['"]/);
    if (jenkinsMatch) {
      commands.push(jenkinsMatch[1]);
    }

    i += 1;
  }

  // Filter out shell-only noise (echo, if/fi, etc.) then test-related commands
  const substantiveCommands = commands.filter((cmd) => !isShellNoise(cmd));

  const testCommands = substantiveCommands.filter((cmd) =>
    TEST_KEYWORDS.some((kw) => isTestCommandKeyword(kw, cmd))
  );

  const result = [];
  for (const cmd of testCommands) {
    if (!seen.has(cmd)) {
      seen.add(cmd);
      result.push(cmd);
    }
  }
  return result.slice(0, 20);
}

function detectCiTestCommands(baseDir) {
  const commands = [];

  const workflowsDir = path.join(baseDir, ".github", "workflows");
  if (fs.existsSync(workflowsDir)) {
    for (const entry of fs.readdirSync(workflowsDir)) {
      if (/\.(yml|yaml)$/.test(entry)) {
        const text = readFileText(path.join(workflowsDir, entry));
        const extracted = extractTestCommandsFromText(text);
        if (extracted.length > 0) {
          const workflowName = path.basename(entry, path.extname(entry));
          extracted.forEach((cmd, idx) => commands.push({
            name: `github-workflow-${workflowName}-${idx + 1}`,
            cwd: ".",
            command: cmd,
          }));
        }
      }
    }
  }

  for (const [filename, label] of Object.entries(CI_FILES)) {
    const filePath = path.join(baseDir, filename);
    if (fs.existsSync(filePath)) {
      const text = readFileText(filePath);
      const extracted = extractTestCommandsFromText(text);
      if (extracted.length > 0) {
        const labelSlug = label.toLowerCase().replace(/\s+/g, "-");
        extracted.forEach((cmd, idx) => commands.push({
          name: `${labelSlug}-${idx + 1}`,
          cwd: ".",
          command: cmd,
        }));
      }
    }
  }

  return commands;
}

function parseMakefileTargets(filePath) {
  const targets = [];
  const targetRe = /^([a-zA-Z0-9_.-]+)\s*:/;
  for (const line of readFileText(filePath).split(/\r?\n/)) {
    const match = targetRe.exec(line);
    if (match && !line.startsWith("\t")) {
      targets.push(match[1]);
    }
  }
  return targets;
}

function parseJustfileTargets(filePath) {
  const targets = [];
  const recipeRe = /^([a-zA-Z0-9_-]+)\s*[:@\[]/;
  for (const line of readFileText(filePath).split(/\r?\n/)) {
    const match = recipeRe.exec(line);
    if (match) targets.push(match[1]);
  }
  return targets;
}

function parseTaskfileTargets(filePath) {
  const targets = [];
  const taskRe = /^\s+([a-zA-Z0-9_-]+):\s*$/;
  let inTasks = false;
  for (const line of readFileText(filePath).split(/\r?\n/)) {
    if (line.trim() === "tasks:") {
      inTasks = true;
      continue;
    }
    if (inTasks) {
      const match = taskRe.exec(line);
      if (match && !line.trim().startsWith("#")) {
        targets.push(match[1]);
      }
    }
  }
  return targets;
}

function filterTestTargets(targets) {
  return targets.filter((t) =>
    TEST_KEYWORDS.some((kw) => t.toLowerCase().includes(kw))
  );
}

function detectTaskRunnerTestCommands(baseDir) {
  const commands = [];

  const makefilePath = path.join(baseDir, "Makefile");
  if (fs.existsSync(makefilePath)) {
    const testTargets = filterTestTargets(parseMakefileTargets(makefilePath));
    testTargets.slice(0, 10).forEach((target) => {
      commands.push({ name: `make-${target}`, cwd: ".", command: `make ${target}` });
    });
  }

  const justfilePath = path.join(baseDir, "justfile");
  if (fs.existsSync(justfilePath)) {
    const testTargets = filterTestTargets(parseJustfileTargets(justfilePath));
    testTargets.slice(0, 10).forEach((target) => {
      commands.push({ name: `just-${target}`, cwd: ".", command: `just ${target}` });
    });
  }

  for (const name of ["Taskfile.yml", "Taskfile.yaml"]) {
    const taskfilePath = path.join(baseDir, name);
    if (fs.existsSync(taskfilePath)) {
      const testTargets = filterTestTargets(parseTaskfileTargets(taskfilePath));
      testTargets.slice(0, 10).forEach((target) => {
        commands.push({ name: `task-${target}`, cwd: ".", command: `task ${target}` });
      });
      break;
    }
  }

  return commands;
}

function detectPythonTestCommands(baseDir) {
  const commands = [];
  const pyprojectPath = path.join(baseDir, "pyproject.toml");
  if (fs.existsSync(pyprojectPath)) {
    const text = readFileText(pyprojectPath).toLowerCase();
    if (text.includes("pytest") || text.includes("[tool.pytest")) {
      commands.push({ name: "python-pytest", cwd: ".", command: "pytest" });
    }
  }
  if (fs.existsSync(path.join(baseDir, "pytest.ini"))) {
    commands.push({ name: "python-pytest", cwd: ".", command: "pytest" });
  }
  if (fs.existsSync(path.join(baseDir, "setup.py"))) {
    const text = readFileText(path.join(baseDir, "setup.py")).toLowerCase();
    if (text.includes("pytest") || text.includes("unittest")) {
      commands.push({ name: "python-pytest", cwd: ".", command: "python -m pytest" });
    }
  }
  return commands;
}

function detectGoTestCommands(baseDir) {
  if (fs.existsSync(path.join(baseDir, "go.mod"))) {
    return [{ name: "go-test", cwd: ".", command: "go test ./..." }];
  }
  return [];
}

function detectRustTestCommands(baseDir) {
  if (fs.existsSync(path.join(baseDir, "Cargo.toml"))) {
    return [{ name: "cargo-test", cwd: ".", command: "cargo test" }];
  }
  return [];
}

function main() {
  const { cwd } = parseArgs();
  const results = [];

  // Root package.json
  const root = detectForDir(cwd, "root", cwd);
  if (root) results.push(root);

  // Subdirectories
  for (const pattern of SUBDIRS_TO_CHECK) {
    const dirs = expandGlobDirs(cwd, pattern);
    for (const dir of dirs) {
      const name = path.basename(dir);
      const detected = detectForDir(dir, name, cwd);
      if (detected) results.push(detected);
    }
  }

  // CI configs
  results.push(...detectCiTestCommands(cwd));

  // Task runners
  results.push(...detectTaskRunnerTestCommands(cwd));

  // Python, Go, Rust
  results.push(...detectPythonTestCommands(cwd));
  results.push(...detectGoTestCommands(cwd));
  results.push(...detectRustTestCommands(cwd));

  console.log(JSON.stringify(results, null, 2));
}

main();
