"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";

const STATUSES = ["active", "pending_downgrade", "pending_close", "closed"];

export default function CardPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = Number(params.id);
  const [tab, setTab] = useState<"benefits" | "sub" | "reminders">("benefits");
  const [card, setCard] = useState<any>(null);
  const [holder, setHolder] = useState<any>(null);
  const [benefits, setBenefits] = useState<any[]>([]);
  const [progress, setProgress] = useState<any[]>([]);
  const [subs, setSubs] = useState<any[]>([]);
  const [reminders, setReminders] = useState<any[]>([]);

  async function load() {
    const c = await api.get(`/cards/${id}`);
    setCard(c);
    setHolder(await api.get(`/cardholders/${c.cardholder_id}`));
    setBenefits(await api.get(`/benefits?card_id=${id}`));
    setSubs(await api.get(`/sign-up-bonuses?card_id=${id}`));
    setReminders(await api.get(`/reminders?card_id=${id}`));
  }

  useEffect(() => { load(); }, [id]);

  async function loadProgress(benefitId: number) {
    setProgress(await api.get(`/benefit-progress?benefit_id=${benefitId}`));
  }

  async function claim(benefitId: number) {
    await api.post(`/benefits/${benefitId}/claim`, {});
    await load();
  }

  async function setStatus(status: string) {
    await api.patch(`/cards/${id}`, { status });
    await load();
  }

  async function removeCard() {
    if (!confirm("Delete this card and all its data?")) return;
    await api.delete(`/cards/${id}`);
    router.push("/holder/all");
  }

  if (!card) return <div>Loading…</div>;

  return (
    <div>
      <div className="card mb-4">
        <div className="flex justify-between items-start gap-3 flex-wrap">
          <div>
            <h1 className="text-xl font-semibold">{card.name}</h1>
            <div className="text-sm text-slate-500">
              {card.issuer} · {holder?.name} · annual fee ${card.annual_fee.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              Opened {card.opened_date} · Next fee {card.next_fee_date} · Closable after {card.can_close_after_date}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select className="input w-auto" value={card.status} onChange={(e) => setStatus(e.target.value)}>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
            <button className="btn btn-danger" onClick={removeCard}>Delete</button>
          </div>
        </div>
      </div>

      <div className="flex gap-2 mb-3">
        {(["benefits", "sub", "reminders"] as const).map((t) => (
          <button key={t}
                  className={`btn ${tab === t ? "btn-primary" : "btn-secondary"}`}
                  onClick={() => setTab(t)}>
            {t === "benefits" ? "Benefits" : t === "sub" ? "Sign-up Bonus" : "Reminders"}
          </button>
        ))}
      </div>

      {tab === "benefits" && (
        <div className="card">
          {benefits.length === 0 && <div className="text-sm text-slate-500">No benefits.</div>}
          <ul className="divide-y">
            {benefits.map((b) => (
              <li key={b.id} className="py-2">
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-medium">{b.name}</div>
                    <div className="text-xs text-slate-500">
                      ${b.amount} · {b.frequency} · {b.cycle_type} · {b.category}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button className="btn btn-secondary" onClick={() => loadProgress(b.id)}>History</button>
                    <button className="btn btn-primary" onClick={() => claim(b.id)}>Claim</button>
                  </div>
                </div>
                {progress.filter((p) => p.benefit_id === b.id).map((p) => (
                  <div key={p.id} className="ml-4 text-xs text-slate-500 mt-1">
                    · {p.period}: ${p.claimed_amount} on {p.claimed_date} {p.claimed_by ? `by ${p.claimed_by}` : ""}
                  </div>
                ))}
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab === "sub" && (
        <div className="card">
          {subs.length === 0 && <div className="text-sm text-slate-500">No SUB.</div>}
          {subs.map((s) => {
            const pct = s.required_spend > 0 ? Math.round((s.current_spend / s.required_spend) * 100) : 0;
            return (
              <div key={s.id} className="py-2">
                <div className="font-medium">{s.reward_description}</div>
                <div className="text-xs text-slate-500">Deadline: {s.deadline_date}</div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 bg-slate-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${Math.min(100, pct)}%` }} />
                  </div>
                  <span className="text-sm">${s.current_spend} / ${s.required_spend}</span>
                </div>
                <input type="number" className="input mt-2" defaultValue={s.current_spend}
                       onBlur={async (e) => {
                         const v = parseFloat(e.target.value);
                         if (!isNaN(v)) {
                           await api.patch(`/sign-up-bonuses/${s.id}`, {
                             current_spend: v,
                             completed: v >= s.required_spend,
                           });
                           await load();
                         }
                       }} />
              </div>
            );
          })}
        </div>
      )}

      {tab === "reminders" && (
        <div className="card">
          {reminders.length === 0 && <div className="text-sm text-slate-500">No reminders.</div>}
          <ul className="divide-y">
            {reminders.map((r) => (
              <li key={r.id} className="py-2 flex justify-between">
                <div>
                  <div className="font-medium">{r.title}</div>
                  <div className="text-xs text-slate-500">Due {r.due_date} · {r.status} · {r.recurring}</div>
                </div>
                <div className="flex gap-2">
                  <button className="btn btn-secondary" onClick={async () => {
                    await api.patch(`/reminders/${r.id}`, { status: "done" });
                    await load();
                  }}>Done</button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
