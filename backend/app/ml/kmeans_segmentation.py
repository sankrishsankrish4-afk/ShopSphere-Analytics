from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


ARTIFACT_DIR = Path(__file__).resolve().parents[2] / "artifacts"
FEATURE_COLUMNS = ["total_transactions", "avg_basket_size", "avg_spend", "purchase_frequency", "category_diversity"]


def build_customer_features(transactions_df: pd.DataFrame, customers_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    merged = transactions_df.merge(products_df[["product_id", "category", "price"]], on="product_id", how="left")
    baskets = merged.groupby(["customer_id", "transaction_id"]).agg(
        basket_size=("product_id", "nunique"), spend=("price", "sum")
    ).reset_index()
    customer_features = baskets.groupby("customer_id").agg(
        total_transactions=("transaction_id", "nunique"), avg_basket_size=("basket_size", "mean"), avg_spend=("spend", "mean")
    ).reset_index()
    diversity = merged.groupby("customer_id")["category"].nunique().rename("category_diversity").reset_index()
    customer_features = customer_features.merge(diversity, on="customer_id", how="left")
    customers = customers_df.copy()
    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    weeks = ((pd.Timestamp.now() - customers["signup_date"]).dt.days.clip(lower=7) / 7).rename("weeks")
    customers = customers.assign(weeks=weeks)
    customer_features = customers[["customer_id", "weeks"]].merge(customer_features, on="customer_id", how="left").fillna(0)
    customer_features["purchase_frequency"] = customer_features["total_transactions"] / customer_features["weeks"].replace(0, 1)
    return customer_features[["customer_id", *FEATURE_COLUMNS]]


def _assign_personas(profile: pd.DataFrame) -> dict[int, str]:
    """Assign distinct portfolio-friendly names by ranking cluster centroids."""
    remaining = set(profile["cluster_label"].astype(int))
    persona_map: dict[int, str] = {}

    premium = int(profile.sort_values(["avg_spend", "purchase_frequency"], ascending=False).iloc[0]["cluster_label"])
    persona_map[premium] = "Premium Shopper"
    remaining.discard(premium)

    if remaining:
        bulk = int(profile[profile["cluster_label"].isin(remaining)].sort_values("avg_basket_size", ascending=False).iloc[0]["cluster_label"])
        persona_map[bulk] = "Bulk Buyer"
        remaining.discard(bulk)

    if remaining:
        occasional = int(profile[profile["cluster_label"].isin(remaining)].sort_values("purchase_frequency").iloc[0]["cluster_label"])
        persona_map[occasional] = "Occasional Buyer"
        remaining.discard(occasional)

    for label in remaining:
        persona_map[label] = "Budget Shopper"
    return persona_map


def evaluate_k(customer_features_df: pd.DataFrame, min_k: int = 2, max_k: int = 8) -> pd.DataFrame:
    X = customer_features_df[FEATURE_COLUMNS]
    scaled = StandardScaler().fit_transform(X)
    rows = []
    for k in range(min_k, min(max_k, len(customer_features_df) - 1) + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(scaled)
        rows.append({"k": k, "inertia": model.inertia_, "silhouette": silhouette_score(scaled, labels)})
    return pd.DataFrame(rows)


def segment_customers(customer_features_df: pd.DataFrame, k: int = 4) -> pd.DataFrame:
    if len(customer_features_df) < k:
        raise ValueError("customer_features_df must contain at least k customers")
    X = customer_features_df[FEATURE_COLUMNS]
    # K-Means is distance-based, so large-scale columns like spend would dominate unless standardized.
    scaler = StandardScaler()
    scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled)
    result = customer_features_df.copy()
    result["cluster_label"] = labels

    profile = result.groupby("cluster_label")[FEATURE_COLUMNS].mean().reset_index()
    persona_map = _assign_personas(profile)
    result["persona_name"] = result["cluster_label"].map(persona_map)
    result["features"] = result[FEATURE_COLUMNS].to_dict("records")

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, ARTIFACT_DIR / "customer_scaler.joblib")
    joblib.dump(kmeans, ARTIFACT_DIR / "customer_kmeans.joblib")
    return result[["customer_id", "cluster_label", "persona_name", "features"]]
