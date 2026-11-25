export type Repository = {
  id: number;
  github_owner: string;
  github_repo: string;
  full_name: string;
  html_url: string;
  description: string | null;
  default_branch: string;
  is_private: boolean;
  last_scanned_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Scan = {
  id: number;
  repository_id: number;
  status: "pending" | "running" | "completed" | "failed";
  trigger: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  summary: Record<string, unknown> | null;
};

export type Finding = {
  id: number;
  scan_id: number;
  tool: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description: string | null;
  package_name: string | null;
  package_version: string | null;
  fixed_version: string | null;
  advisory_id: string | null;
  file_path: string | null;
  line_number: number | null;
  is_redacted: boolean;
  references: string[] | null;
};

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

const API_URL =
  typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL
    : "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    cache: "no-store",
    headers: { Accept: "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new ApiError(res.status, text || `Request failed with status ${res.status}`);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  repositories: () => request<Repository[]>("/repositories"),
  scans: (repositoryId: number) => request<Scan[]>(`/repositories/${repositoryId}/scans`),
  findings: (repositoryId: number, scanId: number) =>
    request<Finding[]>(`/repositories/${repositoryId}/scans/${scanId}/findings`),
  triggerScan: (repositoryId: number) =>
    request<Scan>(`/repositories/${repositoryId}/scans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    }),
};
