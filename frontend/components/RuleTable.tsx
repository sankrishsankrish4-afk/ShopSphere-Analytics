"use client";

import { useEffect, useState } from "react";
import { getRules, Rule } from "@/lib/api";

function liftClass(value: number) {
  if (value > 1.5) return "bg-emerald-50 text-emerald-700";
  if (value < 0.8) return "bg-rose-50 text-rose-700";
  return "bg-slate-100 text-slate-700";
}

export default function RuleTable() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [algorithm, setAlgorithm] = useState("");
  const [minLift, setMinLift] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getRules({ algorithm: algorithm || undefined, min_lift: minLift, page_size: 50 })
      .then((data) => setRules(data.rules))
      .catch(() => setRules([]))
      .finally(() => setLoading(false));
  }, [algorithm, minLift]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Association Rules</h2>
          <p className="text-sm text-slate-500">Lift tooltip: greater than 1 means items co-occur more often than chance.</p>
        </div>
        <div className="flex gap-3">
          <select value={algorithm} onChange={(event) => setAlgorithm(event.target.value)} className="rounded-xl border border-slate-200 px-3 py-2 text-sm">
            <option value="">All algorithms</option>
            <option value="apriori">Apriori</option>
            <option value="fpgrowth">FP-Growth</option>
            <option value="eclat">ECLAT</option>
          </select>
          <input type="number" min="0" step="0.1" value={minLift} onChange={(event) => setMinLift(Number(event.target.value))} className="w-28 rounded-xl border border-slate-200 px-3 py-2 text-sm" />
        </div>
      </div>
      <div className="mt-5 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-slate-200 text-slate-500">
            <tr>
              <th className="py-3">Antecedent</th><th>Consequent</th><th>Support</th><th>Confidence</th><th>Lift</th><th>Algorithm</th><th>Segment</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading ? (
              <tr><td colSpan={7} className="py-6 text-center text-slate-500">Loading rules...</td></tr>
            ) : rules.length ? rules.map((rule) => (
              <tr key={rule.id} className="align-top">
                <td className="py-3">{rule.antecedent.join(", ")}</td>
                <td>{rule.consequent.join(", ")}</td>
                <td>{rule.support.toFixed(3)}</td>
                <td>{rule.confidence.toFixed(3)}</td>
                <td><span title="Lift > 1 positive, = 1 independent, < 1 negative" className={`rounded-full px-2 py-1 text-xs font-semibold ${liftClass(rule.lift)}`}>{rule.lift.toFixed(2)}</span></td>
                <td>{rule.algorithm}</td>
                <td>{rule.segment ?? "Global"}</td>
              </tr>
            )) : (
              <tr><td colSpan={7} className="py-6 text-center text-slate-500">No matching rules.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
