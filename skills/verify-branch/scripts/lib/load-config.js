const fs = require("fs");
const os = require("os");
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
    throw new Error(`Failed to parse YAML (js-yaml missing and Python fallback failed): ${err.message}`);
  }
}

function readYamlFile(filePath) {
  if (!fs.existsSync(filePath)) {
    return { data: null, error: null };
  }
  try {
    const text = fs.readFileSync(filePath, "utf-8");
    if (!text.trim()) {
      return { data: {}, error: null };
    }
    const data = parseYaml(text);
    return { data: data || {}, error: null };
  } catch (err) {
    return { data: null, error: err.message };
  }
}

function deepMerge(target, source) {
  const result = { ...target };
  for (const key of Object.keys(source)) {
    if (
      source[key] &&
      typeof source[key] === "object" &&
      !Array.isArray(source[key]) &&
      result[key] &&
      typeof result[key] === "object" &&
      !Array.isArray(result[key])
    ) {
      result[key] = deepMerge(result[key], source[key]);
    } else {
      result[key] = source[key];
    }
  }
  return result;
}

function loadConfig(projectRoot) {
  const homeDir = os.homedir();
  const userSharedPath = path.join(homeDir, ".agents", "config", "shared.yaml");
  const userVerifyPath = path.join(homeDir, ".agents", "config", "verify-branch.yaml");
  const sharedPath = path.join(projectRoot, ".agents", "config", "shared.yaml");
  const verifyPath = path.join(projectRoot, ".agents", "config", "verify-branch.yaml");

  const userShared = readYamlFile(userSharedPath);
  const userVerify = readYamlFile(userVerifyPath);
  const shared = readYamlFile(sharedPath);
  const verify = readYamlFile(verifyPath);

  const errors = [];
  const warnings = [];

  if (userShared.error) warnings.push(`User shared.yaml is corrupted: ${userShared.error}`);
  if (userVerify.error) warnings.push(`User verify-branch.yaml is corrupted: ${userVerify.error}`);
  if (shared.error) errors.push(`shared.yaml is corrupted: ${shared.error}`);
  if (verify.error) errors.push(`verify-branch.yaml is corrupted: ${verify.error}`);

  // Merge order: user < project shared < project specific.
  let config = deepMerge(userShared.data || {}, userVerify.data || {});
  config = deepMerge(config, shared.data || {});
  config = deepMerge(config, verify.data || {});

  if (errors.length > 0) {
    return {
      config: null,
      errors,
      warnings,
    };
  }

  return {
    config,
    errors: [],
    warnings,
  };
}

module.exports = {
  loadConfig,
  parseYaml,
  readYamlFile,
  deepMerge,
};
