const fs = require("fs");
const path = require("path");
const { renderTemplate } = require("./render-template");

const SKILL_TEMPLATES_DIR = path.join(__dirname, "..", "..", "assets", "templates", "reports");

/**
 * Load a report template by name or path.
 *
 * @param {string} templateName - "default", "compact", "detailed", or a custom path
 * @param {string} customPath - optional override path
 * @returns {string}
 */
function loadTemplate(templateName, customPath) {
  if (customPath) {
    return fs.readFileSync(customPath, "utf-8");
  }
  const templateFile = path.join(SKILL_TEMPLATES_DIR, `${templateName}.md`);
  if (!fs.existsSync(templateFile)) {
    throw new Error(`Report template not found: ${templateName}`);
  }
  return fs.readFileSync(templateFile, "utf-8");
}

/**
 * Prepare render data from gate results and context.
 *
 * @param {object} reportData
 * @returns {object}
 */
function prepareRenderData(reportData) {
  const gateResults = (reportData.gate_results || []).map((g) => ({
    ...g,
    finding_count: Array.isArray(g.findings) ? g.findings.length : 0,
    has_findings: Array.isArray(g.findings) && g.findings.length > 0,
    findings: (g.findings || []).map((f) => ({
      ...f,
      gate: g.gate,
      file: f.file || "—",
      line: f.line ?? "—",
    })),
  }));

  const totalFindings = gateResults.reduce((sum, g) => sum + g.finding_count, 0);

  return {
    ...reportData,
    gate_results: gateResults,
    has_any_findings: totalFindings > 0,
    total_findings: totalFindings,
    has_fresh: (reportData.fresh_context || []).length > 0,
    has_stale: (reportData.stale_context || []).length > 0,
    fresh_context: reportData.fresh_context || [],
    stale_context: reportData.stale_context || [],
    verdict_details_json: JSON.stringify(reportData.verdict_details || {}, null, 2),
  };
}

/**
 * Render a verification report.
 *
 * @param {object} reportData
 * @param {string} reportData.branch
 * @param {string} reportData.base
 * @param {string} reportData.commit
 * @param {string} reportData.generated_at
 * @param {string} reportData.verdict
 * @param {string} reportData.verdict_reason
 * @param {object} reportData.verdict_details
 * @param {object[]} reportData.gate_results
 * @param {object[]} reportData.fresh_context
 * @param {object[]} reportData.stale_context
 * @param {string} templateName - default | compact | detailed
 * @param {string|null} customPath
 * @returns {string}
 */
function renderReport(reportData, templateName = "default", customPath = null) {
  const template = loadTemplate(templateName, customPath);
  const data = prepareRenderData(reportData);
  return renderTemplate(template, data, false); // reports are Markdown, not HTML
}

module.exports = { renderReport, loadTemplate, prepareRenderData };
