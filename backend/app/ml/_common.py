from __future__ import annotations

import pandas as pd
from mlxtend.preprocessing import TransactionEncoder


def normalize_transactions(transactions_df: pd.DataFrame) -> list[list[int]]:
    if "product_ids" in transactions_df.columns:
        return [list(map(int, values)) for values in transactions_df["product_ids"]]
    if {"transaction_id", "product_id"}.issubset(transactions_df.columns):
        return [list(map(int, values)) for values in transactions_df.groupby("transaction_id")["product_id"].apply(list)]
    raise ValueError("transactions_df must contain product_ids or transaction_id/product_id columns")


def to_one_hot(transactions_df: pd.DataFrame) -> pd.DataFrame:
    transactions = normalize_transactions(transactions_df)
    encoder = TransactionEncoder()
    encoded = encoder.fit(transactions).transform(transactions)
    return pd.DataFrame(encoded, columns=encoder.columns_)


def format_mlxtend_rules(rules: pd.DataFrame) -> pd.DataFrame:
    if rules.empty:
        return pd.DataFrame(columns=["antecedent", "consequent", "support", "confidence", "lift"])
    result = rules[["antecedents", "consequents", "support", "confidence", "lift"]].copy()
    result["antecedent"] = result["antecedents"].apply(lambda x: sorted(int(item) for item in x))
    result["consequent"] = result["consequents"].apply(lambda x: sorted(int(item) for item in x))
    return result[["antecedent", "consequent", "support", "confidence", "lift"]].sort_values(
        ["lift", "confidence"], ascending=False
    )
