"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../lib/api";
import type { PhotoCard } from "../lib/types";
import Icon from "./Icon";
import PhotoGrid from "./PhotoGrid";
import BottomNav from "./BottomNav";
import ErrorState from "./ErrorState";

function dateLabel(value: string) {
  return new Date(value + "T12:00:00").toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric", year: "numeric" });
}
export default function Gallery() {
  const [photos, setPhotos] = useState<PhotoCard[]>([]), [loading, setLoading] = useState(true), [error, setError] = useState(false), [retry, setRetry] = useState(0);
  useEffect(() => { const controller = new AbortController(); setLoading(true); setError(false);
    api.photos(controller.signal).then(data => setPhotos(data.items)).catch(() => { if (!controller.signal.aborted) setError(true); }).finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [retry]);
  const groups = photos.reduce<Record<string, PhotoCard[]>>((acc, p) => { const date = p.taken_at?.slice(0, 10) || "No date"; (acc[date] ||= []).push(p); return acc; }, {});
  return <main className="gallery-screen">
    <header className="home-topbar"><div className="library-identity"><div className="neutral-mark"><Icon name="photo_library" size={23} /></div><span>Demo library</span></div><div className="home-tools"><Icon name="notifications_none" /><span className="initial-avatar">S</span></div></header>
    <Link href="/search" className="home-search"><Icon name="search" /><span>Search your photos</span></Link>
    <div className="gallery-heading"><h1>Photos</h1><span>{photos.length ? `${photos.length} memories` : "Your demo library"}</span></div>
    {loading && <div className="progress-bar" role="progressbar" aria-label="Loading photos" />}
    {error ? <ErrorState retry={() => setRetry(retry + 1)} /> : loading ? <div className="skeleton-grid">{Array.from({ length: 12 }, (_, i) => <div key={i} />)}</div> : Object.entries(groups).map(([date, items]) => <section key={date}><h2 className="date-header">{date === "No date" ? date : dateLabel(date)}</h2><PhotoGrid photos={items} back="/" /></section>)}
    <footer className="gallery-credit">Curated memories · <a href="/demo/SOURCES.md" target="_blank" rel="noreferrer">Photo credits</a></footer>
    <BottomNav />
  </main>;
}
