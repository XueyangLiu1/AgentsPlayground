"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

type Overview = {
  unclaimed_this_period: any[];
  sub_gaps: any[];
  fee_due_soon: any[];
  closable_soon: any[];
  family_summary: { month: string; claimed_amount: number; total_amount: number };
};

export default function Home() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setData(await api.get("/dashboard/overview"));
    } catch (e: any) {
      setError(e.message);
    }
  }

  useEffect(() => { load(); }, []);

  async function claim(benefitId: number) {
    await api.post(`/benefits/${benefitId}/claim`, {});
    await load();
  }

  if (error) return <div className="card text-red-600">Error: {error}</div>;
  if (!data) return <div>Loading…</div>;

  const fam = data.family_summary;
  const pct = fam.total_amount > 0 ? Math.round((fam.claimed_amount / fam.total_amount) * 100) : 0;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <section className="card md:col-span-2">
        <div className="flex justify-between items-baseline">
          <h2 className="text-lg font-semibold">Family this month ({fam.month})</h2>
          <span className="text-sm text-slate-500">
            ${fam.claimed_amount.toFixed(2)} / ${fam.total_amount.toFixed(2)}
          </span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2 mt-3">
          <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${pct}%` }} />
        </div>
      </section>

      <section className="card">
        <h2 className="text-lg font-semibold mb-3">Unclaimed this period</h2>
        {data.unclaimed_this_period.length === 0 && (
          <p className="text-slate-500 text-sm">All clear 🎉</p>
        )}
        <ul className="divide-y">
          {data.unclaimed_this_period.map((b) => (
            <li key={`${b.benefit_id}-${b.period}`} className="py-2 flex items-center justify-between gap-2">
              <div>
                <div className="font-medium">{b.benefit_name}</div>
                <div className="text-xs text-slate-500">
                  {b.card_name} · {b.cardholder_name} · {b.period}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="font-semibold">${b.amount.toFixed(2)}</span>
                <button className="btn btn-primary" onClick={() => claim(b.benefit_id)}>
                  Claim
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2 className="text-lg font-semibold mb-3">SUB gaps</h2>
        {data.sub_gaps.length === 0 && <p className="text-slate-500 text-sm">No active SUBs.</p>}
        <ul className="divide-y">
          {data.sub_gaps.map((s) => (
            <li key={s.card_id} className="py-2">
              <div className="font-medium">
                <Link href={`/card/${s.card_id}`} className="hover:underline">{s.card_name}</Link>
                <span className="text-xs text-slate-500 ml-1">({s.cardholder_name})</span>
              </div>
              <div className="text-sm">
                Spend ${s.current_spend.toFixed(2)} / ${s.required_spend.toFixed(2)} —
                <span className={s.remaining_days < 30 ? "text-red-600 font-semibold ml-1" : "ml-1"}>
                  {s.remaining_days} days left
                </span>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2 className="text-lg font-semibold mb-3">Fee due in 30 days</h2>
        {data.fee_due_soon.length === 0 && <p className="text-slate-500 text-sm">Nothing yet.</p>}
        <ul className="divide-y">
          {data.fee_due_soon.map((c) => (
            <li key={c.card_id} className="py-2 flex justify-between">
              <Link href={`/card/${c.card_id}`} className="hover:underline">
                {c.card_name} <span className="text-xs text-slate-500">({c.cardholder_name})</span>
              </Link>
              <span className="text-sm">${c.annual_fee?.toFixed(2)} on {c.next_fee_date}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2 className="text-lg font-semibold mb-3">Closable in 30 days</h2>
        {data.closable_soon.length === 0 && <p className="text-slate-500 text-sm">Nothing yet.</p>}
        <ul className="divide-y">
          {data.closable_soon.map((c) => (
            <li key={c.card_id} className="py-2 flex justify-between">
              <Link href={`/card/${c.card_id}`} className="hover:underline">
                {c.card_name} <span className="text-xs text-slate-500">({c.cardholder_name})</span>
              </Link>
              <span className="text-sm">on {c.can_close_after_date}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
