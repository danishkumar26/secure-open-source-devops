"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

type AlertProps = React.HTMLAttributes<HTMLDivElement>;

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("rounded-lg border p-4", className)} {...props} />
));
Alert.displayName = "Alert";

export { Alert };
