from collections.abc import Iterable


TransactionSet = Iterable[Iterable[int]]


def _as_sets(transactions: TransactionSet) -> list[set[int]]:
    return [set(transaction) for transaction in transactions]


def support(itemset: Iterable[int], transactions: TransactionSet) -> float:
    """Support(A->B) = P(A intersect B): share of transactions containing the itemset."""
    itemset_values = set(itemset)
    transaction_sets = _as_sets(transactions)
    if not transaction_sets or not itemset_values:
        return 0.0
    return sum(itemset_values.issubset(transaction) for transaction in transaction_sets) / len(transaction_sets)


def confidence(antecedent: Iterable[int], consequent: Iterable[int], transactions: TransactionSet) -> float:
    """Confidence(A->B) = P(A intersect B) / P(A): likelihood B appears when A appears."""
    antecedent_set = set(antecedent)
    consequent_set = set(consequent)
    transaction_sets = _as_sets(transactions)
    antecedent_support = support(antecedent_set, transaction_sets)
    if antecedent_support == 0:
        return 0.0
    return support(antecedent_set | consequent_set, transaction_sets) / antecedent_support


def lift(antecedent: Iterable[int], consequent: Iterable[int], transactions: TransactionSet) -> float:
    """Lift(A->B) = P(A intersect B) / (P(A) x P(B)): strength versus random chance."""
    consequent_set = set(consequent)
    transaction_sets = _as_sets(transactions)
    consequent_support = support(consequent_set, transaction_sets)
    if consequent_support == 0:
        return 0.0
    return confidence(antecedent, consequent_set, transaction_sets) / consequent_support


def interpret_lift(lift_value: float) -> str:
    """Return a dashboard-friendly explanation of a lift score."""
    if lift_value > 1:
        return "Positive association: items are bought together more often than random chance."
    if lift_value == 1:
        return "Independent: items appear together about as often as random chance."
    return "Negative association: items are bought together less often than random chance."
