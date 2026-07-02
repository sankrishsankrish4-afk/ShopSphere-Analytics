import pandas as pd

from app.ml.kmeans_segmentation import segment_customers


def _features():
    return pd.DataFrame(
        [
            {"customer_id": 1, "total_transactions": 20, "avg_basket_size": 6, "avg_spend": 40, "purchase_frequency": 2.0, "category_diversity": 4},
            {"customer_id": 2, "total_transactions": 18, "avg_basket_size": 5, "avg_spend": 42, "purchase_frequency": 1.8, "category_diversity": 4},
            {"customer_id": 3, "total_transactions": 2, "avg_basket_size": 1, "avg_spend": 12, "purchase_frequency": 0.1, "category_diversity": 1},
            {"customer_id": 4, "total_transactions": 3, "avg_basket_size": 1, "avg_spend": 10, "purchase_frequency": 0.2, "category_diversity": 1},
            {"customer_id": 5, "total_transactions": 10, "avg_basket_size": 2, "avg_spend": 400, "purchase_frequency": 1.1, "category_diversity": 3},
            {"customer_id": 6, "total_transactions": 11, "avg_basket_size": 2, "avg_spend": 380, "purchase_frequency": 1.2, "category_diversity": 3},
        ]
    )


def test_segment_customers_returns_k_clusters():
    result = segment_customers(_features(), k=3)
    assert result["cluster_label"].nunique() == 3


def test_segment_customers_is_stable_with_fixed_random_state():
    first = segment_customers(_features(), k=3)
    second = segment_customers(_features(), k=3)
    assert first["cluster_label"].tolist() == second["cluster_label"].tolist()
