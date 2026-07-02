"use client";

import { useEffect, useState } from "react";
import { Cluster, getClusters } from "@/lib/api";

export default function ClusterView() {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  useEffect(() => {
    getClusters().then(setClusters).catch(() => setClusters([]));
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {clusters.length ? clusters.map((cluster) => (
        <article key={cluster.persona_name} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">Persona</p>
          <h2 className="mt-1 text-xl font-semibold">{cluster.persona_name}</h2>
          <p className="mt-3 text-3xl font-semibold text-accent">{cluster.customer_count}</p>
          <p className="text-sm text-slate-500">customers</p>
          <dl className="mt-4 space-y-2 text-sm">
            {Object.entries(cluster.traits).slice(0, 4).map(([key, value]) => (
              <div key={key} className="flex justify-between gap-3"><dt className="text-slate-500">{key.replaceAll("_", " ")}</dt><dd className="font-medium">{value}</dd></div>
            ))}
          </dl>
        </article>
      )) : <p className="text-slate-500">No clusters found. Run the seed script first.</p>}
    </div>
  );
}
