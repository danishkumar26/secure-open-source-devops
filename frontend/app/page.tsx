"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface Repository {
  id: number;
  full_name: string;
  html_url: string;
  description: string | null;
}

export default function Dashboard() {
  const API_URL =
    (typeof process !== "undefined" &&
      process.env.NEXT_PUBLIC_API_URL) ||
    "http://localhost:8000";
  const [health, setHealth] = useState<string | null>(null);
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [healthRes, repoRes] = await Promise.all([
          fetch(`${API_URL}/health`, { cache: "no-store" }),
          fetch(`${API_URL}/repositories`, { cache: "no-store" }),
        ]);
        if (cancelled) return;
        if (healthRes.ok) {
          setHealth((await healthRes.json()).status as string);
        } else {
          setHealth(`error ${healthRes.status}`);
        }
        if (repoRes.ok) {
          setRepositories((await repoRes.json()) as Repository[]);
        } else {
          setError(`repositories ${repoRes.status}`);
        }
      } catch (err) {
        if (cancelled) return;
        setError(String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main>
      <h1>Secure Open Source DevOps Platform</h1>
      <p>Backend health: {health ?? "checking…"}</p>
      {error && <p style={{ color: "b71c1c" }}>Error: {error}</p>}
      <h2>Monitored repositories</h2>
      {repositories.length === 0 ? (
        <p>None registered yet.</p>
      ) : (
        <ul>
          {repositories.map((r) => (
            <li key={r.id}>
              <Link href={r.html_url} target="_blank" rel="noreferrer">
                {r.full_name}
              </Link>
              {r.description ? ` — ${r.description}` : ""}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
