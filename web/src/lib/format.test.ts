import { describe, expect, it } from "vitest";
import { money, percent, quantity, signedMoney, tone } from "./format";

describe("format", () => {
  it("formats money from API decimal strings", () => {
    expect(money("1234.5")).toBe("$1,234.50");
    expect(money(null)).toBe("—");
    expect(money("not a number")).toBe("—");
  });

  it("signs profit and loss", () => {
    expect(signedMoney("140")).toBe("+$140.00");
    expect(signedMoney("-60")).toBe("-$60.00");
    expect(signedMoney("0")).toBe("$0.00");
  });

  it("formats percentages with optional sign", () => {
    expect(percent("10")).toBe("10.00%");
    expect(percent("-10", true)).toBe("-10.00%");
    expect(percent("3.456", true)).toBe("+3.46%");
    expect(percent(null)).toBe("—");
  });

  it("keeps fractional quantities", () => {
    expect(quantity("0.125000")).toBe("0.125");
    expect(quantity("1200")).toBe("1,200");
  });

  it("classifies gains and losses", () => {
    expect(tone("5")).toBe("gain");
    expect(tone("-0.01")).toBe("loss");
    expect(tone(null)).toBe("flat");
  });
});
