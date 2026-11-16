export type Side = "buy" | "sell";

export interface Transaction {
  id: number;
  symbol: string;
  side: Side;
  quantity: string;
  price: string;
  fee: string;
  executed_at: string;
}

export interface NewTransaction {
  symbol: string;
  side: Side;
  quantity: string;
  price: string;
  fee: string;
  executed_at: string;
}

export interface Position {
  symbol: string;
  quantity: string;
  average_cost: string;
  cost_basis: string;
  market_price: string | null;
  market_value: string;
  unrealized_pl: string;
  unrealized_pl_pct: string | null;
  realized_pl: string;
  allocation_pct: string | null;
}

export interface Summary {
  cost_basis: string;
  market_value: string;
  unrealized_pl: string;
  unrealized_pl_pct: string | null;
  realized_pl: string;
  total_pl: string;
  positions_count: number;
  unpriced_symbols: string[];
}
