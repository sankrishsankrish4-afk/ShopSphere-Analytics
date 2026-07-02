from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AssociationRule
from app.schemas import RuleListResponse, RuleResponse


router = APIRouter(prefix="/rules", tags=["rules"])


@router.get("", response_model=RuleListResponse)
def list_rules(
    algorithm: str | None = Query(default=None),
    segment: str | None = Query(default=None),
    min_lift: float | None = Query(default=None, ge=0),
    min_confidence: float | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
) -> RuleListResponse:
    """Browse mined association rules with dashboard filters and pagination."""
    try:
        query = db.query(AssociationRule)
        if algorithm:
            query = query.filter(AssociationRule.algorithm == algorithm)
        if segment:
            query = query.filter(AssociationRule.segment == segment)
        if min_lift is not None:
            query = query.filter(AssociationRule.lift >= min_lift)
        if min_confidence is not None:
            query = query.filter(AssociationRule.confidence >= min_confidence)
        total = query.count()
        rules = query.order_by(AssociationRule.lift.desc(), AssociationRule.confidence.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return RuleListResponse(rules=[RuleResponse.model_validate(rule) for rule in rules], total=total)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not load rules") from exc
