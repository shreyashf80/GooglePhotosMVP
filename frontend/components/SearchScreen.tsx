"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api } from "../lib/api";
import { freshSearch, readSearch, searchUrl } from "../lib/search-state";
import type { DropAction, Filter, SearchRequest, SearchResponse } from "../lib/types";
import PhotoGrid from "./PhotoGrid";
import Icon from "./Icon";
import ErrorState from "./ErrorState";

export default function SearchScreen() {
  const router = useRouter(), params = useSearchParams();
  const serialized = params.toString();
  const state = useMemo(() => readSearch(new URLSearchParams(serialized)), [serialized]);
  const [draft, setDraft] = useState(state.query), [result, setResult] = useState<SearchResponse | null>(null), [loading, setLoading] = useState(false), [error, setError] = useState(false), [retry, setRetry] = useState(0);
  useEffect(() => setDraft(state.query), [state.query]);
  useEffect(() => {
    const controller = new AbortController(); setError(false);
    if (!state.query) { setResult(null); setLoading(false); return () => controller.abort(); }
    setLoading(true);
    api.search(state, controller.signal).then(setResult).catch(() => { if (!controller.signal.aborted) setError(true); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [state, retry]);
  const update = (next: SearchRequest) => router.push(searchUrl(next), { scroll: false });
  function addFilter(filter: Filter) { update({ ...state, filters: [...state.filters, filter] }); }
  function applyDrop(action: DropAction) {
    if (action.type === "remove_concept") update({ ...state, removed_concept_ids: [...state.removed_concept_ids, action.concept_id] });
    else if (action.type === "remove_filter") update({ ...state, filters: state.filters.filter((_, i) => i !== action.index) });
    else update({ ...state, concept_overrides: [...state.concept_overrides.filter(c => c.id !== action.concept_id), { ...action.with, id: action.concept_id }] });
  }
  const count = result?.n_results || 0;
  const hasQuery = Boolean(state.query);
  const back = searchUrl(state);
  return <main className="search-screen" aria-busy={loading}>
    <header className="search-header"><Link href="/" className="icon-button" aria-label="Back to photos"><Icon name="arrow_back" /></Link><form className="search-form" onSubmit={e => { e.preventDefault(); update(freshSearch(draft.trim())); }}>
      <input aria-label="Search your photos" placeholder="Search your photos" value={draft} onChange={e => setDraft(e.target.value)} autoFocus={!state.query} maxLength={300} enterKeyHint="search" />
      {draft && <button type="button" className="icon-button" aria-label="Clear search" onClick={() => { setDraft(""); update(freshSearch()); }}><Icon name="close" size={21} /></button>}
    </form></header>
    {loading && <div className="progress-bar" role="progressbar" aria-label="Searching photos" />}
    {!hasQuery ? <section className="empty-search"><div className="empty-search-art"><Icon name="search" size={38} /><span className="art-small"><Icon name="photo" size={21} /></span></div><h1>Search the way<br />you remember it</h1><p>A place. A person. A little detail.</p><div className="examples">{["cafe in Goa", "beach sunset", "medicine"].map(example => <button key={example} className="example-chip" onClick={() => { setDraft(example); update(freshSearch(example)); }}><Icon name="search" size={18} />{example}</button>)}</div></section> : <>
      <div className="active-chips" aria-label="Active search details">
        {(result?.concepts || []).map(c => <button key={c.id} className="active-chip concept-chip" disabled={loading} aria-label={`Remove ${c.label}`} onClick={() => update({ ...state, removed_concept_ids: [...state.removed_concept_ids, c.id] })}>{c.label}<Icon name="close" size={16} /></button>)}
        {state.filters.map((f, i) => <button key={JSON.stringify(f) + i} className="active-chip" disabled={loading} aria-label={`Remove ${f.label}`} onClick={() => update({ ...state, filters: state.filters.filter((_, index) => i !== index) })}><Icon name={f.facet === "when" ? "calendar_today" : f.facet === "who" ? "person" : "filter_alt"} size={15} />{f.label}<Icon name="close" size={16} /></button>)}
      </div>
      {error ? <ErrorState retry={() => setRetry(retry + 1)} /> : result ? <>
        <div className="results-heading"><h1>{count === 1 ? "1 photo" : `${count} photos`}</h1><button className="not-finding" disabled={loading} onClick={() => update({ ...state, want_drop: !state.want_drop })}>Not finding it?</button></div>
        {result.hints.length > 0 && <section className="hints-section" aria-label="Search Hints">
          <div className="hints-intro"><Icon name="lightbulb" size={19} /><span>Remember a little more?</span></div>
          {result.hints.map(row => <div className="hint-row" key={row.facet}><h2>{row.label}</h2><div className="hint-values">{row.values.map(value => <button key={JSON.stringify(value.filter)} className="hint-chip" disabled={loading} onClick={() => addFilter(value.filter)} aria-label={`${value.label}, ${value.count} ${value.count === 1 ? "photo" : "photos"}`}><img src={value.thumb_url} alt="" /><span>{value.label} <span className="chip-count">· {value.count}</span></span></button>)}</div></div>)}
        </section>}
        {(state.want_drop || count <= 1) && <section className="drop-section" aria-label="Recovery suggestions"><h2>NOT FINDING IT? TRY</h2><div className="drop-options">{result.drop.map((drop, i) => <button key={i} className={`drop-chip ${drop.kind === "nearest" ? "nearest-chip" : ""}`} disabled={loading} onClick={() => applyDrop(drop.action)}><Icon name={drop.kind === "nearest" ? "history" : "remove_circle_outline"} size={18} /><span>{drop.label}</span></button>)}</div>{result.drop.length === 0 && count === 0 && !result.message && <p>No photos match. Try fewer words, or something you can see in the photo.</p>}</section>}
        {result.message && <p className="search-message">{result.message}</p>}
        {count > 0 && <PhotoGrid photos={result.results} back={back} />}
        {count > 0 && <div className="end-results"><Icon name="check" size={18} /><span>You&apos;re all caught up</span></div>}
      </> : <div className="search-loading">Finding your photos…</div>}
    </>}
  </main>;
}
