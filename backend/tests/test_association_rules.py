import pandas as pd

from app.ml.apriori_engine import run_apriori
from app.ml.eclat_engine import run_eclat
from app.ml.fpgrowth_engine import run_fpgrowth
from app.services.metrics import confidence, lift, support


def test_support_confidence_lift_math():
    transactions = [{1, 2}, {1, 2}, {1, 3}, {2, 3}]
    assert support({1, 2}, transactions) == 0.5
    assert confidence({1}, {2}, transactions) == 2 / 3
    assert round(lift({1}, {2}, transactions), 4) == round((2 / 3) / (3 / 4), 4)


def test_algorithms_agree_on_tiny_dataset():
    df = pd.DataFrame(
        {"transaction_id": [1, 2, 3, 4], "product_ids": [[1, 2], [1, 2], [1, 3], [2, 3]]}
    )
    apriori_rules = run_apriori(df, min_support=0.5, min_confidence=0.5)
    fpgrowth_rules = run_fpgrowth(df, min_support=0.5, min_confidence=0.5)
    eclat_rules = run_eclat(df, min_support=0.5, min_confidence=0.5)

    def pairs(rules):
        return {(tuple(row["antecedent"]), tuple(row["consequent"])) for _, row in rules.iterrows()}

    assert pairs(apriori_rules) == pairs(fpgrowth_rules) == pairs(eclat_rules)
