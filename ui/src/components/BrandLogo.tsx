import { cn } from "@/lib/utils";

// Reusable Dograh wordmark. Theme-aware by default: the dark logo shows on light
// surfaces and the light/cream logo shows on dark. Pass `inverse` to force the
// light logo on an always-dark surface (e.g. the auth brand panel). Pass `mark`
// to render the square logo mark instead of the full wordmark (e.g. the app
// sidebar header). Height is controlled by the caller via className (e.g.
// "h-7"); width stays auto so each lockup keeps its aspect ratio.
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
      <div className={cn("inline-flex items-center justify-center font-bold tracking-wider rounded-lg bg-emerald-600 text-white px-2 py-1 text-xs select-none", className)}>
        GQ
      </div>
    );
  }

  return (
    <div className={cn("inline-flex items-center gap-2 font-bold tracking-tight text-lg select-none", inverse ? "text-white" : "text-foreground", className)}>
      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-600 font-extrabold text-white text-xs shadow-sm">
        GQ
      </div>
      <span className="font-semibold text-foreground tracking-tight">
        {appName}
      </span>
    </div>
  );
}
