"use client";

import Link from "next/link";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type Repository } from "@/lib/api";

type RepositoryTableProps = {
  repositories: Repository[];
  onScan: (repository: Repository) => Promise<void>;
  scanning: number | null;
  scanErrors: Record<number, string>;
};

export function RepositoryTable({
  repositories,
  onScan,
  scanning,
  scanErrors,
}: RepositoryTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Monitored repositories</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Repository</TableHead>
              <TableHead className="w-32">Description</TableHead>
              <TableHead className="w-24">Branch</TableHead>
              <TableHead className="w-16">Private</TableHead>
              <TableHead className="w-32">Last scanned</TableHead>
              <TableHead className="w-20">Scan now</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {repositories.length === 0 ? (
              <TableRow>
                <TableCell>None registered yet.</TableCell>
              </TableRow>
            ) : (
              repositories.map((repository) => (
                <TableRow key={repository.id}>
                  <TableCell className="font-medium">
                    <Link
                      href={repository.html_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-gray-900 hover:underline"
                    >
                      {repository.full_name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {repository.description ?? "—"}
                  </TableCell>
                  <TableCell className="text-sm">{repository.default_branch}</TableCell>
                  <TableCell className="text-sm">
                    <Badge variant="outline">
                      {repository.is_private ? "Yes" : "No"}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">
                    {repository.last_scanned_at ?? "—"}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={scanning === repository.id}
                      onClick={() => onScan(repository)}
                    >
                      {scanning === repository.id ? "Scanning…" : "Scan"}
                    </Button>
                    {scanErrors[repository.id] && (
                      <p className="mt-1 text-xs text-red-600">{scanErrors[repository.id]}</p>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
