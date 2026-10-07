import { Suspense } from "react";
import Viewer from "../../../components/Viewer";
export default async function PhotoPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <Suspense fallback={<div className="viewer-loading">Loading photo…</div>}><Viewer id={id} /></Suspense>;
}
