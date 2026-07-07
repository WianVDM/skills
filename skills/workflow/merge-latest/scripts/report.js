#!/usr/bin/env node
/**
 * report.js — generate the merge report and chat summary.
 *
 * Reads JSON from stdin with the merge result and writes a markdown report
 * to disk. Prints a concise chat summary to stdout.
 *
 * Usage:
 *   node report.js --out .merge-latest/my-branch-merge-report.md
 */

const fs = require('fs');
const path = require('path');

function parseArgs() {
  const args = process.argv.slice(2);
  const result = {};
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].replace(/^--/, '');
    result[key] = args[i + 1];
  }
  return result;
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', chunk => { data += chunk; });
    process.stdin.on('end', () => {
      try {
        resolve(JSON.parse(data));
      } catch (err) {
        reject(new Error('Invalid JSON on stdin'));
      }
    });
  });
}

function formatCommitList(commits) {
  if (!commits || commits.length === 0) return '_None_';
  return commits.map(c => `- \`${c.hash.slice(0, 8)}\` ${c.subject}`).join('\n');
}

function formatFileList(files) {
  if (!files || files.length === 0) return '_None_';
  return files.map(f => `- ${f}`).join('\n');
}

function renderReport(data) {
  const now = new Date().toISOString();

  const conflictSection = (data.conflicts || []).map(c => {
    const resolution = c.resolution || 'paused';
    const reason = c.reason || 'semantic conflict';
    return `### ${c.file}\n- Classification: ${c.classification}\n- Resolution: ${resolution}\n- Reason: ${reason}`;
  }).join('\n\n') || '_No conflicts_';

  const trivialSection = (data.trivialResolutions || []).map(r => {
    return `- ${r.file}: ${r.reason}`;
  }).join('\n') || '_None_';

  const branchInference = data.branchInference || {};
  const fetchResult = data.fetchResult || {};

  const investigationSection = (data.conflictInvestigation || []).map(b => {
    return `### ${b.file}\n- Recommendation: ${b.recommendation}\n- Confidence: ${b.confidence}\n- Downstream risk: ${b.downstreamRisk}\n- Reason: ${b.reason}`;
  }).join('\n\n') || '_No deep investigation_';

  return `# Merge Report: ${data.target} ← ${data.upstream}

## Summary
- Result: ${data.result}
- Upstream: ${data.upstream} (${data.upstreamCommit?.slice(0, 8) || 'unknown'})
- Target: ${data.target} (${data.targetCommit?.slice(0, 8) || 'unknown'})
- Remote: ${data.remote || 'unknown'}
- Merge base: ${data.mergeBase?.slice(0, 8) || 'unknown'}
- Build: ${data.build || 'not run'}
- Generated: ${now}

## Branch inference
- Inferred upstream: ${branchInference.inferred || data.upstream}
- Confidence: ${branchInference.confidence || 'unknown'}
- Method: ${branchInference.method || 'unknown'}

## Fetch result
- Remote: ${fetchResult.remote || data.remote || 'unknown'}
- ${fetchResult.targetRef || data.target}: ${fetchResult.targetCommit || 'unknown'}
- ${fetchResult.upstreamRef || data.upstream}: ${fetchResult.upstreamCommit || 'unknown'}
- Local target fast-forwarded: ${fetchResult.targetFastForwarded != null ? fetchResult.targetFastForwarded : 'unknown'}

## Commits introduced from upstream
${formatCommitList(data.upstreamCommits)}

## Files touched by upstream
${formatFileList(data.upstreamFiles)}

## Files touched by target
${formatFileList(data.targetFiles)}

## Conflicts
${conflictSection}

## Trivial resolutions applied
${trivialSection}

## Conflict investigation
${investigationSection}

## Build output
\`\`\`
${data.buildOutput || 'N/A'}
\`\`\`

## Next steps
${data.nextSteps || 'Review the merge and push when ready.'}
`;
}

function renderChatSummary(data) {
  const lines = [
    `**Merge ${data.result}: \`${data.target}\` ← \`${data.upstream}\`**`,
    `- Conflicts: ${(data.conflicts || []).length}`,
    `- Trivial resolutions: ${(data.trivialResolutions || []).length}`,
    `- Build: ${data.build || 'not run'}`,
  ];

  const semantic = (data.conflicts || []).filter(c => c.classification === 'semantic' && c.resolution !== 'resolved');
  if (semantic.length > 0) {
    lines.push(`- Semantic conflicts requiring action:`);
    for (const c of semantic) {
      lines.push(`  - ${c.file}: ${c.reason}`);
    }
  }

  lines.push(`- Full report: ${data.reportPath}`);
  lines.push(`- ${data.nextSteps || 'Review and push when ready.'}`);

  return lines.join('\n');
}

async function main() {
  const args = parseArgs();
  if (!args.out) {
    console.error('Usage: node report.js --out <path>');
    process.exit(1);
  }

  const outPath = path.resolve(args.out);

  try {
    const data = await readStdin();
    data.reportPath = outPath;

    const report = renderReport(data);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, report, 'utf8');

    console.log(renderChatSummary(data));
  } catch (err) {
    console.error('report failed:', err.message);
    process.exit(1);
  }
}

main();
