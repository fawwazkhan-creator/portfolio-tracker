import { money, percent, signedMoney, tone } from "@/lib/format";
import type { Summary } from "@/lib/types";

const toneClass = { gain: "text-gain", loss: "text-loss", flat: "text-ink" } as const;

function Card({ label, value, detail, valueTone }: { label: string; value: string; detail?: string; valueTone?: keyof typeof toneClass }) {
  return (
    <div className="rounded-xl border border-line bg-panel p-4">
      <div className="text-xs uppercase tracking-wider text-muted">{label}</div>
      <div className={`tabular mt-2 text-xl font-semibold sm:text-2xl ${toneClass[valueTone ?? "flat"]}`}>{value}</div>
      {detail && <div className="tabular mt-1 text-sm text-muted">{detail}</div>}
    </div>
  );
}

export function SummaryCards({ summary }: { summary: Summary }) {
  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <Card label="Market value" value={money(summary.market_value)} detail={`${summary.positions_count} open positions`} />
      <Card label="Cost basis" value={money(summary.cost_basis)} detail="Average cost, fees included" />
      <Card
        label="Unrealised P/L"
        value={signedMoney(summary.unrealized_pl)}
        detail={percent(summary.unrealized_pl_pct, true)}
        valueTone={tone(summary.unrealized_pl)}
      />
      <Card
        label="Total P/L"
        value={signedMoney(summary.total_pl)}
        detail={`Realised ${signedMoney(summary.realized_pl)}`}
        valueTone={tone(summary.total_pl)}
      />
    </section>
  );
}
