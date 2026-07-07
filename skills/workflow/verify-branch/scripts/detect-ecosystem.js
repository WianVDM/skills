const fs = require("fs");
const path = require("path");

/**
 * Detect the ecosystem of the project at the given root.
 *
 * This is intentionally lightweight. It looks for marker files and returns
 * the best-matching ecosystem template name. The bootstrap subagent can then
 * load the template and let the user confirm or edit it.
 *
 * @param {string} projectRoot
 * @returns {{ecosystem: string, confidence: string, reason: string}}
 */
function detectEcosystem(projectRoot) {
  if (!fs.existsSync(projectRoot)) {
    return { ecosystem: "default", confidence: "low", reason: "project root does not exist" };
  }

  const has = (name) => fs.existsSync(path.join(projectRoot, name));

  // Mobile
  if (has("pubspec.yaml") || has("Podfile") || has("android") || has("ios")) {
    return { ecosystem: "mobile", confidence: "high", reason: "mobile indicator files" };
  }

  // Node.js / TypeScript / web
  if (has("package.json")) {
    const pkgPath = path.join(projectRoot, "package.json");
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgPath, "utf-8"));
      const deps = {
        ...pkg.dependencies,
        ...pkg.devDependencies,
        ...pkg.peerDependencies,
      };

      if (deps["@angular/core"]) {
        return { ecosystem: "angular", confidence: "high", reason: "Angular dependency detected" };
      }
      if (deps["react"] || deps["react-dom"] || deps["next"]) {
        return { ecosystem: "react", confidence: "high", reason: "React dependency detected" };
      }
      if (deps["vue"] || deps["@vue/runtime-dom"]) {
        return { ecosystem: "node-typescript", confidence: "high", reason: "Vue/Node project" };
      }
      if (deps["svelte"] || deps["solid-js"]) {
        return { ecosystem: "node-typescript", confidence: "high", reason: "Svelte/Solid/Node project" };
      }
      return { ecosystem: "node-typescript", confidence: "medium", reason: "Node.js project without recognized framework" };
    } catch {
      return { ecosystem: "node-typescript", confidence: "low", reason: "package.json present but unreadable" };
    }
  }

  // Python
  if (has("pyproject.toml") || has("requirements.txt") || has("setup.py") || has("setup.cfg")) {
    return { ecosystem: "python", confidence: "high", reason: "Python project files" };
  }

  // Go
  if (has("go.mod")) {
    return { ecosystem: "go", confidence: "high", reason: "Go module" };
  }

  // Rust
  if (has("Cargo.toml")) {
    return { ecosystem: "rust", confidence: "high", reason: "Rust project" };
  }

  // Java
  if (has("pom.xml") || has("build.gradle") || has("build.gradle.kts")) {
    return { ecosystem: "java", confidence: "high", reason: "Java build file" };
  }

  // Terraform / infrastructure
  if (fs.existsSync(path.join(projectRoot, "terraform")) || has("main.tf")) {
    return { ecosystem: "infra-terraform", confidence: "high", reason: "Terraform files" };
  }

  return { ecosystem: "default", confidence: "low", reason: "no recognized ecosystem markers" };
}

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

function main() {
  const { cwd } = parseArgs();
  const result = detectEcosystem(cwd);
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  main();
} else {
  module.exports = { detectEcosystem };
}
