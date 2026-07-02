from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AssociationRule, Product, Transaction, TransactionItem
from app.schemas import AnalyticsSummaryResponse


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def summary(db: Session = Depends(get_db)) -> AnalyticsSummaryResponse:
    """Return high-level KPIs for the dashboard landing page."""
    try:
        top_categories = [
            category
            for category, _ in db.query(Product.category, func.count(TransactionItem.id))
            .join(TransactionItem, Product.product_id == TransactionItem.product_id)
            .group_by(Product.category)
            .order_by(func.count(TransactionItem.id).desc())
            .limit(5)
            .all()
        ]
        return AnalyticsSummaryResponse(
            total_transactions=db.query(Transaction).count(),
            total_products=db.query(Product).count(),
            total_rules=db.query(AssociationRule).count(),
            avg_lift=round(db.query(func.avg(AssociationRule.lift)).scalar() or 0, 3),
            top_categories=top_categories,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not load analytics summary") from exc


@router.get("/lift-matrix")
def lift_matrix(db: Session = Depends(get_db)) -> dict:
    """Return category-to-category average lift values for a heatmap."""
    try:
        product_categories = {product.product_id: product.category for product in db.query(Product).all()}
        buckets: dict[tuple[str, str], list[float]] = defaultdict(list)
        categories = sorted(set(product_categories.values()))
        for rule in db.query(AssociationRule).filter(AssociationRule.segment.is_(None)).all():
            antecedent_categories = {product_categories.get(pid) for pid in rule.antecedent if pid in product_categories}
            consequent_categories = {product_categories.get(pid) for pid in rule.consequent if pid in product_categories}
            for left in antecedent_categories:
                for right in consequent_categories:
                    if left and right:
                        buckets[(left, right)].append(rule.lift)
        matrix = [
            [round(sum(buckets[(left, right)]) / len(buckets[(left, right)]), 3) if buckets[(left, right)] else 0 for right in categories]
            for left in categories
        ]
        return {"categories": categories, "matrix": matrix}
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not load lift matrix") from exc
