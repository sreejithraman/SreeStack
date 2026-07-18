import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
let limit = 8;
let json = false;
let sourceOnly = false;
const queryParts = [];

for (let index = 0; index < args.length; index += 1) {
  const arg = args[index];
  if (arg === "--limit") {
    limit = Number.parseInt(args[index + 1], 10);
    index += 1;
  } else if (arg === "--json") {
    json = true;
  } else if (arg === "--source") {
    sourceOnly = true;
  } else if (arg === "--help" || arg === "-h") {
    console.log("Usage: node scripts/search.mjs <query> [--limit N] [--json]");
    console.log("       node scripts/search.mjs --source");
    process.exit(0);
  } else {
    queryParts.push(arg);
  }
}

if (
  (!sourceOnly && queryParts.length === 0) ||
  !Number.isInteger(limit) ||
  limit < 1
) {
  console.error("Usage: node scripts/search.mjs <query> [--limit N] [--json]");
  process.exit(2);
}

const normalize = (value) =>
  value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

const catalogPath = fileURLToPath(
  new URL("../references/catalog.json", import.meta.url),
);
const catalog = JSON.parse(await readFile(catalogPath, "utf8"));
const rawRoot = `https://raw.githubusercontent.com/ckissi/kinetics/${catalog.source.ref}`;
const source = {
  ...catalog.source,
  index_url: `${rawRoot}/${catalog.source.index}`,
  cards_url: `${rawRoot}/${catalog.source.cards}`,
};
const query = normalize(queryParts.join(" "));
if (sourceOnly) {
  console.log(source.cards_url);
  process.exit(0);
}
if (query.length === 0) {
  console.error("Search query must contain letters or numbers.");
  process.exit(2);
}
const queryTokens = [...new Set(query.split(" ").filter(Boolean))];

const ranked = catalog.effects
  .map((effect) => {
    const name = normalize(effect.name);
    const category = normalize(effect.category);
    const keywords = effect.keywords.map(normalize);
    let score = name === query ? 30 : name.includes(query) ? 14 : 0;

    for (const keyword of keywords) {
      if (keyword === query) score += 12;
      else if (keyword.includes(query) || query.includes(keyword)) score += 5;
    }

    for (const token of queryTokens) {
      const nameTokens = name.split(" ");
      const categoryTokens = category.split(" ");
      if (nameTokens.includes(token)) score += 6;
      else if (name.includes(token)) score += 3;
      if (categoryTokens.includes(token)) score += 2;
      if (keywords.some((keyword) => keyword.split(" ").includes(token))) score += 4;
      else if (keywords.some((keyword) => keyword.includes(token))) score += 2;
    }

    const matches = effect.keywords.filter((keyword) => {
      const normalized = normalize(keyword);
      return queryTokens.some(
        (token) => normalized.includes(token) || token.includes(normalized),
      );
    });

    return { ...effect, score, matches: matches.slice(0, 6) };
  })
  .filter((effect) => effect.score > 0)
  .sort((left, right) =>
    right.score - left.score || left.name.localeCompare(right.name),
  )
  .slice(0, limit);

if (json) {
  console.log(JSON.stringify({ source, query, results: ranked }, null, 2));
  process.exit(0);
}

console.log(`Kinetics ${catalog.source.ref.slice(0, 12)} · ${ranked.length} matches`);
console.log(`Source: ${source.cards_url}`);
for (const [index, effect] of ranked.entries()) {
  console.log(`${index + 1}. ${effect.name} — ${effect.category} (${effect.score})`);
  if (effect.matches.length > 0) console.log(`   ${effect.matches.join(", ")}`);
}
