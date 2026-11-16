"use client";

import { useState } from "react";
import type { NewTransaction, Side } from "@/lib/types";

const today = () => new Date().toISOString().slice(0, 10);
const empty = (): NewTransaction => ({ symbol: "", side: "buy", quantity: "", price: "", fee: "0", executed_at: today() });

const inputClass = "tabular w-full rounded-lg border border-line bg-canvas px-3 py-2 outline-none focus:border-accent";

export function TransactionForm({ onSubmit }: { onSubmit: (transaction: NewTransaction) => Promise<void> }) {
  const [form, setForm] = useState<NewTransaction>(empty);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const update = (field: keyof NewTransaction) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((current) => ({ ...current, [field]: event.target.value }));

  return (
    <form
      className="rounded-xl border border-line bg-panel p-4"
      onSubmit={async (event) => {
        event.preventDefault();
        setBusy(true);
        setError(null);
        try {
          await onSubmit({ ...form, symbol: form.symbol.trim().toUpperCase(), fee: form.fee || "0" });
          setForm(empty());
        } catch (caught) {
          setError(caught instanceof Error ? caught.message : "Could not save the transaction.");
        } finally {
          setBusy(false);
        }
      }}
    >
      <h2 className="text-sm font-semibold">Add transaction</h2>
      <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-6">
        <label className="col-span-1 text-xs text-muted">
          Symbol
          <input required value={form.symbol} onChange={update("symbol")} placeholder="AAPL" maxLength={12} className={`${inputClass} mt-1 uppercase`} />
        </label>
        <label className="text-xs text-muted">
          Side
          <select value={form.side} onChange={update("side")} className={`${inputClass} mt-1`}>
            {(["buy", "sell"] as Side[]).map((side) => (
              <option key={side} value={side}>
                {side === "buy" ? "Buy" : "Sell"}
              </option>
            ))}
          </select>
        </label>
        <label className="text-xs text-muted">
          Quantity
          <input required inputMode="decimal" value={form.quantity} onChange={update("quantity")} placeholder="10" className={`${inputClass} mt-1`} />
        </label>
        <label className="text-xs text-muted">
          Price
          <input required inputMode="decimal" value={form.price} onChange={update("price")} placeholder="187.50" className={`${inputClass} mt-1`} />
        </label>
        <label className="text-xs text-muted">
          Fee
          <input inputMode="decimal" value={form.fee} onChange={update("fee")} className={`${inputClass} mt-1`} />
        </label>
        <label className="text-xs text-muted">
          Date
          <input required type="date" max={today()} value={form.executed_at} onChange={update("executed_at")} className={`${inputClass} mt-1`} />
        </label>
      </div>
      <div className="mt-3 flex items-center gap-3">
        <button disabled={busy} className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-canvas disabled:opacity-50">
          {busy ? "Saving…" : "Save transaction"}
        </button>
        {error && (
          <p role="alert" className="text-sm text-loss">
            {error}
          </p>
        )}
      </div>
    </form>
  );
}
