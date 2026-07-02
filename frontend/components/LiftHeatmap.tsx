"use client";

import { useEffect, useState } from "react";
import { getLiftMatrix, LiftMatrix } from "@/lib/api";

function cellColor(value: number) {
  if (value === 0) return "bg-slate-50";
  if (value > 2) return "bg-emerald-600 text-white";
  if (value > 1.2) return "bg-emerald-200 text-emerald-950";
  return "bg-slate-200 text-slate-700";
}

export default function LiftHeatmap() {
  const [data, setData] = useState<LiftMatrix | null>(null);
  useEffect(() => {
    getLiftMatrix().then(setData).catch(() => setData(null));
  }, []);

  if (!data) return <div className="rounded-2xl border border-slate-200 bg-white p-6 text-slate-500">Loading lift matrix...</div>;

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">Category Lift Heatmap</h2>
      <div className="mt-5 overflow-auto">
        <div className="grid min-w-[760px]" style={{ gridTemplateColumns: `140px repeat(${data.categories.length}, minmax(70px, 1fr))` }}>
          <div />
          {data.categories.map((category) => <div key={category} className="p-2 text-xs font-semibold text-slate-500">{category}</div>)}
          {data.categories.map((left, rowIndex) => (
            <div key={left} className="contents">
              <div className="p-2 text-xs font-semibold text-slate-500">{left}</div>
              {data.matrix[rowIndex].map((value, colIndex) => (
                <div key={`${left}-${data.categories[colIndex]}`} className={`m-1 rounded-lg p-3 text-center text-xs ${cellColor(value)}`}>{value ? value.toFixed(2) : "-"}</div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
