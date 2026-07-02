import LiftHeatmap from "@/components/LiftHeatmap";
import RuleTable from "@/components/RuleTable";

export default function RulesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Association Matrix Dashboard</h1>
        <p className="mt-2 max-w-3xl text-slate-600">Explore product affinities, confidence scores, and lift correlations mined from POS transactions.</p>
      </div>
      <LiftHeatmap />
      <RuleTable />
    </div>
  );
}
