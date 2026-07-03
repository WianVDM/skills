#!/usr/bin/env node
/**
 * parse-args.js — parse invocation tokens for merge-latest.
 *
 * Supports the following forms:
 *   /merge-latest
 *   /merge-latest <to>
 *   /merge-latest <to> <from>
 *   /merge-latest --from <from>
 *   /merge-latest --to <to> --from <from>
 *   /merge-latest <to> --from <from>
 *
 * Rules:
 *   - Named arguments override positional values.
 *   - If both a named and a positional value are given for the same role,
 *     emit an error.
 *   - More than two positional arguments is an error.
 *   - `--stash` is a boolean flag.
 *
 * Outputs JSON to stdout:
 *   { to: string | null, from: string | null, stash: boolean, errors: string[] }
 *
 * Exits non-zero if errors is non-empty.
 */

function parseArgs(tokens) {
  const named = { to: null, from: null };
  const positionals = [];
  const errors = [];
  let stash = false;

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];

    if (token === '--to') {
      const next = tokens[i + 1];
      if (!next || next.startsWith('--')) {
        errors.push('--to requires a branch name');
      } else {
        named.to = next;
        i++;
      }
      continue;
    }

    if (token === '--from') {
      const next = tokens[i + 1];
      if (!next || next.startsWith('--')) {
        errors.push('--from requires a branch name');
      } else {
        named.from = next;
        i++;
      }
      continue;
    }

    if (token === '--stash') {
      stash = true;
      continue;
    }

    if (token.startsWith('--')) {
      errors.push(`Unknown option: ${token}`);
      continue;
    }

    positionals.push(token);
  }

  if (positionals.length > 2) {
    errors.push(
      `Too many positional arguments: expected at most two (target and upstream), got ${positionals.length}`
    );
  }

  const positionalTo = positionals[0] || null;
  const positionalFrom = positionals[1] || null;

  let to = null;
  if (named.to && positionalTo) {
    errors.push(
      `Target branch specified both as --to ${named.to} and positional ${positionalTo}; please use one form`
    );
  } else if (named.to) {
    to = named.to;
  } else if (positionalTo) {
    to = positionalTo;
  }

  let from = null;
  if (named.from && positionalFrom) {
    errors.push(
      `Upstream branch specified both as --from ${named.from} and positional ${positionalFrom}; please use one form`
    );
  } else if (named.from) {
    from = named.from;
  } else if (positionalFrom) {
    from = positionalFrom;
  }

  return { to, from, stash, errors };
}

function main() {
  // Strip the leading command name if the harness passed it as the first token.
  let tokens = process.argv.slice(2);
  if (tokens[0] === 'merge-latest' || tokens[0] === '/merge-latest') {
    tokens = tokens.slice(1);
  }

  const result = parseArgs(tokens);
  console.log(JSON.stringify(result, null, 2));

  if (result.errors.length > 0) {
    process.exit(1);
  }
}

main();
