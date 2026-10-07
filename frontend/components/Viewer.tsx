"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { api } from "../lib/api";
import { safeBack } from "../lib/search-state";
import type { PhotoDetail } from "../lib/types";
import Icon from "./Icon";
import ErrorState from "./ErrorState";

type Credit = { id: string; creator: string; source_url: string };
export default function Viewer({ id }: { id: string }) {
  const params = useSearchParams();
  const back = safeBack(params.get("back"));
  const [photo, setPhoto] = useState<PhotoDetail | null>(null), [error, setError] = useState(false), [retry, setRetry] = useState(0), [info, setInfo] = useState(false), [found, setFound] = useState(params.get("found") === "1"), [credit, setCredit] = useState<Credit | null>(null);
  useEffect(() => { const controller = new AbortController(); setError(false);
    api.photo(id, controller.signal).then(setPhoto).catch(() => { if (!controller.signal.aborted) setError(true); });
    fetch("/demo/sources.json", { signal: controller.signal }).then(r => r.json()).then((sources: Credit[]) => setCredit(sources.find(c => c.id === id) || null)).catch(() => {});
    return () => controller.abort();
  }, [id, retry]);
  useEffect(() => { function close(e: KeyboardEvent) { if (e.key === "Escape") setInfo(false); } document.addEventListener("keydown", close); return () => document.removeEventListener("keydown", close); }, []);
  const date = photo?.taken_at ? new Date(photo.taken_at) : null;
  function succeed() {
    if (found) return;
    setFound(true);
    const url = new URL(window.location.href); url.searchParams.set("found", "1");
    window.history.replaceState(null, "", url);
  }
  let touchY = 0;
  return <main className="viewer-screen" onTouchStart={e => { touchY = e.touches[0].clientY; }} onTouchEnd={e => { if (touchY - e.changedTouches[0].clientY > 70) setInfo(true); }}>
    <header className="viewer-header"><Link href={back} className="icon-button" aria-label="Back to results"><Icon name="arrow_back" /></Link><div className="viewer-date"><strong>{date?.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" }) || "Photo"}</strong><span>{date?.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }).toLowerCase()}</span></div><div className="viewer-top-actions"><button className="icon-button" aria-label="Favorite (unavailable in demo)"><Icon name="star_outline" /></button><button className="icon-button" aria-label="Photo information" onClick={() => setInfo(true)}><Icon name="more_vert" /></button></div></header>
    {error ? <ErrorState message="This photo couldn't be loaded. Try again." retry={() => setRetry(retry + 1)} /> : photo ? <div className="viewer-image"><img src={photo.full_url} alt={photo.caption} /></div> : <div className="viewer-loading" role="status">Loading photo…</div>}
    <div className="viewer-bottom">
      {found && <div className="found-message" role="status"><span className="found-check"><Icon name="check" size={20} /></span><div><strong>Thanks! You found it.</strong><span>A little detail brought it back.</span></div></div>}
      {photo && <button className={`found-button ${found ? "is-found" : ""}`} disabled={found} onClick={succeed}><Icon name={found ? "check_circle" : "check"} size={21} />{found ? "Photo found" : "This is it"}</button>}
      <div className="viewer-action-bar"><button aria-label="Share (unavailable in demo)"><Icon name="share" /><span>Share</span></button><button aria-label="Edit (unavailable in demo)"><Icon name="tune" /><span>Edit</span></button><button aria-label="Add to (unavailable in demo)"><Icon name="add" /><span>Add to</span></button><button aria-label="Info" onClick={() => setInfo(true)}><Icon name="info" /><span>Info</span></button></div>
    </div>
    {info && photo && <div className="sheet-overlay" onClick={() => setInfo(false)}><section className="info-sheet" role="dialog" aria-modal="true" aria-label="Photo information" onClick={e => e.stopPropagation()}><div className="sheet-handle" /><button className="sheet-close icon-button" aria-label="Close information" onClick={() => setInfo(false)}><Icon name="close" /></button><h2>{date?.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric" })}</h2><p className="info-time">{date?.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}</p><p className="info-caption">{photo.caption}</p><div className="info-row"><Icon name="location_on" /><div><strong>{photo.city[0].toUpperCase() + photo.city.slice(1)}</strong><span>{photo.setting[0].toUpperCase() + photo.setting.slice(1)}</span></div></div>{photo.people_names.length > 0 && <div className="info-row"><Icon name="person" /><div><strong>People</strong><span>{photo.people_names.map(n => n[0].toUpperCase() + n.slice(1)).join(", ")}</span></div></div>}<p className="demo-info-note">Demo library · Dates, places and names are curated labels.</p>{credit && <a className="photo-credit" href={credit.source_url} target="_blank" rel="noreferrer">Photo by {credit.creator} on Pexels ↗</a>}</section></div>}
  </main>;
}
