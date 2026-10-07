import { API_BASE_URL } from "./config";
import type { PhotoCard, PhotoDetail, SearchRequest, SearchResponse } from "./types";

// The UI consumes only these contracts. Replace the backend URL, not the screens.
async function request<T>(path: string, options: RequestInit = {}, signal?: AbortSignal): Promise<T> {
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options, headers: { "Content-Type": "application/json", ...options.headers },
        signal: signal ? AbortSignal.any([signal, AbortSignal.timeout(12000)]) : AbortSignal.timeout(12000),
      });
      if (!response.ok) throw new Error(response.status === 404 ? "Photo not found." : "Something went wrong. Try again.");
      return await response.json() as T;
    } catch (error) {
      if (signal?.aborted) throw error;
      if (attempt === 0 && error instanceof Error && error.name === "TimeoutError") continue;
      throw error;
    }
  }
  throw new Error("Something went wrong. Try again.");
}
export const api = {
  photos: (signal?: AbortSignal) => request<{ items: PhotoCard[]; next_cursor: string | null }>("/api/photos", {}, signal),
  photo: (id: string, signal?: AbortSignal) => request<PhotoDetail>(`/api/photos/${encodeURIComponent(id)}`, {}, signal),
  search: (state: SearchRequest, signal?: AbortSignal) => request<SearchResponse>("/api/search", { method: "POST", body: JSON.stringify(state) }, signal),
};
