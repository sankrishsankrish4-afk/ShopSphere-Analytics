from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal, create_tables  # noqa: E402
from app.models import AssociationRule, Customer, CustomerCluster, Product, Transaction, TransactionItem  # noqa: E402


class ShopSphereETL:
    """Extract, transform, and load raw POS CSV files into normalized SQL tables."""

    def __init__(self, raw_dir: Path | None = None) -> None:
        self.raw_dir = raw_dir or Path(__file__).resolve().parent / "raw"
        self.frames: dict[str, pd.DataFrame] = {}
        self.summary = {"processed": 0, "rejected": 0}

    def extract(self) -> dict[str, pd.DataFrame]:
        print("[ETL] Extract: reading raw CSV files.")
        self.frames = {
            "products": pd.read_csv(self.raw_dir / "products.csv"),
            "customers": pd.read_csv(self.raw_dir / "customers.csv"),
            "transactions": pd.read_csv(self.raw_dir / "transactions.csv"),
        }
        return self.frames

    def transform(self) -> dict[str, pd.DataFrame]:
        print("[ETL] Transform: cleaning duplicates, nulls, and broken references.")
        products = self.frames["products"].drop_duplicates("product_id").dropna()
        customers = self.frames["customers"].drop_duplicates("customer_id").dropna()
        transactions = self.frames["transactions"].drop_duplicates(["transaction_id", "product_id"]).dropna()

        valid_products = set(products["product_id"])
        valid_customers = set(customers["customer_id"])
        before = len(transactions)
        transactions = transactions[
            transactions["product_id"].isin(valid_products) & transactions["customer_id"].isin(valid_customers)
        ].copy()
        self.summary["rejected"] += before - len(transactions)

        customers["signup_date"] = pd.to_datetime(customers["signup_date"])
        transactions["timestamp"] = pd.to_datetime(transactions["timestamp"])
        self.frames = {"products": products, "customers": customers, "transactions": transactions}
        self.summary["processed"] = len(products) + len(customers) + len(transactions)
        return self.frames

    def load(self) -> None:
        print("[ETL] Load: replacing database rows in dependency-safe order.")
        create_tables()
        products = self.frames["products"]
        customers = self.frames["customers"]
        tx_items = self.frames["transactions"]
        tx = tx_items[["transaction_id", "customer_id", "timestamp"]].drop_duplicates("transaction_id")

        with SessionLocal() as db:
            for model in (AssociationRule, CustomerCluster, TransactionItem, Transaction, Product, Customer):
                db.query(model).delete()
            db.bulk_insert_mappings(Product, products.to_dict("records"))
            db.bulk_insert_mappings(Customer, customers.to_dict("records"))
            db.bulk_insert_mappings(Transaction, tx.to_dict("records"))
            db.bulk_insert_mappings(
                TransactionItem,
                tx_items[["transaction_id", "product_id"]].to_dict("records"),
            )
            db.commit()

    def run(self) -> None:
        started = time.perf_counter()
        self.extract()
        self.transform()
        self.load()
        elapsed = time.perf_counter() - started
        print(
            f"[ETL] Complete: processed={self.summary['processed']:,}, "
            f"rejected={self.summary['rejected']:,}, seconds={elapsed:.2f}"
        )


if __name__ == "__main__":
    ShopSphereETL().run()
