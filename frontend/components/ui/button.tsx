"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "destructive";
  size?: "default" | "sm";
}

const variants = {
  default: "bg-gray-900 text-white hover:bg-gray-800",
  outline: "border border-gray-200 bg-white hover:bg-gray-50",
  destructive: "bg-red-600 text-white hover:bg-red-700",
};

const sizes = { default: "h-10 px-4 py-2", sm: "h-9 px-3" };

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", disabled, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-900 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled}
      {...props}
    />
  ),
);
Button.displayName = "Button";

export { Button };
