import Link from "next/link";
import Icon from "./Icon";
export default function BottomNav({ active = "photos" }: { active?: "photos" | "search" }) {
  return <nav className="bottom-nav" aria-label="Main navigation"><div className="nav-pill">
    <Link href="/" className={active === "photos" ? "nav-item selected" : "nav-item"}><Icon name="photo_library" filled={active === "photos"} /><span>Photos</span></Link>
    <button className="nav-item" aria-label="Collections (unavailable in demo)"><span>Collections</span></button>
    <button className="nav-item" aria-label="Create (unavailable in demo)"><span>Create</span></button>
  </div><Link href="/search" aria-label="Search" className={active === "search" ? "nav-search selected" : "nav-search"}><Icon name="search" size={28} /></Link></nav>;
}
