"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & {
  variant?: "default" | "secondary" | "destructive" | "outline";
};

const variants = {
  default: "bg-gray-900 text-white",
  secondary: "bg-gray-100 text-gray-900 border border-gray-200",
  destructive: "bg-red-600 text-white",
  outline: "border border-gray-200 text-gray-900",
};

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  ),
);
Badge.displayName = "Badge";

export { Badge };
