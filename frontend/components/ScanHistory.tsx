"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { type Scan } from "@/lib/api";

const STATUS_VARIANT: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
  pending: "outline",
  running: "default",
  completed: "default",
  failed: "destructive",
};

type ScanHistoryProps = {
  scans: Scan[];
  repositories: Record<number, string>;
};

export function ScanHistory({ scans, repositories }: ScanHistoryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Scan history</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Repository</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-20">Trigger</TableHead>
              <TableHead className="w-40">Started at</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {scans.length === 0 ? (
              <TableRow>
                <TableCell>No scans yet.</TableCell>
              </TableRow>
            ) : (
              scans.map((scan) => (
                <TableRow key={scan.id}>
                  <TableCell className="text-sm">
                    {repositories[scan.repository_id] ?? String(scan.repository_id)}
                  </TableCell>
                  <TableCell className="text-sm">
                    <Badge variant={STATUS_VARIANT[scan.status] ?? "secondary"}>
                      {scan.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">{scan.trigger}</TableCell>
                  <TableCell className="text-sm text-gray-600">
                    {scan.started_at ?? "—"}
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
