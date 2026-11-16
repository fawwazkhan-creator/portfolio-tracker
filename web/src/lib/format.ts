const currency = process.env.NEXT_PUBLIC_CURRENCY ?? "USD";

const moneyFormat = new Intl.NumberFormat("en-US", { style: "currency", currency, minimumFractionDigits: 2 });
const quantityFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 6 });

export function money(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const amount = Number(value);
  return Number.isFinite(amount) ? moneyFormat.format(amount) : "—";
}

export function signedMoney(value: string | number): string {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "—";
  const text = moneyFormat.format(Math.abs(amount));
  return amount > 0 ? `+${text}` : amount < 0 ? `-${text}` : text;
}

export function percent(value: string | number | null | undefined, signed = false): string {
  if (value === null || value === undefined || value === "") return "—";
  const amount = Number(value);
  if (!Number.isFinite(amount)) return "—";
  const text = `${Math.abs(amount).toFixed(2)}%`;
  if (!signed) return `${amount.toFixed(2)}%`;
  return amount > 0 ? `+${text}` : amount < 0 ? `-${text}` : text;
}

export function quantity(value: string | number): string {
  const amount = Number(value);
  return Number.isFinite(amount) ? quantityFormat.format(amount) : "—";
}

export function tone(value: string | number | null | undefined): "gain" | "loss" | "flat" {
  const amount = Number(value ?? 0);
  return amount > 0 ? "gain" : amount < 0 ? "loss" : "flat";
}
