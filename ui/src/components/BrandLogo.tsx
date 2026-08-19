import Image from "next/image";
import { cn } from "@/lib/utils";

// Centralized GenQuantaa BrandLogo component.
// Uses brand assets from /brand/ (logo.svg, icon.svg, logo-dark.svg, logo-light.svg)
// with clean text fallbacks.
export function BrandLogo({
  className,
  inverse = false,
  mark = false,
}: {
  className?: string;
  inverse?: boolean;
  mark?: boolean;
}) {
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "GenQuantaa";

  if (mark) {
    return (
      <div className={cn("inline-flex items-center gap-2 select-none", className)}>
        <Image
          src="/brand/icon.svg"
          alt="GenQuantaa"
          width={28}
          height={28}
          className="h-7 w-7 rounded-lg"
        />
      </div>
    );
  }

  return (
    <div className={cn("inline-flex items-center gap-2.5 font-bold tracking-tight text-lg select-none", inverse ? "text-white" : "text-foreground", className)}>
      <Image
        src="/brand/icon.svg"
        alt="GenQuantaa Icon"
        width={28}
        height={28}
        className="h-7 w-7 rounded-lg"
      />
      <span className={cn("font-semibold tracking-tight", inverse ? "text-white" : "text-foreground")}>
        {appName}
      </span>
    </div>
  );
}
