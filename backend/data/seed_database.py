from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal  # noqa: E402
from app.ml.apriori_engine import run_apriori  # noqa: E402
from app.ml.eclat_engine import run_eclat  # noqa: E402
from app.ml.fpgrowth_engine import run_fpgrowth  # noqa: E402
from app.ml.kmeans_segmentation import build_customer_features, segment_customers  # noqa: E402
from app.models import AssociationRule, CustomerCluster  # noqa: E402
from data.etl_pipeline import ShopSphereETL  # noqa: E402
from data.generate_synthetic_data import main as generate_data  # noqa: E402


RAW_DIR = Path(__file__).resolve().parent / "raw"


def _load_raw() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(RAW_DIR / "products.csv"),
        pd.read_csv(RAW_DIR / "customers.csv"),
        pd.read_csv(RAW_DIR / "transactions.csv"),
    )


def _save_rules(rules: pd.DataFrame, algorithm: str, segment: str | None) -> int:
    if rules.empty:
        return 0
    payload = []
    for row in rules.head(500).to_dict("records"):
        payload.append(
            {
                "antecedent": [int(item) for item in row["antecedent"]],
                "consequent": [int(item) for item in row["consequent"]],
                "support": float(row["support"]),
                "confidence": float(row["confidence"]),
                "lift": float(row["lift"]),
                "algorithm": algorithm,
                "segment": segment,
            }
        )
    with SessionLocal() as db:
        db.bulk_insert_mappings(AssociationRule, payload)
        db.commit()
    return len(payload)


def main() -> None:
    started = time.perf_counter()
    print("1/5 Checking synthetic raw data")
    if not all((RAW_DIR / name).exists() for name in ["products.csv", "customers.csv", "transactions.csv"]):
        generate_data()

    print("2/5 Loading CSVs into the database")
    ShopSphereETL().run()
    products, customers, transactions = _load_raw()

    print("3/5 Segmenting customers with K-Means")
    features = build_customer_features(transactions, customers, products)
    clusters = segment_customers(features, k=4)
    with SessionLocal() as db:
        db.query(CustomerCluster).delete()
        db.bulk_insert_mappings(
            CustomerCluster,
            [
                {
                    "customer_id": int(row["customer_id"]),
                    "cluster_label": int(row["cluster_label"]),
                    "persona_name": row["persona_name"],
                    "cluster_features": row["features"],
                }
                for row in clusters.to_dict("records")
            ],
        )
        db.query(AssociationRule).delete()
        db.commit()
    print(f"Saved {len(clusters):,} customer cluster assignments")

    print("4/5 Mining global association rules")
    grouped = transactions.groupby("transaction_id")["product_id"].apply(list).reset_index(name="product_ids")
    algorithms = {"apriori": run_apriori, "fpgrowth": run_fpgrowth, "eclat": run_eclat}
    for name, func in algorithms.items():
        count = _save_rules(func(grouped, min_support=0.01, min_confidence=0.2), name, None)
        print(f"Saved {count:,} global {name} rules")

    print("5/5 Mining segment-specific FP-Growth rules")
    tx_segments = transactions.merge(clusters[["customer_id", "persona_name"]], on="customer_id", how="inner")
    for persona, segment_rows in tx_segments.groupby("persona_name"):
        segment_grouped = segment_rows.groupby("transaction_id")["product_id"].apply(list).reset_index(name="product_ids")
        count = _save_rules(run_fpgrowth(segment_grouped, min_support=0.02, min_confidence=0.2), "fpgrowth", persona)
        print(f"Saved {count:,} rules for {persona}")

    print(f"Seed complete in {time.perf_counter() - started:.2f}s")


if __name__ == "__main__":
    main()
