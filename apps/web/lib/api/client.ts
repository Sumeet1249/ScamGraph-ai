import type { ScamAssessment, CytoscapeGraph, ScamJourney } from "./types";

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(status: number, message: string, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

const BASE_URL =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) ||
  "http://127.0.0.1:8001/api/v1";

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    let detail = "";
    try {
      const errJson = await response.json();
      detail = errJson.detail || errJson.message || "";
    } catch {
      detail = response.statusText;
    }
    throw new ApiError(response.status, `API Error ${response.status}: ${detail}`, detail);
  }

  return response.json();
}

export const api = {
  async getIncidentAssessment(id: string): Promise<ScamAssessment> {
    const data = await apiFetch<ScamAssessment>(`/incidents/${id}/assessment`);
    if (data && typeof data.risk_score === "number" && data.risk_score <= 1.0) {
      data.risk_score = Math.round(data.risk_score * 100);
    }
    return data;
  },

  async getIncidentGraph(id: string): Promise<CytoscapeGraph> {
    return apiFetch<CytoscapeGraph>(`/incidents/${id}/graph`);
  },

  async getIncidentJourney(id: string): Promise<ScamJourney> {
    return apiFetch<ScamJourney>(`/incidents/${id}/journey`);
  },
};
