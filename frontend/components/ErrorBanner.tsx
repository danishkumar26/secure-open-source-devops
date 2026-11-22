"use client";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";

type ErrorBannerProps = {
  message: string;
  onRetry: () => void;
};

export function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <Alert className="border-red-200 bg-red-50">
      <span className="text-red-800">{message}</span>
      <Button variant="outline" size="sm" onClick={onRetry} className="ml-3">
        Retry
      </Button>
    </Alert>
  );
}
