import Link from "next/link";
import type { PhotoCard } from "../lib/types";
export default function PhotoGrid({ photos, back }: { photos: PhotoCard[]; back: string }) {
  return <div className="photo-grid">{photos.map((p, index) => <Link key={p.id} className="photo-tile" href={`/photo/${p.id}?back=${encodeURIComponent(back)}`} aria-label={`Open photo ${p.id}`}>
    {/* Local images deliberately bypass a remote image proxy for deploy reliability. */}
    <img src={p.thumb_url} alt={`Photo ${p.id}`} loading={index < 12 ? "eager" : "lazy"} decoding="async" />
  </Link>)}</div>;
}
