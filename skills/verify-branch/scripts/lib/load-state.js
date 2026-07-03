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
    throw new Error(`Failed to parse YAML frontmatter (js-yaml missing and Python fallback failed): ${err.message}`);
  }
}

function parseFrontmatter(text) {
  if (!text || !text.startsWith("---")) {
    return { frontmatter: {}, body: text || "" };
  }
  const end = text.indexOf("---", 3);
  if (end === -1) {
    return { frontmatter: {}, body: text };
  }
  const frontmatterText = text.slice(3, end).trim();
  const body = text.slice(end + 3).trimStart();
  try {
    const frontmatter = frontmatterText ? parseYaml(frontmatterText) : {};
    return { frontmatter: frontmatter || {}, body };
  } catch (err) {
    throw new Error(`Invalid frontmatter YAML: ${err.message}`);
  }
}

function loadState(statePath) {
  if (!fs.existsSync(statePath)) {
    return {
      state: null,
      error: null,
      exists: false,
    };
  }

  try {
    const text = fs.readFileSync(statePath, "utf-8");
    const { frontmatter, body } = parseFrontmatter(text);
    return {
      state: {
        ...frontmatter,
        body,
      },
      error: null,
      exists: true,
    };
  } catch (err) {
    return {
      state: null,
      error: err.message,
      exists: true,
    };
  }
}

function loadStateForBranch(projectRoot, branch) {
  const safeBranch = branch.replace(/[^\w\-]/g, "_");
  const statePath = path.join(projectRoot, ".agents", "context", "verify-branch", `${safeBranch}-state.md`);
  return loadState(statePath);
}

module.exports = {
  loadState,
  loadStateForBranch,
  parseFrontmatter,
  parseYaml,
};
