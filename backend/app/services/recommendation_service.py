from __future__ import annotations

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AssociationRule, CustomerCluster, Product


def _rank_rules(rules: list[AssociationRule], cart: set[int]) -> list[AssociationRule]:
    return sorted(
        [rule for rule in rules if set(rule.antecedent).issubset(cart)],
        key=lambda rule: (rule.lift, rule.confidence),
        reverse=True,
    )


def get_recommendations(
    cart_items: list[int], customer_id: int | None = None, top_n: int = 5, db: Session | None = None
) -> list[dict]:
    """Return complementary products for a live cart using segment rules first, then global rules."""
    owns_session = db is None
    db = db or SessionLocal()
    try:
        cart = set(map(int, cart_items))
        if not cart:
            return []

        segment = None
        if customer_id is not None:
            cluster = db.get(CustomerCluster, customer_id)
            segment = cluster.persona_name if cluster else None

        scoped_rules: list[AssociationRule] = []
        if segment:
            scoped_rules = db.query(AssociationRule).filter(AssociationRule.segment == segment).all()
        ranked = _rank_rules(scoped_rules, cart)
        if not ranked:
            global_rules = db.query(AssociationRule).filter(AssociationRule.segment.is_(None)).all()
            ranked = _rank_rules(global_rules, cart)

        product_ids: list[int] = []
        best_metrics: dict[int, tuple[float, float, list[int]]] = {}
        for rule in ranked:
            for product_id in rule.consequent:
                if product_id in cart:
                    continue
                current = best_metrics.get(product_id)
                if current is None or (rule.lift, rule.confidence) > (current[0], current[1]):
                    best_metrics[product_id] = (rule.lift, rule.confidence, rule.antecedent)
                    product_ids.append(product_id)

        if not product_ids:
            return []
        products = {product.product_id: product for product in db.query(Product).filter(Product.product_id.in_(product_ids)).all()}
        recommendations = []
        for product_id in product_ids:
            if product_id not in products or len(recommendations) >= top_n:
                continue
            lift_value, confidence_value, antecedent = best_metrics[product_id]
            anchor = ", ".join(str(item) for item in antecedent)
            recommendations.append(
                {
                    "product_id": product_id,
                    "name": products[product_id].name,
                    "confidence": round(confidence_value, 4),
                    "lift": round(lift_value, 4),
                    "reason": f"Frequently bought with {anchor} (lift {lift_value:.2f})",
                }
            )
        return recommendations
    finally:
        if owns_session:
            db.close()
