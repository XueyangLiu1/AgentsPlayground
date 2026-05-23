"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";

export default function HolderPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [holders, setHolders] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);

  async function load() {
    const hs = await api.get("/cardholders");
    setHolders(hs);
    if (id === "all") {
      const all: any[] = [];
      for (const h of hs) {
        const cs = await api.get(`/cardholders/${h.id}/cards`);
        for (const c of cs) all.push({ ...c, _holder: h.name });
      }
      setCards(all);
    } else {
      const cs = await api.get(`/cardholders/${id}/cards`);
      setCards(cs);
    }
  }

  useEffect(() => { load(); }, [id]);

  return (
    <div>
      <div className="flex gap-2 mb-4 flex-wrap">
        <Link href="/holder/all" className={`btn ${id === "all" ? "btn-primary" : "btn-secondary"}`}>All</Link>
        {holders.map((h) => (
          <Link key={h.id}
                href={`/holder/${h.id}`}
                className={`btn ${String(h.id) === id ? "btn-primary" : "btn-secondary"}`}>
            <span className="w-2 h-2 rounded-full mr-2" style={{ background: h.color_tag }} />
            {h.name}
          </Link>
        ))}
      </div>

      {cards.length === 0 && (
        <div className="card text-slate-500">No cards yet. <Link href="/new" className="text-blue-600 hover:underline">Add one →</Link></div>
      )}

      <div className="grid gap-3 md:grid-cols-2">
        {cards.map((c) => {
          const pct = c.period_total > 0 ? Math.round((c.period_claimed / c.period_total) * 100) : 0;
          return (
            <Link key={c.id} href={`/card/${c.id}`} className="card hover:shadow-md transition">
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-semibold">{c.name}</div>
                  <div className="text-xs text-slate-500">
                    {c.issuer}{c._holder ? ` · ${c._holder}` : ""}
                  </div>
                </div>
                <span className={`badge ${
                  c.status === "active" ? "bg-green-100 text-green-700"
                  : c.status === "closed" ? "bg-slate-200 text-slate-700"
                  : "bg-amber-100 text-amber-700"
                }`}>{c.status}</span>
              </div>
              <div className="mt-3 text-sm text-slate-600">Annual fee: ${c.annual_fee.toFixed(2)}</div>
              <div className="mt-2">
                <div className="flex justify-between text-xs text-slate-500 mb-1">
                  <span>Period benefits</span>
                  <span>${c.period_claimed.toFixed(2)} / ${c.period_total.toFixed(2)}</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${pct}%` }} />
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
