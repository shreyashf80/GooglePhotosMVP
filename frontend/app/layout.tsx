import type { Metadata, Viewport } from "next";
import "@fontsource/roboto/400.css";
import "@fontsource/roboto/500.css";
import "material-symbols/outlined.css";
import "./globals.css";
export const metadata: Metadata = { title: "Search Hints · Demo", description: "Find a photo by recognizing the little details you remember." };
export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><div className="app-column">{children}</div></body></html>;
}
