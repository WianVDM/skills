const fs = require("fs");
const path = require("path");

const SKILL_ADAPTER_DIR = path.join(__dirname, "..", "adapters");

/**
 * Build a list of directories to search for adapters, in priority order.
 *
 * Order:
 *   1. Project adapters from config.adapter_paths
 *   2. Project default adapter directory: {project_root}/.agents/verify-branch/adapters
 *   3. Global extension adapters (if provided via env or extension_paths)
 *   4. Skill built-in adapters (new flat layout first, then legacy category layout)
 *
 * @param {object} options
 * @param {string} options.project_root
 * @param {string[]} options.adapter_paths - extra adapter directories from config
 * @param {string[]} options.extension_paths - global extension directories
 * @returns {string[]}
 */
function buildAdapterSearchPath({ project_root, adapter_paths = [], extension_paths = [] }) {
  const dirs = [];

  // Project-configured adapter paths.
  for (const raw of adapter_paths) {
    if (!raw) continue;
    const resolved = path.isAbsolute(raw) ? raw : path.join(project_root, raw);
    dirs.push(resolved);
  }

  // Project default adapter directory.
  dirs.push(path.join(project_root, ".agents", "verify-branch", "adapters"));

  // Global extension directories.
  for (const raw of extension_paths) {
    if (!raw) continue;
    const resolved = path.isAbsolute(raw) ? raw : path.join(project_root, raw);
    dirs.push(resolved);
  }

  // Extension directory from environment (harness-level extension).
  if (process.env.VERIFY_BRANCH_EXTENSION_DIR) {
    dirs.push(process.env.VERIFY_BRANCH_EXTENSION_DIR);
  }

  // Skill built-in adapters - new flat layout.
  dirs.push(SKILL_ADAPTER_DIR);

  // Skill built-in adapters - legacy layout by category.
  dirs.push(path.join(SKILL_ADAPTER_DIR, "test"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "spec-coverage"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "standards"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "dead-code"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "complexity"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "duplication"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "security"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "style"));
  dirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", "architecture"));

  return dirs;
}

/**
 * Resolve an adapter script path given a gate and adapter name.
 *
 * Supports legacy resolution (gate category) and open registry (adapter by name).
 *
 * @param {string} adapterName
 * @param {object} options
 * @param {string} options.gate - gate name or static-analysis/{sub-gate}
 * @param {string} options.project_root
 * @param {string[]} options.adapter_paths
 * @param {string[]} options.extension_paths
 * @returns {string|null}
 */
function resolveAdapter(adapterName, options = {}) {
  if (!adapterName) return null;

  const { gate, project_root, adapter_paths, extension_paths } = options;
  const searchDirs = buildAdapterSearchPath({ project_root, adapter_paths, extension_paths });

  // Try exact adapter name first (e.g., knip.js).
  for (const dir of searchDirs) {
    const candidate = path.join(dir, `${adapterName}.js`);
    if (fs.existsSync(candidate)) return candidate;
  }

  // Legacy: try gate-category subdirectories for backwards compatibility.
  if (gate) {
    const gateParts = gate.split("/").filter(Boolean);
    const category = gateParts[0];
    const subGate = gateParts[1];

    const legacyDirs = [];
    if (subGate && category === "static-analysis") {
      legacyDirs.push(path.join(SKILL_ADAPTER_DIR, "static-analysis", subGate));
    } else if (category) {
      legacyDirs.push(path.join(SKILL_ADAPTER_DIR, category));
    }

    for (const dir of legacyDirs) {
      const candidate = path.join(dir, `${adapterName}.js`);
      if (fs.existsSync(candidate)) return candidate;
    }
  }

  return null;
}

/**
 * Resolve an adapter and return an error message if not found.
 *
 * @param {string} adapterName
 * @param {object} options
 * @returns {{path: string|null, error: string|null, searched: string[]}}
 */
function resolveAdapterWithDiagnostics(adapterName, options = {}) {
  const { gate, project_root, adapter_paths, extension_paths } = options;
  const searched = buildAdapterSearchPath({ project_root, adapter_paths, extension_paths });
  const adapterPath = resolveAdapter(adapterName, { gate, project_root, adapter_paths, extension_paths });
  if (adapterPath) {
    return { path: adapterPath, error: null, searched };
  }
  const error = `Adapter "${adapterName}" not found for gate "${gate || "unknown"}". Searched: ${searched.join(", ")}`;
  return { path: null, error, searched };
}

module.exports = {
  buildAdapterSearchPath,
  resolveAdapter,
  resolveAdapterWithDiagnostics,
};
