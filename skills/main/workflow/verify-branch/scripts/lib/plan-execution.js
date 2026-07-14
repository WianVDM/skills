/**
 * plan-execution.js
 *
 * Plans which gates to run for a verify-branch execution based on config,
 * execution mode, tags, and gate dependencies.
 *
 * Input: a config object from `.agents/config/verify-branch.yaml`.
 * Output: { gates, skipped, errors } where
 *   - gates is an ordered list of gate names to run
 *   - skipped lists gates that were skipped with reasons
 *   - errors lists planning errors (e.g., circular dependencies)
 */

const DEFAULT_MODE = "full";

const MODE_FILTERS = {
  quick: (gateName, gateConfig) => {
    const tags = gateConfig.tags || [];
    const importance = gateConfig.importance;
    if (importance === "required") return true;
    if (tags.includes("fast") || tags.includes("quick")) return true;
    return false;
  },
  full: () => true,
  "security-audit": (gateName, gateConfig) => {
    const tags = gateConfig.tags || [];
    return tags.includes("security");
  },
};

function isGateEnabled(gateConfig) {
  if (!gateConfig) return false;
  if (gateConfig.enabled === false) return false;
  if (gateConfig.enabled === "auto") return true;
  return gateConfig.enabled !== false;
}

function filterByMode(gates, mode) {
  const filter = MODE_FILTERS[mode] || MODE_FILTERS[DEFAULT_MODE];
  const passed = [];
  const skipped = [];
  for (const [name, config] of gates) {
    if (filter(name, config)) {
      passed.push([name, config]);
    } else {
      skipped.push({ gate: name, reason: `excluded by execution mode '${mode}'` });
    }
  }
  return { passed, skipped };
}

function filterByTags(gates, requiredTags) {
  if (!Array.isArray(requiredTags) || requiredTags.length === 0) {
    return { passed: gates, skipped: [] };
  }
  const passed = [];
  const skipped = [];
  for (const [name, config] of gates) {
    const tags = config.tags || [];
    if (requiredTags.every((t) => tags.includes(t))) {
      passed.push([name, config]);
    } else {
      skipped.push({ gate: name, reason: `missing required tags: ${requiredTags.filter((t) => !tags.includes(t)).join(", ")}` });
    }
  }
  return { passed, skipped };
}

function topologicalSort(gates) {
  const order = [];
  const visited = new Set();
  const visiting = new Set();
  const errors = [];

  function visit(name, config) {
    if (visiting.has(name)) {
      errors.push({ gate: name, reason: `circular dependency detected involving ${name}` });
      return;
    }
    if (visited.has(name)) return;
    visiting.add(name);

    const deps = Array.isArray(config.depends_on) ? config.depends_on : [];
    for (const dep of deps) {
      if (dep === name) {
        errors.push({ gate: name, reason: `gate depends on itself` });
        continue;
      }
      const depConfig = config._all_gates ? config._all_gates[dep] : null;
      if (!depConfig) {
        errors.push({ gate: name, reason: `depends on unknown gate '${dep}'` });
        continue;
      }
      visit(dep, depConfig);
    }

    visiting.delete(name);
    visited.add(name);
    order.push(name);
  }

  // Build lookup and attach it to each config for recursive access.
  const allGates = Object.fromEntries(gates);
  for (const [name, config] of gates) {
    config._all_gates = allGates;
  }

  for (const [name, config] of gates) {
    visit(name, config);
  }

  return { order, errors };
}

function planExecution(config) {
  if (!config || typeof config !== "object") {
    return { gates: [], skipped: [], errors: [{ gate: "*", reason: "invalid config object" }] };
  }

  const preferences = config.preferences || {};
  const mode = preferences.execution_mode || DEFAULT_MODE;
  const requiredTags = preferences.tags || [];
  const gatesConfig = preferences.gates || {};

  const allGates = Object.entries(gatesConfig)
    .filter(([, gateConfig]) => isGateEnabled(gateConfig))
    .map(([name, gateConfig]) => [name, gateConfig]);

  const disabled = Object.entries(gatesConfig)
    .filter(([, gateConfig]) => !isGateEnabled(gateConfig))
    .map(([name]) => ({ gate: name, reason: "gate is disabled" }));

  const modeFilter = filterByMode(allGates, mode);
  const tagFilter = filterByTags(modeFilter.passed, requiredTags);
  const sort = topologicalSort(tagFilter.passed);

  const skipped = [...disabled, ...modeFilter.skipped, ...tagFilter.skipped];

  return {
    gates: sort.order,
    skipped,
    errors: sort.errors,
  };
}

module.exports = {
  planExecution,
  DEFAULT_MODE,
  MODE_FILTERS,
  isGateEnabled,
  filterByMode,
  filterByTags,
  topologicalSort,
};
