from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CustomerCluster
from app.schemas import ClusterResponse


router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("")
def list_clusters(db: Session = Depends(get_db)) -> list[dict]:
    """List customer personas with counts and average behavioral traits."""
    try:
        clusters = db.query(CustomerCluster).all()
        grouped: dict[str, list[CustomerCluster]] = {}
        for cluster in clusters:
            grouped.setdefault(cluster.persona_name, []).append(cluster)
        response = []
        for persona, rows in grouped.items():
            keys = rows[0].cluster_features.keys() if rows else []
            traits = {key: round(sum(row.cluster_features.get(key, 0) for row in rows) / len(rows), 2) for key in keys}
            response.append({"persona_name": persona, "customer_count": len(rows), "traits": traits})
        return sorted(response, key=lambda item: item["persona_name"])
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not load clusters") from exc


@router.get("/{customer_id}", response_model=ClusterResponse)
def get_cluster(customer_id: int, db: Session = Depends(get_db)) -> ClusterResponse:
    """Return one customer's assigned K-Means persona."""
    cluster = db.get(CustomerCluster, customer_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Customer cluster not found")
    return ClusterResponse(
        customer_id=cluster.customer_id,
        cluster_label=cluster.cluster_label,
        persona_name=cluster.persona_name,
        features=cluster.cluster_features,
    )
