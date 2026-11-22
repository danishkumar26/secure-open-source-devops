"use client";

import { useCallback, useEffect, useState } from "react";
import { api, type Finding, type Repository, type Scan } from "@/lib/api";
import { ErrorBanner } from "@/components/ErrorBanner";
import { MetricCard } from "@/components/MetricCard";
import { RepositoryTable } from "@/components/RepositoryTable";
import { ScanHistory } from "@/components/ScanHistory";
import { SeverityChart } from "@/components/SeverityChart";
import { Skeleton } from "@/components/ui/skeleton";

const SEVERITIES = ["critical", "high", "medium", "low", "info"];

export default function Dashboard() {
  const API_URL =
    (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) ||
    "http://localhost:8000";
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [health, setHealth] = useState<"ok" | "down" | null>(null);
  const [scans, setScans] = useState<Scan[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scanning, setScanning] = useState<number | null>(null);
  const [scanErrors, setScanErrors] = useState<Record<number, string>>({});

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [healthRes, repositoriesRes] = await Promise.all([
        api.health(),
        api.repositories(),
      ]);
      setHealth(healthRes.status === "ok" ? "ok" : "down");
      setRepositories(repositoriesRes);

      // Scan history: latest scans per monitored repository (few repos in dev).
      // shortcut: per-repository requests (N+1); upgrade when the backend adds an
      // aggregated scan-history endpoint.
      const allScans: Scan[] = [];
      await Promise.all(
        repositoriesRes.map(async (repository) => {
          try {
            const repositoryScans = await api.scans(repository.id);
            allScans.push(...repositoryScans.slice(0, 5));
          } catch (err) {
            console.warn(`Failed to load scans for ${repository.full_name}`, err);
          }
        }),
      );
      allScans.sort(
        (a, b) =>
          new Date(b.started_at ?? 0).getTime() - new Date(a.started_at ?? 0).getTime(),
      );
      setScans(allScans.slice(0, 20));

      // Vulnerability summary: findings of the latest completed scan.
      const latest = allScans.find((scan) => scan.status === "completed");
      if (latest) {
        const repository = repositoriesRes.find((r) => r.id === latest.repository_id);
        if (repository) {
          setFindings(await api.findings(repository.id, latest.id));
        } else {
          setFindings([]);
        }
      } else {
        setFindings([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleScan = useCallback(
    async (repository: Repository) => {
      setScanning(repository.id);
      setScanErrors({});
      try {
        await api.triggerScan(repository.id);
        await load();
      } catch (err) {
        setScanErrors((previous) => ({
          ...previous,
          [repository.id]: err instanceof Error ? err.message : String(err),
        }));
      } finally {
        setScanning(null);
      }
    },
    [load],
  );

  const counts = findings.reduce(
    (acc, finding) => {
      acc[finding.severity] = (acc[finding.severity] ?? 0) + 1;
      return acc;
    },
    {} as Record<string, number>,
  );

  if (loading) {
    return (
      <main className="max-w-6xl mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold">Secure Open Source DevOps Platform</h1>
            <p className="text-gray-600">
              Dashboard &middot; monitored repositories, scans, and findings
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((index) => (
            <Skeleton key={index} className="h-20 w-full" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-[300px] w-full" />
          <div className="flex flex-col gap-4">
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-48 w-full" />
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold">Secure Open Source DevOps Platform</h1>
          <p className="text-gray-600">
            Dashboard &middot; monitored repositories, scans, and findings
          </p>
        </div>
        <a
          href={`${API_URL}/docs`}
          target="_blank"
          rel="noreferrer"
          className="text-sm text-gray-600 hover:underline"
        >
          Open API docs &rarr;
        </a>
      </div>

      {error && <ErrorBanner message={error} onRetry={load} />}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <MetricCard
          title="Backend"
          value={
            <span className="flex items-center gap-1">
              {health === "ok" ? (
                <span className="relative flex h-2 w-2">
                  <span className="flex h-2 w-2 rounded-full bg-green-500" />
                </span>
              ) : (
                <span className="relative flex h-2 w-2">
                  <span className="flex h-2 w-2 rounded-full bg-red-500" />
                </span>
              )}
              {health === "ok" ? "Operational" : "Degraded"}
            </span>
          }
          status={health === "ok" ? "ok" : "down"}
        />
        <MetricCard title="Repositories" value={repositories.length} />
        <MetricCard title="Scans" value={scans.length} />
        <MetricCard title="Findings" value={findings.length} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SeverityChart counts={counts} />
        <div className="flex flex-col gap-4">
          <RepositoryTable
            repositories={repositories}
            onScan={handleScan}
            scanning={scanning}
            scanErrors={scanErrors}
          />
          <ScanHistory
            scans={scans}
            repositories={Object.fromEntries(
              repositories.map((repository) => [repository.id, repository.full_name]),
            )}
          />
        </div>
      </div>
    </main>
  );
}
