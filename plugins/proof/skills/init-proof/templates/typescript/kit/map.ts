import { createHash } from "node:crypto";
import { sourceId } from "./evidence";
import { scenarioId, type Registry } from "./features";

export type MapClause = { text: string; evidence: string[] };
export type MapScenario = { sub: string; id: string; given: string; when: string; then: string; proof: MapClause[]; text: string };
export type FeatureMap = {
  title: string;
  subFeatures: { id: string; description: string }[];
  scenarios: MapScenario[];
  hash: string;
  errors: string[];
};

export const MAP_SECTIONS = ["Sub-features", "How to get to it (user POV)", "Driving it with Mole", "Gotchas"] as const;
const LABEL = /^\*\*\(([a-z][a-z0-9-]*) \| ([a-z][a-z0-9-]*)\):\*\*\s+([\s\S]+)$/;
const BODY = /^\*\*Given\*\*\s+([\s\S]+?);\s+\*\*When\*\*\s+([\s\S]+?);\s+\*\*Then\*\*\s+([\s\S]+?)\.\s+\*\*Proof:\*\*\s+([\s\S]+)$/;
const CLAUSE = /^([\s\S]+?)\s*\(([^()]+)\)$/;

/** Splits a feature map into its sections, sub-features and scenario paragraphs. Format problems come back in `errors`. */
export function parseMap(text: string): FeatureMap {
  const errors: string[] = [];
  const map: FeatureMap = { title: "", subFeatures: [], scenarios: [], hash: createHash("sha256").update(text).digest("hex").slice(0, 16), errors };
  const lines = text.split(/\r?\n/);
  const title = lines.find(line => /^# \S/.test(line));
  if (!title) errors.push("No `# Title` line.");
  else map.title = title.slice(2).trim();
  const sections = new Map<string, string[]>();
  let current: string[] | null = null;
  for (const line of lines) {
    const heading = line.match(/^## (.+?)\s*$/);
    if (heading) {
      if (sections.has(heading[1])) errors.push(`Duplicate section "${heading[1]}".`);
      current = [];
      sections.set(heading[1], current);
    } else if (current) current.push(line);
  }
  const headings = [...sections.keys()];
  for (const name of MAP_SECTIONS) if (!sections.has(name)) errors.push(`Missing section "## ${name}".`);
  for (const name of headings) if (!(MAP_SECTIONS as readonly string[]).includes(name)) errors.push(`Unexpected section "## ${name}". Sections: ${MAP_SECTIONS.join(", ")}.`);
  if (headings.length && MAP_SECTIONS.every(name => sections.has(name)) && MAP_SECTIONS.some((name, i) => headings.filter(h => (MAP_SECTIONS as readonly string[]).includes(h))[i] !== name)) {
    errors.push(`Sections are out of order. Order: ${MAP_SECTIONS.join(", ")}.`);
  }

  for (const line of sections.get("Sub-features") ?? []) {
    if (!line.trim()) continue;
    const item = line.match(/^- `([a-z][a-z0-9-]*)` — (.+)$/);
    if (item) map.subFeatures.push({ id: item[1], description: item[2].trim() });
    else errors.push(`Sub-features: "${line.trim()}" is not "- \`id\` — description".`);
  }

  const paragraphs: string[] = [];
  let open: string[] = [];
  for (const line of sections.get("Driving it with Mole") ?? []) {
    if (line.trim()) open.push(line.trim());
    else if (open.length) { paragraphs.push(open.join(" ")); open = []; }
  }
  if (open.length) paragraphs.push(open.join(" "));
  for (const paragraph of paragraphs) {
    if (/^[-*+]\s/.test(paragraph)) { errors.push(`Scenario entries are not bullets: "${paragraph.slice(0, 60)}".`); continue; }
    const label = paragraph.match(LABEL);
    if (!label) {
      errors.push(/^\*\*Evidence/i.test(paragraph) || /^Evidence/i.test(paragraph)
        ? `Orphan evidence declaration: "${paragraph.slice(0, 60)}". Name evidence in parentheses after each proof check.`
        : `"${paragraph.slice(0, 60)}" does not start with "**(sub-feature-id | scenario-id):**".`);
      continue;
    }
    const where = `(${label[1]} | ${label[2]})`;
    const body = label[3];
    if (/\*\*Evidence/i.test(body)) errors.push(`${where}: no separate **Evidence** clause. Name evidence in parentheses after each check.`);
    if (body.includes("|")) errors.push(`${where}: no pipes between clauses; clauses are separated by semicolons.`);
    const parts = body.match(BODY);
    if (!parts) { errors.push(`${where}: needs "**Given** ...; **When** ...; **Then** .... **Proof:** check (evidence); ...".`); continue; }
    const proofText = parts[4].trim();
    if (!proofText.endsWith(".")) errors.push(`${where}: end the **Proof:** clause with a period.`);
    const proof: MapClause[] = [];
    for (const raw of proofText.replace(/\.$/, "").split(";").map(part => part.trim()).filter(Boolean)) {
      const clause = raw.match(CLAUSE);
      const evidence = clause ? clause[2].split(",").map(name => sourceId(name)).filter(Boolean) : [];
      if (!clause || !evidence.length) errors.push(`${where}: proof check "${raw}" names no evidence. Write "check (evidence)".`);
      else proof.push({ text: clause[1].trim(), evidence });
    }
    if (!proof.length) errors.push(`${where}: needs at least one proof check.`);
    if (map.scenarios.some(s => s.sub === label[1] && s.id === label[2])) errors.push(`${where}: duplicate scenario.`);
    map.scenarios.push({ sub: label[1], id: label[2], given: parts[1].trim(), when: parts[2].trim(), then: parts[3].trim(), proof, text: paragraph });
  }
  for (const scenario of map.scenarios) {
    if (!map.subFeatures.some(sub => sub.id === scenario.sub)) errors.push(`(${scenario.sub} | ${scenario.id}): sub-feature "${scenario.sub}" is not in ## Sub-features.`);
  }
  const subIds = map.subFeatures.map(sub => sub.id);
  for (const id of subIds.filter((id, i) => subIds.indexOf(id) !== i)) errors.push(`Duplicate sub-feature "${id}".`);
  return map;
}

/** The map-level rules that keep Markdown from carrying selectors or wire details: those belong in code. */
export function mapBanned(text: string, banned: readonly RegExp[]): string[] {
  return banned.filter(pattern => pattern.test(text)).map(pattern => `Mentions ${pattern}: that belongs in a page object or an adapter.`);
}

const sameSet = (a: string[], b: string[]) => a.length === b.length && a.every(item => b.includes(item));

/**
 * Markdown against builders, in both directions: a map per feature, a sub-feature and scenario for each label, and for every
 * proof clause the proof check that carries exactly the evidence it names. Returns the problems; none means in step.
 */
export function checkMaps(registry: Registry, maps: Record<string, string>, banned: readonly RegExp[] = []): string[] {
  const problems: string[] = [];
  const names = registry.features.map(feature => feature.name);
  for (const name of Object.keys(maps)) if (!names.includes(name)) problems.push(`${name}.md: map has no feature in the registry.`);
  for (const feature of registry.features) {
    const text = maps[feature.name];
    if (text === undefined) { problems.push(`${feature.name}: no map ${feature.name}.md.`); continue; }
    const map = parseMap(text);
    const at = `${feature.name}.md`;
    problems.push(...map.errors.map(error => `${at}: ${error}`), ...mapBanned(text, banned).map(error => `${at}: ${error}`));
    const mapSubs = map.subFeatures.map(sub => sub.id);
    for (const sub of feature.subFeatures) if (!mapSubs.includes(sub.id)) problems.push(`${at}: sub-feature "${sub.id}" is built but not listed in ## Sub-features.`);
    for (const id of mapSubs) if (!feature.subFeatures.some(sub => sub.id === id)) problems.push(`${at}: sub-feature "${id}" is listed but not built.`);
    for (const sub of feature.subFeatures) {
      for (const scenario of sub.scenarios) {
        if (!map.scenarios.some(entry => entry.sub === sub.id && entry.id === scenario.id)) problems.push(`${at}: scenario ${scenarioId(feature.name, sub.id, scenario.id)} is built but has no \`(${sub.id} | ${scenario.id}):\` paragraph.`);
      }
    }
    for (const entry of map.scenarios) {
      const built = feature.subFeatures.find(sub => sub.id === entry.sub)?.scenarios.find(scenario => scenario.id === entry.id);
      const id = scenarioId(feature.name, entry.sub, entry.id);
      if (!built) { problems.push(`${at}: scenario ${id} is mapped but not built (stale map or missing builder).`); continue; }
      const proofs = built.steps.flatMap(step => (step.kind === "proof" ? [step.check] : []));
      if (proofs.length !== entry.proof.length) problems.push(`${at}: ${id} maps ${entry.proof.length} proof check(s) but the builder attaches ${proofs.length} with .proof().`);
      entry.proof.slice(0, proofs.length).forEach((clause, i) => {
        if (!sameSet(clause.evidence, proofs[i].evidence)) problems.push(`${at}: ${id} proof ${i + 1} ("${clause.text}") names evidence [${clause.evidence.join(", ")}] but "${proofs[i].id}" declares [${proofs[i].evidence.join(", ")}].`);
      });
    }
  }
  return problems;
}
