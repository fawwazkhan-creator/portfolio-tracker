"use client";

import { useState } from "react";
import { money, quantity } from "@/lib/format";
import type { Transaction } from "@/lib/types";

export function TransactionsTable({ transactions, onDelete }: { transactions: Transaction[]; onDelete: (id: number) => Promise<void> }) {
  const [pending, setPending] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  return (
    <section className="rounded-xl border border-line bg-panel">
      <div className="flex items-center justify-between px-4 pt-4">
        <h2 className="text-sm font-semibold">Transactions</h2>
        {error && (
          <p role="alert" className="text-sm text-loss">
            {error}
          </p>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="mt-2 w-full min-w-[640px] text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-muted">
            <tr className="border-b border-line">
              <th className="px-4 py-2">Date</th>
              <th className="px-4 py-2">Symbol</th>
              <th className="px-4 py-2">Side</th>
              <th className="px-4 py-2 text-right">Quantity</th>
              <th className="px-4 py-2 text-right">Price</th>
              <th className="px-4 py-2 text-right">Fee</th>
              <th className="px-4 py-2" />
            </tr>
          </thead>
          <tbody>
            {transactions.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-muted">
                  No transactions recorded.
                </td>
              </tr>
            )}
            {transactions.map((t) => (
              <tr key={t.id} className="border-b border-line/60 last:border-0">
                <td className="tabular px-4 py-2 text-muted">{t.executed_at}</td>
                <td className="px-4 py-2 font-medium">{t.symbol}</td>
                <td className={`px-4 py-2 ${t.side === "buy" ? "text-gain" : "text-loss"}`}>{t.side === "buy" ? "Buy" : "Sell"}</td>
                <td className="tabular px-4 py-2 text-right">{quantity(t.quantity)}</td>
                <td className="tabular px-4 py-2 text-right">{money(t.price)}</td>
                <td className="tabular px-4 py-2 text-right text-muted">{money(t.fee)}</td>
                <td className="px-4 py-2 text-right">
                  <button
                    type="button"
                    disabled={pending === t.id}
                    onClick={async () => {
                      if (!window.confirm(`Delete this ${t.side} of ${t.symbol}?`)) return;
                      setPending(t.id);
                      setError(null);
                      try {
                        await onDelete(t.id);
                      } catch (caught) {
                        setError(caught instanceof Error ? caught.message : "Could not delete the transaction.");
                      } finally {
                        setPending(null);
                      }
                    }}
                    className="text-xs text-muted hover:text-loss disabled:opacity-50"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
