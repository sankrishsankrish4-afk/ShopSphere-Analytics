from __future__ import annotations

import time

import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

from app.ml._common import format_mlxtend_rules, to_one_hot


def run_fpgrowth(transactions_df: pd.DataFrame, min_support: float = 0.01, min_confidence: float = 0.2) -> pd.DataFrame:
    """Mine rules with FP-Growth, which avoids Apriori candidate generation by using an FP-tree."""
    one_hot = to_one_hot(transactions_df)
    frequent = fpgrowth(one_hot, min_support=min_support, use_colnames=True)
    if frequent.empty:
        return format_mlxtend_rules(pd.DataFrame())
    try:
        rules = association_rules(frequent, metric="confidence", min_threshold=min_confidence)
    except TypeError:
        rules = association_rules(frequent, num_itemsets=len(one_hot), metric="confidence", min_threshold=min_confidence)
    return format_mlxtend_rules(rules)


def benchmark_fpgrowth(transactions_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    started = time.perf_counter()
    rules = run_fpgrowth(transactions_df)
    return rules, time.perf_counter() - started
