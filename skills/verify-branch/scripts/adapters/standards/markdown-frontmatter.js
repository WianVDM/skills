#!/usr/bin/env node
/**
 * markdown-frontmatter adapter
 *
 * Reads standards from Markdown frontmatter sources and applies lightweight
 * heuristic checks to changed files. The body of the Markdown file is ignored
 * for rule extraction.
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
      // Ensure all sources are treated as markdown-frontmatter unless overridden.
      const config = parsed.config || {};
      const sources = Array.isArray(config.sources) ? config.sources : [];
      const typedSources = sources.map((s) => ({ ...s, type: "markdown-frontmatter" }));
      const result = runStandardsCheck({
        ...parsed,
        config: { ...config, sources: typedSources },
      });
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
            summary: `markdown-frontmatter adapter error: ${err.message}`,
          },
          null,
          2
        )
      );
    }
  });
}

main();
