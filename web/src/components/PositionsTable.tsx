"use client";

import { useState } from "react";
import { money, percent, quantity, signedMoney, tone } from "@/lib/format";
import type { Position } from "@/lib/types";

const toneClass = { gain: "text-gain", loss: "text-loss", flat: "text-muted" } as const;

function PriceCell({ position, onSetPrice }: { position: Position; onSetPrice: (symbol: string, price: string) => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(position.market_price ?? "");
  const [busy, setBusy] = useState(false);

  if (!editing) {
    return (
      <button
        type="button"
        onClick={() => setEditing(true)}
        className="tabular rounded px-1 underline decoration-dotted underline-offset-4 hover:text-accent"
        title="Update price"
      >
        {position.market_price ? money(position.market_price) : "Set price"}
      </button>
    );
  }

  return (
    <form
      className="flex justify-end gap-1"
      onSubmit={async (event) => {
        event.preventDefault();
        setBusy(true);
        try {
          await onSetPrice(position.symbol, value);
          setEditing(false);
        } finally {
          setBusy(false);
        }
      }}
    >
      <input
        autoFocus
        inputMode="decimal"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="tabular w-24 rounded border border-line bg-canvas px-2 py-1 text-right"
        aria-label={`New price for ${position.symbol}`}
      />
      <button disabled={busy || !value} className="rounded bg-accent px-2 text-sm font-medium text-canvas disabled:opacity-50">
        Save
      </button>
    </form>
  );
}

export function PositionsTable({ positions, onSetPrice }: { positions: Position[]; onSetPrice: (symbol: string, price: string) => Promise<void> }) {
  return (
    <section className="overflow-x-auto rounded-xl border border-line bg-panel">
      <table className="w-full min-w-[720px] text-sm">
        <thead className="text-left text-xs uppercase tracking-wider text-muted">
          <tr className="border-b border-line">
            <th className="px-4 py-3">Symbol</th>
            <th className="px-4 py-3 text-right">Quantity</th>
            <th className="px-4 py-3 text-right">Avg cost</th>
            <th className="px-4 py-3 text-right">Price</th>
            <th className="px-4 py-3 text-right">Value</th>
            <th className="px-4 py-3 text-right">Unrealised</th>
            <th className="px-4 py-3 text-right">Realised</th>
          </tr>
        </thead>
        <tbody>
          {positions.length === 0 && (
            <tr>
              <td colSpan={7} className="px-4 py-8 text-center text-muted">
                No open positions yet. Add a buy transaction to get started.
              </td>
            </tr>
          )}
          {positions.map((p) => (
            <tr key={p.symbol} className="border-b border-line/60 last:border-0">
              <td className="px-4 py-3 font-semibold">{p.symbol}</td>
              <td className="tabular px-4 py-3 text-right">{quantity(p.quantity)}</td>
              <td className="tabular px-4 py-3 text-right">{money(p.average_cost)}</td>
              <td className="px-4 py-3 text-right">
                <PriceCell position={p} onSetPrice={onSetPrice} />
              </td>
              <td className="tabular px-4 py-3 text-right">{money(p.market_value)}</td>
              <td className={`tabular px-4 py-3 text-right ${toneClass[tone(p.unrealized_pl)]}`}>
                {signedMoney(p.unrealized_pl)}
                <div className="text-xs">{percent(p.unrealized_pl_pct, true)}</div>
              </td>
              <td className={`tabular px-4 py-3 text-right ${toneClass[tone(p.realized_pl)]}`}>{signedMoney(p.realized_pl)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
