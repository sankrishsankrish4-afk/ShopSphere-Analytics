const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface Recommendation {
  product_id: number;
  name: string;
  confidence: number;
  lift: number;
  reason: string;
}

export interface Rule {
  id: number;
  antecedent: number[];
  consequent: number[];
  support: number;
  confidence: number;
  lift: number;
  algorithm: string;
  segment: string | null;
}

export interface RuleListResponse {
  rules: Rule[];
  total: number;
}

export interface Cluster {
  persona_name: string;
  customer_count: number;
  traits: Record<string, number>;
}

export interface AnalyticsSummary {
  total_transactions: number;
  total_products: number;
  total_rules: number;
  avg_lift: number;
  top_categories: string[];
}

export interface LiftMatrix {
  categories: string[];
  matrix: number[][];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getRecommendations(cart_items: number[], customer_id?: number | null) {
  return request<Recommendation[]>("/api/recommendations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cart_items, customer_id: customer_id ?? null })
  });
}

export function getRules(params: { algorithm?: string; min_lift?: number; page?: number; page_size?: number } = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") search.set(key, String(value));
  });
  return request<RuleListResponse>(`/api/rules?${search.toString()}`);
}

export function getClusters() {
  return request<Cluster[]>("/api/clusters");
}

export function getAnalyticsSummary() {
  return request<AnalyticsSummary>("/api/analytics/summary");
}

export function getLiftMatrix() {
  return request<LiftMatrix>("/api/analytics/lift-matrix");
}
