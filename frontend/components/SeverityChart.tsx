"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Pie, PieChart, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

type SeverityChartProps = {
  counts: Record<string, number>;
};

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#64748b"];
const SEVERITIES = ["critical", "high", "medium", "low", "info"];

export function SeverityChart({ counts }: SeverityChartProps) {
  const data = SEVERITIES.map((severity) => ({
    name: severity,
    value: counts[severity] ?? 0,
  }));
  const total = data.reduce((sum, entry) => sum + entry.value, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Vulnerabilities by severity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={data}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={70}
                  outerRadius={90}
                >
                  {data.map((_entry, index) => (
                    <Cell key={SEVERITIES[index]} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-right space-y-1">
            {total === 0 ? (
              <span className="text-gray-500">No findings yet</span>
            ) : (
              SEVERITIES.map((severity, index) => (
                <div key={severity} className="flex items-center gap-1.5">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-sm font-medium">{counts[severity] ?? 0}</span>
                  <span className="text-xs text-gray-500 capitalize">{severity}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
