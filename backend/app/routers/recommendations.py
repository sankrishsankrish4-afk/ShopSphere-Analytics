from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import CartRequest, RecommendationResponse
from app.services.recommendation_service import get_recommendations


router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=list[RecommendationResponse], status_code=status.HTTP_200_OK)
def recommend(request: CartRequest, db: Session = Depends(get_db)) -> list[dict]:
    """Return real-time complementary products for the supplied shopping cart."""
    try:
        return get_recommendations(request.cart_items, request.customer_id, db=db)
    except Exception as exc:  # pragma: no cover - keeps API errors clean in production.
        raise HTTPException(status_code=500, detail="Could not generate recommendations") from exc
