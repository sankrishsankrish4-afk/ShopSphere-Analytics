from __future__ import annotations

import time

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

from app.ml._common import format_mlxtend_rules, to_one_hot


def run_apriori(transactions_df: pd.DataFrame, min_support: float = 0.01, min_confidence: float = 0.2) -> pd.DataFrame:
    """Mine association rules with Apriori candidate generation."""
    one_hot = to_one_hot(transactions_df)
    frequent = apriori(one_hot, min_support=min_support, use_colnames=True)
    if frequent.empty:
        return format_mlxtend_rules(pd.DataFrame())
    try:
        rules = association_rules(frequent, metric="confidence", min_threshold=min_confidence)
    except TypeError:
        rules = association_rules(frequent, num_itemsets=len(one_hot), metric="confidence", min_threshold=min_confidence)
    return format_mlxtend_rules(rules)


def benchmark_apriori(transactions_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    started = time.perf_counter()
    rules = run_apriori(transactions_df)
    return rules, time.perf_counter() - started
