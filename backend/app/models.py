from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


JsonList = MutableList.as_mutable(JSON().with_variant(JSONB, "postgresql"))
JsonDict = MutableDict.as_mutable(JSON().with_variant(JSONB, "postgresql"))


class Product(Base):
    """Product catalog dimension used to translate mined item IDs into merchandise names."""

    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    items: Mapped[list["TransactionItem"]] = relationship(back_populates="product")


class Customer(Base):
    """Customer dimension; segment_hint biases synthetic behavior but is not used as ML truth."""

    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signup_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    segment_hint: Mapped[str] = mapped_column(String(80), nullable=False)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="customer")
    cluster: Mapped["CustomerCluster"] = relationship(back_populates="customer", uselist=False)


class Transaction(Base):
    """One checkout event from POS data; items are stored separately for long-format baskets."""

    __tablename__ = "transactions"

    __table_args__ = (UniqueConstraint("transaction_id", name="uq_transactions_transaction_id"),)

    transaction_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="transactions")
    items: Mapped[list["TransactionItem"]] = relationship(back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    """Line-item bridge table connecting each transaction to the products in its basket."""

    __tablename__ = "transaction_items"
    __table_args__ = (UniqueConstraint("transaction_id", "product_id", name="uq_transaction_product"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.transaction_id"), index=True, nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"), index=True, nullable=False)

    transaction: Mapped[Transaction] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="items")


class AssociationRule(Base):
    """Mined rule such as [bread] -> [butter] with support, confidence, and lift."""

    __tablename__ = "association_rules"

    __table_args__ = (
        UniqueConstraint("antecedent", "consequent", "algorithm", "segment", name="uq_rule_scope"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    antecedent: Mapped[list[int]] = mapped_column(JsonList, nullable=False)
    consequent: Mapped[list[int]] = mapped_column(JsonList, nullable=False)
    support: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    lift: Mapped[float] = mapped_column(Float, nullable=False)
    algorithm: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    segment: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class CustomerCluster(Base):
    """K-Means output used to personalize rules by behavioral customer persona."""

    __tablename__ = "customer_clusters"


    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"), primary_key=True)
    cluster_label: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    persona_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    cluster_features: Mapped[dict] = mapped_column(JsonDict, nullable=False)

    customer: Mapped[Customer] = relationship(back_populates="cluster")
