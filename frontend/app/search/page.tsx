import { Suspense } from "react";
import SearchScreen from "../../components/SearchScreen";
export default function SearchPage() { return <Suspense fallback={<div className="search-loading">Loading search…</div>}><SearchScreen /></Suspense>; }
