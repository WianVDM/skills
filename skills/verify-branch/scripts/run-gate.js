#!/usr/bin/env node
/**
 * run-gate.js
 *
 * Generic gate runner for the verify-branch skill.
 *
 * Thin orchestrator that selects an adapter for a gate, executes it, and
 * forwards the normalized adapter output to stdout. It is the bridge between
 * subagents and the concrete adapter implementations.
 *
 * Usage:
 *   cat input.json | node scripts/run-gate.js --gate my-gate --adapter my-adapter
 *
 * Input JSON (via stdin):
 *   {
 *     "project_root": "/path/to/project",
 *     "base_branch": "origin/main",
 *     "changed_files": [{ "path": "src/app/billing.ts", "status": "M" }],
 *     "config": {
 *       "enabled": true,
 *       "adapter": "my-adapter",
 *       "fallback_adapters": ["fallback-adapter"],
 *       "command": null,
 *       "cwd": ".",
 *       "timeout": 120
 *     }
 *   }
 *
 * Output JSON (to stdout):
 *   The exact output produced by the selected adapter, or an ERROR object if no
 *   adapter could be executed.
 *
 * Adapter discovery:
 *   Adapters are discovered in the following order:
 *     1. Paths from config.adapter_paths
 *     2. {project_root}/.agents/verify-branch/adapters
 *     3. Extension directories (env or config)
 *     4. Skill built-in adapters (flat layout)
 *     5. Skill built-in adapters (legacy category layout)
 *
 * Exit behavior:
 *   - Exit 0 if an adapter was successfully executed and returned valid JSON,
 *     even if the adapter reported FAIL.
 *   - Exit non-zero only if the runner itself could not execute any adapter
 *     (missing adapter, spawn error, invalid JSON, etc.).
 *
 * Rules:
 *   - Deterministic for the same gate, adapter order, and input.
 *   - No interactive prompts.
 *   - All runner errors are logged to stderr and surfaced as JSON on stdout.
 */

const { spawn } = require("child_process");
const {
  buildAdapterSearchPath,
  resolveAdapter,
  resolveAdapterWithDiagnostics,
} = require("./lib/resolve-adapter");

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = { gate: null, adapter: null };
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--gate" || arg === "-g") {
      parsed.gate = args[i + 1] || null;
      i++;
    } else if (arg === "--adapter" || arg === "-a") {
      parsed.adapter = args[i + 1] || null;
      i++;
    } else if (arg.startsWith("--gate=")) {
      parsed.gate = arg.slice("--gate=".length);
    } else if (arg.startsWith("--adapter=")) {
      parsed.adapter = arg.slice("--adapter=".length);
    }
  }
  return parsed;
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf-8");
    process.stdin.on("data", (chunk) => {
      data += chunk;
    });
    process.stdin.on("end", () => {
      resolve(data);
    });
    process.stdin.on("error", (err) => {
      reject(err);
    });
  });
}

function parseInput(raw) {
  if (!raw || !raw.trim()) {
    throw new Error("No input provided on stdin");
  }
  try {
    return JSON.parse(raw.trim());
  } catch (err) {
    throw new Error("Invalid JSON on stdin: " + err.message);
  }
}

function buildAdapterCandidates(gate, cliAdapter, config) {
  const candidates = [];
  const cfg = config || {};

  // CLI adapter takes precedence over config.adapter.
  const primary = cliAdapter || cfg.adapter;
  if (primary) {
    candidates.push(primary);
  }

  // Config fallbacks are tried after the primary.
  if (Array.isArray(cfg.fallback_adapters)) {
    for (const fallback of cfg.fallback_adapters) {
      if (fallback && fallback !== primary && !candidates.includes(fallback)) {
        candidates.push(fallback);
      }
    }
  }

  return candidates;
}

function executeAdapter(adapterPath, input) {
  return new Promise((resolve, reject) => {
    let stdout = "";
    let stderr = "";

    const child = spawn("node", [adapterPath], {
      cwd: process.cwd(),
      env: process.env,
    });

    child.stdin.write(JSON.stringify(input));
    child.stdin.end();

    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });

    child.on("error", (err) => {
      reject(new Error(`Failed to spawn adapter ${adapterPath}: ${err.message}`));
    });

    child.on("close", (code) => {
      if (!stdout.trim()) {
        reject(
          new Error(
            `Adapter ${adapterPath} produced no stdout. stderr: ${stderr.trim() || "(empty)"}`
          )
        );
        return;
      }

      try {
        const output = JSON.parse(stdout.trim());
        resolve({ output, exitCode: code });
      } catch (err) {
        reject(
          new Error(
            `Adapter ${adapterPath} returned invalid JSON: ${err.message}\nstdout:\n${stdout}\nstderr:\n${stderr}`
          )
        );
      }
    });
  });
}

function makeErrorOutput(message, extra = {}) {
  return {
    status: "ERROR",
    findings: [
      {
        file: null,
        line: 0,
        rule: "runner_error",
        severity: "error",
        message,
        introduced: true,
      },
    ],
    summary: message,
    raw_output: "",
    ...extra,
  };
}

async function main() {
  const { gate, adapter: cliAdapter } = parseArgs();

  if (!gate) {
    const message = "Missing required --gate argument";
    console.error(`[run-gate] ${message}`);
    console.log(JSON.stringify(makeErrorOutput(message), null, 2));
    process.exit(1);
  }

  let input;
  try {
    const raw = await readStdin();
    input = parseInput(raw);
  } catch (err) {
    console.error(`[run-gate] ${err.message}`);
    console.log(JSON.stringify(makeErrorOutput(err.message), null, 2));
    process.exit(1);
  }

  const candidates = buildAdapterCandidates(gate, cliAdapter, input.config);

  if (candidates.length === 0) {
    const message = `No adapter specified for gate "${gate}"`;
    console.error(`[run-gate] ${message}`);
    console.log(JSON.stringify(makeErrorOutput(message), null, 2));
    process.exit(1);
  }

  const projectRoot = input.project_root || process.cwd();
  const adapterPaths = input.config?.adapter_paths || input.adapter_paths || [];
  const extensionPaths = input.extension_paths || [];
  const errors = [];

  for (const adapterName of candidates) {
    const { path: adapterPath, error: resolveError, searched } = resolveAdapterWithDiagnostics(
      adapterName,
      {
        gate,
        project_root: projectRoot,
        adapter_paths: adapterPaths,
        extension_paths: extensionPaths,
      }
    );

    if (!adapterPath) {
      const message = resolveError || `Adapter not found: ${adapterName}`;
      console.error(`[run-gate] ${message}`);
      errors.push(message);
      continue;
    }

    try {
      const { output } = await executeAdapter(adapterPath, input);
      console.log(JSON.stringify(output, null, 2));
      process.exit(0);
    } catch (err) {
      console.error(`[run-gate] ${err.message}`);
      errors.push(err.message);
    }
  }

  const tried = candidates.join(", ");
  const message = `No adapter could be executed for gate "${gate}". Tried: ${tried}. Errors: ${errors.join("; ")}`;
  console.error(`[run-gate] ${message}`);
  console.log(JSON.stringify(makeErrorOutput(message, { tried, errors }), null, 2));
  process.exit(1);
}

if (require.main === module) {
  main();
} else {
  module.exports = {
    parseArgs,
    buildAdapterCandidates,
    executeAdapter,
    makeErrorOutput,
    buildAdapterSearchPath,
    resolveAdapter,
    resolveAdapterWithDiagnostics,
  };
}
