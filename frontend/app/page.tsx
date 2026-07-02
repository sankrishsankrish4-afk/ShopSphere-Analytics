import { getAnalyticsSummary } from "@/lib/api";

function formatNumber(value: number) {
  return new Intl.NumberFormat("en-US").format(value);
}

export default async function HomePage() {
  let summary;
  try {
    summary = await getAnalyticsSummary();
  } catch {
    summary = null;
  }

  if (!summary) {
    return (
      <section className="rounded-3xl border border-dashed border-slate-300 bg-white p-10 text-center">
        <h1 className="text-3xl font-semibold">Association Matrix Dashboard</h1>
        <p className="mt-3 text-slate-600">Start the FastAPI backend and seed the database to load dashboard metrics.</p>
      </section>
    );
  }

  const cards = [
    ["Transactions", formatNumber(summary.total_transactions)],
    ["Products", formatNumber(summary.total_products)],
    ["Rules mined", formatNumber(summary.total_rules)],
    ["Average lift", summary.avg_lift.toFixed(2)]
  ];

  return (
    <div className="space-y-8">
      <section className="rounded-3xl bg-gradient-to-br from-ink to-slate-700 p-8 text-white shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.25em] text-blue-100">Market Basket Intelligence</p>
        <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight">Find product affinities, rank upsell rules, and personalize recommendations by customer persona.</h1>
      </section>
      <section className="grid gap-4 md:grid-cols-4">
        {cards.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <p className="text-sm text-slate-500">{label}</p>
            <p className="mt-2 text-3xl font-semibold text-ink">{value}</p>
          </div>
        ))}
      </section>
      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Top Categories</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          {summary.top_categories.length ? summary.top_categories.map((category) => (
            <span key={category} className="rounded-full bg-blue-50 px-4 py-2 text-sm font-medium text-accent">{category}</span>
          )) : <p className="text-sm text-slate-500">No category activity yet.</p>}
        </div>
      </section>
    </div>
  );
}
