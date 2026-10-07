import type { Concept, Filter, SearchRequest } from "./types";

export function freshSearch(query = ""): SearchRequest {
  return { query, removed_concept_ids: [], concept_overrides: [], filters: [], hints_on: true, want_drop: false };
}
function parseArray<T>(value: string | null): T[] {
  if (!value || value.length > 12000) return [];
  try { const parsed = JSON.parse(value); return Array.isArray(parsed) ? parsed.slice(0, 50) : []; } catch { return []; }
}
export function readSearch(params: URLSearchParams): SearchRequest {
  const filters = parseArray<Filter>(params.get("filters")).filter(f => f && (f.facet === "when" ? typeof f.start === "string" && typeof f.end === "string" && typeof f.label === "string" : (f.facet === "who" || f.facet === "also") && typeof f.value === "string" && typeof f.label === "string"));
  const month = params.get("month");
  if (month && /^20\d{2}-(0[1-9]|1[0-2])$/.test(month)) {
    const [year, m] = month.split("-").map(Number);
    const start = `${month}-01T00:00:00`;
    const end = `${m === 12 ? year + 1 : year}-${String(m === 12 ? 1 : m + 1).padStart(2, "0")}-01T00:00:00`;
    const label = new Date(`${month}-01T12:00:00`).toLocaleDateString("en-GB", { month: "long", year: "numeric" });
    filters.push({ facet: "when", level: "month", label, start, end });
  }
  return {
    ...freshSearch(params.get("q")?.slice(0, 300) || ""), filters,
    removed_concept_ids: parseArray<string>(params.get("removed")).filter(x => typeof x === "string"),
    concept_overrides: parseArray<Concept>(params.get("overrides")).filter(c => c && typeof c.id === "string" && typeof c.label === "string" && (c.kind === "thing" || c.kind === "time") && Array.isArray(c.synonyms)),
    want_drop: params.get("drop") === "1",
  };
}
export function searchUrl(state: SearchRequest): string {
  const p = new URLSearchParams();
  if (state.query) p.set("q", state.query);
  if (state.filters.length) p.set("filters", JSON.stringify(state.filters));
  if (state.removed_concept_ids.length) p.set("removed", JSON.stringify(state.removed_concept_ids));
  if (state.concept_overrides.length) p.set("overrides", JSON.stringify(state.concept_overrides));
  if (state.want_drop) p.set("drop", "1");
  return "/search" + (p.size ? `?${p}` : "");
}
export function safeBack(value: string | null): string {
  return value && (value === "/" || value === "/search" || value.startsWith("/search?")) ? value : "/";
}
