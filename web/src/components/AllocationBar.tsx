import { percent } from "@/lib/format";
import type { Position } from "@/lib/types";

const COLORS = ["#7c9cff", "#34d399", "#fbbf24", "#f472b6", "#38bdf8", "#a78bfa", "#fb923c", "#94a3b8"];

export function AllocationBar({ positions }: { positions: Position[] }) {
  if (positions.length === 0) return null;
  return (
    <section className="rounded-xl border border-line bg-panel p-4">
      <div className="text-xs uppercase tracking-wider text-muted">Allocation by market value</div>
      <div className="mt-3 flex h-3 overflow-hidden rounded-full bg-line" role="img" aria-label="Portfolio allocation">
        {positions.map((p, i) => (
          <div key={p.symbol} style={{ width: `${Number(p.allocation_pct ?? 0)}%`, background: COLORS[i % COLORS.length] }} />
        ))}
      </div>
      <ul className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm">
        {positions.map((p, i) => (
          <li key={p.symbol} className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: COLORS[i % COLORS.length] }} />
            <span className="font-medium">{p.symbol}</span>
            <span className="tabular text-muted">{percent(p.allocation_pct)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
