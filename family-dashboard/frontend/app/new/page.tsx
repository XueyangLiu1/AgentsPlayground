"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type Kind = "cardholder" | "card" | "benefit" | "sub" | "reminder";

export default function NewPage() {
  const router = useRouter();
  const [kind, setKind] = useState<Kind>("cardholder");
  const [holders, setHolders] = useState<any[]>([]);
  const [cards, setCards] = useState<any[]>([]);
  const [benefits, setBenefits] = useState<any[]>([]);
  const [presets, setPresets] = useState<any[]>([]);
  const [form, setForm] = useState<any>({});
  const [msg, setMsg] = useState<string | null>(null);

  async function loadDeps() {
    setHolders(await api.get("/cardholders"));
    setCards(await api.get("/cards"));
    setBenefits(await api.get("/benefits"));
    setPresets(await api.get("/presets/cards"));
  }
  useEffect(() => { loadDeps(); }, []);
  useEffect(() => { setForm({}); setMsg(null); }, [kind]);

  function up(k: string, v: any) { setForm((f: any) => ({ ...f, [k]: v })); }

  async function applyPreset(name: string) {
    const p = presets.find((x) => `${x.issuer}::${x.name}` === name);
    if (!p) return;
    up("issuer", p.issuer);
    up("name", p.name);
    up("annual_fee", p.annual_fee);
    up("_preset_benefits", p.benefits);
  }

  async function submit() {
    try {
      setMsg(null);
      if (kind === "cardholder") {
        await api.post("/cardholders", {
          name: form.name,
          color_tag: form.color_tag || "#3b82f6",
        });
        setMsg("Created ✓");
      } else if (kind === "card") {
        const card = await api.post("/cards", {
          cardholder_id: Number(form.cardholder_id),
          issuer: form.issuer,
          name: form.name,
          opened_date: form.opened_date,
          annual_fee: parseFloat(form.annual_fee || "0"),
          fee_waived_first_year: !!form.fee_waived_first_year,
          status: "active",
          next_fee_date: form.next_fee_date,
          can_close_after_date: form.can_close_after_date,
          notes: form.notes,
        });
        if (form._preset_benefits) {
          for (const b of form._preset_benefits) {
            await api.post("/benefits", { ...b, card_id: card.id });
          }
        }
        setMsg(`Card created (id ${card.id}) ✓`);
        router.push(`/card/${card.id}`);
      } else if (kind === "benefit") {
        await api.post("/benefits", {
          card_id: Number(form.card_id),
          name: form.name,
          amount: parseFloat(form.amount || "0"),
          frequency: form.frequency || "monthly",
          cycle_type: form.cycle_type || "statement_month",
          category: form.category || "credit",
          notes: form.notes,
        });
        setMsg("Benefit created ✓");
      } else if (kind === "sub") {
        await api.post("/sign-up-bonuses", {
          card_id: Number(form.card_id),
          required_spend: parseFloat(form.required_spend || "0"),
          deadline_date: form.deadline_date,
          reward_description: form.reward_description,
          current_spend: parseFloat(form.current_spend || "0"),
          completed: false,
        });
        setMsg("SUB created ✓");
      } else if (kind === "reminder") {
        await api.post("/reminders", {
          card_id: form.card_id ? Number(form.card_id) : null,
          title: form.title,
          due_date: form.due_date,
          status: "pending",
          recurring: form.recurring || "none",
        });
        setMsg("Reminder created ✓");
      }
      await loadDeps();
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    }
  }

  return (
    <div className="grid gap-4">
      <div className="card">
        <label className="block text-sm font-medium mb-1">Type</label>
        <select className="input" value={kind} onChange={(e) => setKind(e.target.value as Kind)}>
          <option value="cardholder">Cardholder</option>
          <option value="card">Card</option>
          <option value="benefit">Benefit</option>
          <option value="sub">Sign-up Bonus</option>
          <option value="reminder">Reminder</option>
        </select>
      </div>

      <div className="card grid gap-3">
        {kind === "cardholder" && (
          <>
            <Field label="Name"><input className="input" onChange={(e) => up("name", e.target.value)} /></Field>
            <Field label="Color"><input className="input" placeholder="#3b82f6" onChange={(e) => up("color_tag", e.target.value)} /></Field>
          </>
        )}

        {kind === "card" && (
          <>
            <Field label="Preset (optional)">
              <select className="input" onChange={(e) => applyPreset(e.target.value)}>
                <option value="">— None —</option>
                {presets.map((p) => (
                  <option key={`${p.issuer}::${p.name}`} value={`${p.issuer}::${p.name}`}>
                    {p.issuer} — {p.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Cardholder">
              <select className="input" onChange={(e) => up("cardholder_id", e.target.value)}>
                <option value="">— Select —</option>
                {holders.map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
              </select>
            </Field>
            <Field label="Issuer">
              <select className="input" value={form.issuer || ""} onChange={(e) => up("issuer", e.target.value)}>
                <option value="">— Select —</option>
                <option>Chase</option><option>Amex</option><option>Other</option>
              </select>
            </Field>
            <Field label="Name"><input className="input" value={form.name || ""} onChange={(e) => up("name", e.target.value)} /></Field>
            <Field label="Annual fee"><input type="number" className="input" value={form.annual_fee ?? ""} onChange={(e) => up("annual_fee", e.target.value)} /></Field>
            <Field label="Opened date"><input type="date" className="input" onChange={(e) => up("opened_date", e.target.value)} /></Field>
            <Field label="Next fee date"><input type="date" className="input" onChange={(e) => up("next_fee_date", e.target.value)} /></Field>
            <Field label="Can close after date"><input type="date" className="input" onChange={(e) => up("can_close_after_date", e.target.value)} /></Field>
            <Field label="Notes"><textarea className="input" rows={2} onChange={(e) => up("notes", e.target.value)} /></Field>
            {form._preset_benefits && (
              <div className="text-xs text-slate-500">
                Will auto-create {form._preset_benefits.length} benefits from preset.
              </div>
            )}
          </>
        )}

        {kind === "benefit" && (
          <>
            <Field label="Card">
              <select className="input" onChange={(e) => up("card_id", e.target.value)}>
                <option value="">— Select —</option>
                {cards.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
            <Field label="Name"><input className="input" onChange={(e) => up("name", e.target.value)} /></Field>
            <Field label="Amount"><input type="number" className="input" onChange={(e) => up("amount", e.target.value)} /></Field>
            <Field label="Frequency">
              <select className="input" onChange={(e) => up("frequency", e.target.value)}>
                <option value="monthly">monthly</option>
                <option value="quarterly">quarterly</option>
                <option value="yearly">yearly</option>
              </select>
            </Field>
            <Field label="Cycle type">
              <select className="input" onChange={(e) => up("cycle_type", e.target.value)}>
                <option value="statement_month">statement_month</option>
                <option value="calendar_year">calendar_year</option>
                <option value="anniversary_year">anniversary_year</option>
              </select>
            </Field>
            <Field label="Category">
              <select className="input" onChange={(e) => up("category", e.target.value)}>
                <option value="credit">credit</option>
                <option value="lounge">lounge</option>
                <option value="points">points</option>
                <option value="experience">experience</option>
              </select>
            </Field>
          </>
        )}

        {kind === "sub" && (
          <>
            <Field label="Card">
              <select className="input" onChange={(e) => up("card_id", e.target.value)}>
                <option value="">— Select —</option>
                {cards.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
            <Field label="Required spend"><input type="number" className="input" onChange={(e) => up("required_spend", e.target.value)} /></Field>
            <Field label="Current spend"><input type="number" className="input" onChange={(e) => up("current_spend", e.target.value)} /></Field>
            <Field label="Deadline"><input type="date" className="input" onChange={(e) => up("deadline_date", e.target.value)} /></Field>
            <Field label="Reward description"><input className="input" onChange={(e) => up("reward_description", e.target.value)} /></Field>
          </>
        )}

        {kind === "reminder" && (
          <>
            <Field label="Card (optional)">
              <select className="input" onChange={(e) => up("card_id", e.target.value)}>
                <option value="">— None —</option>
                {cards.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </Field>
            <Field label="Title"><input className="input" onChange={(e) => up("title", e.target.value)} /></Field>
            <Field label="Due date"><input type="date" className="input" onChange={(e) => up("due_date", e.target.value)} /></Field>
            <Field label="Recurring">
              <select className="input" onChange={(e) => up("recurring", e.target.value)}>
                <option value="none">none</option>
                <option value="yearly">yearly</option>
                <option value="monthly">monthly</option>
              </select>
            </Field>
          </>
        )}

        <button className="btn btn-primary" onClick={submit}>Submit</button>
        {msg && <div className="text-sm">{msg}</div>}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="block text-sm font-medium mb-1">{label}</span>
      {children}
    </label>
  );
}
