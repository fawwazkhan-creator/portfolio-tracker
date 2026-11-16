import type { NewTransaction, Position, Summary, Transaction } from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

function describe(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item?.loc) ? item.loc.at(-1) : "";
        return field ? `${field}: ${item.msg}` : String(item?.msg ?? "");
      })
      .join("; ");
  }
  return "Something went wrong. Please try again.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(describe(body.detail), response.status);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const api = {
  summary: () => request<Summary>("/summary"),
  positions: () => request<Position[]>("/positions"),
  transactions: () => request<Transaction[]>("/transactions"),
  addTransaction: (body: NewTransaction) =>
    request<Transaction>("/transactions", { method: "POST", body: JSON.stringify(body) }),
  deleteTransaction: (id: number) => request<void>(`/transactions/${id}`, { method: "DELETE" }),
  setPrice: (symbol: string, price: string) =>
    request(`/prices/${encodeURIComponent(symbol)}`, { method: "PUT", body: JSON.stringify({ price }) }),
};
