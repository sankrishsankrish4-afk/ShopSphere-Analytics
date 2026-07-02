import os
import sys
from datetime import datetime
from pathlib import Path

import pytest


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import AssociationRule, Customer, CustomerCluster, Product, Transaction, TransactionItem  # noqa: E402


@pytest.fixture(autouse=True)
def seed_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all(
            [
                Product(product_id=1, name="Bread", category="Groceries", price=3),
                Product(product_id=2, name="Butter", category="Groceries", price=4),
                Product(product_id=3, name="Milk", category="Groceries", price=3),
                Customer(customer_id=1, signup_date=datetime(2024, 1, 1), segment_hint="Budget Shopper"),
                Transaction(transaction_id=1, customer_id=1, timestamp=datetime(2024, 2, 1)),
                Transaction(transaction_id=2, customer_id=1, timestamp=datetime(2024, 2, 2)),
                TransactionItem(transaction_id=1, product_id=1),
                TransactionItem(transaction_id=1, product_id=2),
                TransactionItem(transaction_id=2, product_id=1),
                TransactionItem(transaction_id=2, product_id=3),
                AssociationRule(
                    antecedent=[1], consequent=[2], support=0.5, confidence=0.5, lift=1.0, algorithm="apriori"
                ),
                CustomerCluster(
                    customer_id=1,
                    cluster_label=0,
                    persona_name="Budget Shopper",
                    cluster_features={"avg_basket_size": 2, "avg_spend": 6},
                ),
            ]
        )
        db.commit()
    yield
