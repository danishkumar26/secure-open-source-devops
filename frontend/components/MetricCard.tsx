"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type MetricCardProps = {
  title: string;
  value: React.ReactNode;
  status?: "ok" | "down";
};

export function MetricCard({ title, value, status }: MetricCardProps) {
  return (
    <Card className={status === "down" ? "border-red-200" : undefined}>
      <CardHeader className="space-y-1">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {status && (
          <Badge
            variant={status === "ok" ? "secondary" : "destructive"}
            className="mt-2 inline-block"
          >
            {status}
          </Badge>
        )}
      </CardContent>
    </Card>
  );
}
