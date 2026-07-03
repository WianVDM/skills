/**
 * Minimal Mustache-like template renderer.
 *
 * Supports:
 *   - {{variable}} replacement
 *   - {{#section}} ... {{/section}} for truthy values and arrays
 *   - {{^section}} ... {{/section}} for falsy values and empty arrays
 *   - {{.}} for the current item in array iteration
 *   - Dot paths for nested values: {{gate_results.0.gate}}
 *
 * This is intentionally small to avoid external dependencies.
 */

function getValue(obj, path) {
  if (path === ".") return obj;
  const keys = path.split(".");
  let value = obj;
  for (const key of keys) {
    if (value == null) return "";
    value = value[key];
    if (value == null) return "";
  }
  return value;
}

function escapeHtml(text) {
  if (text == null) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderSection(template, data, escapeValues) {
  const pattern = /\{\{\{?([#/^])?\s*([\w.]+)\s*\}?\}\}/g;
  let result = "";
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(template)) !== null) {
    const [fullMatch, modifier, name] = match;
    const raw = fullMatch.includes("{{{");
    const value = getValue(data, name);

    result += template.slice(lastIndex, match.index);

    const openTag = `{{${modifier || ""}${name}}}`;
    const closeTag = `{{/${name}}}`;
    const openIndex = template.indexOf(openTag, match.index);

    if (!modifier) {
      if (raw) {
        result += String(value ?? "");
      } else {
        result += escapeValues ? escapeHtml(value) : String(value ?? "");
      }
      lastIndex = match.index + fullMatch.length;
      continue;
    }

    if (openIndex === -1) {
      lastIndex = match.index + fullMatch.length;
      continue;
    }
    const innerStart = openIndex + openTag.length;
    const innerEnd = template.indexOf(closeTag, innerStart);
    if (innerEnd === -1) {
      lastIndex = match.index + fullMatch.length;
      continue;
    }
    const inner = template.slice(innerStart, innerEnd);
    const sectionEnd = innerEnd + closeTag.length;

    if (modifier === "#") {
      if (!value) {
        // skip
      } else if (Array.isArray(value)) {
        for (const item of value) {
          result += renderSection(inner, item, escapeValues);
        }
      } else if (typeof value === "boolean") {
        // Boolean section: render with current data context
        result += renderSection(inner, data, escapeValues);
      } else {
        result += renderSection(inner, value, escapeValues);
      }
    } else if (modifier === "^") {
      if (Array.isArray(value) && value.length === 0) {
        result += renderSection(inner, data, escapeValues);
      } else if (!value) {
        result += renderSection(inner, data, escapeValues);
      }
    }

    lastIndex = sectionEnd;
    pattern.lastIndex = lastIndex;
  }

  result += template.slice(lastIndex);
  return result;
}

function renderTemplate(template, data, escapeValues = true) {
  return renderSection(template, data, escapeValues);
}

module.exports = { renderTemplate, getValue };
