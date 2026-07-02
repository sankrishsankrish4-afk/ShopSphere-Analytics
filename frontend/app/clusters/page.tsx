import ClusterView from "@/components/ClusterView";

export default function ClustersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Customer Personas</h1>
        <p className="mt-2 text-slate-600">K-Means segments customers by frequency, spend, basket size, and category diversity for personalized rules.</p>
      </div>
      <ClusterView />
    </div>
  );
}
