"use client";

import { useCallback, useEffect, useState } from "react";
import { AllocationBar } from "@/components/AllocationBar";
import { PositionsTable } from "@/components/PositionsTable";
import { SummaryCards } from "@/components/SummaryCards";
import { TransactionForm } from "@/components/TransactionForm";
import { TransactionsTable } from "@/components/TransactionsTable";
import { api } from "@/lib/api";
import type { NewTransaction, Position, Summary, Transaction } from "@/lib/types";

interface Dashboard {
  summary: Summary;
  positions: Position[];
  transactions: Transaction[];
}

export default function Home() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [summary, positions, transactions] = await Promise.all([api.summary(), api.positions(), api.transactions()]);
      setData({ summary, positions, transactions });
      setError(null);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Could not load the portfolio.");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const addTransaction = async (transaction: NewTransaction) => {
    await api.addTransaction(transaction);
    await load();
  };
  const deleteTransaction = async (id: number) => {
    await api.deleteTransaction(id);
    await load();
  };
  const setPrice = async (symbol: string, price: string) => {
    await api.setPrice(symbol, price);
    await load();
  };

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-8">
      <header className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Portfolio Tracker</h1>
          <p className="text-sm text-muted">Positions at average cost, with realised and unrealised profit and loss.</p>
        </div>
        {data && data.summary.unpriced_symbols.length > 0 && (
          <p className="text-sm text-amber-300">No price for {data.summary.unpriced_symbols.join(", ")}: valued at cost.</p>
        )}
      </header>

      {error && (
        <div role="alert" className="flex items-center justify-between rounded-xl border border-loss/40 bg-loss/10 px-4 py-3 text-sm">
          <span>{error}</span>
          <button type="button" onClick={() => void load()} className="font-medium underline">
            Retry
          </button>
        </div>
      )}

      {!data && !error && <div className="h-40 animate-pulse rounded-xl bg-panel" aria-label="Loading" />}

      {data && (
        <>
          <SummaryCards summary={data.summary} />
          <AllocationBar positions={data.positions} />
          <PositionsTable positions={data.positions} onSetPrice={setPrice} />
          <TransactionForm onSubmit={addTransaction} />
          <TransactionsTable transactions={data.transactions} onDelete={deleteTransaction} />
        </>
      )}
    </main>
  );
}
