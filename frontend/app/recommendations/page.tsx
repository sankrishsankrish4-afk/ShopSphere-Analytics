import RecommendationWidget from "@/components/RecommendationWidget";

export default function RecommendationsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Rule Engine Demo Cart</h1>
        <p className="mt-2 max-w-3xl text-slate-600">Pick products and watch the API return complementary items ranked by lift and confidence.</p>
      </div>
      <RecommendationWidget />
    </div>
  );
}
