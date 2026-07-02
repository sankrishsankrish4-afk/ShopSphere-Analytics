from __future__ import annotations

import itertools
import time
from collections import defaultdict

import pandas as pd

from app.ml._common import normalize_transactions


def _frequent_itemsets(transactions: list[list[int]], min_support: float, max_size: int = 3) -> dict[frozenset[int], float]:
    """
    ECLAT uses vertical item -> transaction-id sets. Apriori/FP-Growth scan horizontal
    baskets; ECLAT intersects TID sets, which makes support counting simple and fast.
    """
    tidsets: dict[int, set[int]] = defaultdict(set)
    for tid, basket in enumerate(transactions):
        for item in set(basket):
            tidsets[int(item)].add(tid)

    min_count = max(1, int(min_support * len(transactions)))
    frequent: dict[frozenset[int], float] = {}

    def recurse(prefix: tuple[int, ...], items: list[tuple[int, set[int]]]) -> None:
        for index, (item, tids) in enumerate(items):
            new_items = tuple(sorted(prefix + (item,)))
            support_count = len(tids)
            if support_count < min_count:
                continue
            itemset = frozenset(new_items)
            frequent[itemset] = support_count / len(transactions)
            if len(new_items) >= max_size:
                continue
            suffix = []
            for next_item, next_tids in items[index + 1 :]:
                intersection = tids & next_tids
                if len(intersection) >= min_count:
                    suffix.append((next_item, intersection))
            recurse(new_items, suffix)

    recurse(tuple(), sorted(tidsets.items()))
    return frequent


def run_eclat(transactions_df: pd.DataFrame, min_support: float = 0.01, min_confidence: float = 0.2) -> pd.DataFrame:
    transactions = normalize_transactions(transactions_df)
    if not transactions:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift"])
    frequent = _frequent_itemsets(transactions, min_support)
    rows = []
    for itemset, itemset_support in frequent.items():
        if len(itemset) < 2:
            continue
        for size in range(1, len(itemset)):
            for antecedent in itertools.combinations(sorted(itemset), size):
                antecedent_set = frozenset(antecedent)
                consequent_set = itemset - antecedent_set
                antecedent_support = frequent.get(antecedent_set, 0)
                consequent_support = frequent.get(consequent_set, 0)
                if not antecedent_support or not consequent_support:
                    continue
                confidence = itemset_support / antecedent_support
                if confidence < min_confidence:
                    continue
                rows.append(
                    {
                        "antecedent": sorted(antecedent_set),
                        "consequent": sorted(consequent_set),
                        "support": itemset_support,
                        "confidence": confidence,
                        "lift": confidence / consequent_support,
                    }
                )
    return pd.DataFrame(rows).sort_values(["lift", "confidence"], ascending=False) if rows else pd.DataFrame(
        columns=["antecedent", "consequent", "support", "confidence", "lift"]
    )


def benchmark_eclat(transactions_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    started = time.perf_counter()
    rules = run_eclat(transactions_df)
    return rules, time.perf_counter() - started


def benchmark_all(transactions_df: pd.DataFrame) -> pd.DataFrame:
    from app.ml.apriori_engine import benchmark_apriori
    from app.ml.fpgrowth_engine import benchmark_fpgrowth

    rows = []
    for name, func in [("apriori", benchmark_apriori), ("fpgrowth", benchmark_fpgrowth), ("eclat", benchmark_eclat)]:
        rules, seconds = func(transactions_df)
        rows.append({"algorithm": name, "rules": len(rules), "seconds": seconds})
    return pd.DataFrame(rows)
