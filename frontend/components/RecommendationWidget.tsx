"use client";

import { useEffect, useState } from "react";
import { getRecommendations, Recommendation } from "@/lib/api";

const demoProducts = [
  { id: 1, name: "Smartphone" }, { id: 2, name: "Phone Case" }, { id: 21, name: "Bread" }, { id: 22, name: "Butter" },
  { id: 79, name: "Shampoo" }, { id: 80, name: "Conditioner" }, { id: 123, name: "Notebook" }, { id: 124, name: "Gel Pens" }
];

export default function RecommendationWidget() {
  const [cart, setCart] = useState<number[]>([21]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!cart.length) {
      setRecommendations([]);
      return;
    }
    setLoading(true);
    const timeout = window.setTimeout(() => {
      getRecommendations(cart, 1).then(setRecommendations).catch(() => setRecommendations([])).finally(() => setLoading(false));
    }, 250);
    return () => window.clearTimeout(timeout);
  }, [cart]);

  const addProduct = (value: string) => {
    const id = Number(value);
    if (id && !cart.includes(id)) setCart((current) => [...current, id]);
  };

  return (
    <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Build a demo cart</h2>
        <select onChange={(event) => addProduct(event.target.value)} defaultValue="" className="mt-4 w-full rounded-xl border border-slate-200 px-3 py-3">
          <option value="" disabled>Add product</option>
          {demoProducts.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}
        </select>
        <div className="mt-4 flex flex-wrap gap-2">
          {cart.map((id) => (
            <button key={id} onClick={() => setCart(cart.filter((item) => item !== id))} className="rounded-full bg-slate-100 px-3 py-1.5 text-sm hover:bg-rose-50 hover:text-rose-700">
              {demoProducts.find((product) => product.id === id)?.name ?? id} x
            </button>
          ))}
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Recommended complements</h2>
        <div className="mt-4 space-y-3">
          {loading ? <div className="h-24 animate-pulse rounded-xl bg-slate-100" /> : recommendations.length ? recommendations.map((item) => (
            <article key={item.product_id} className="rounded-xl border border-slate-100 p-4">
              <div className="flex items-center justify-between gap-4"><h3 className="font-semibold">{item.name}</h3><span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">lift {item.lift.toFixed(2)}</span></div>
              <p className="mt-2 text-sm text-slate-600">{item.reason}</p>
            </article>
          )) : <p className="text-sm text-slate-500">No matching rule yet. Try Bread, Shampoo, or Smartphone after seeding.</p>}
        </div>
      </div>
    </section>
  );
}
