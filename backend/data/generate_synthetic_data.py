from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 42
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"

CATEGORIES = {
    "Electronics": [
        ("Smartphone", 699), ("Phone Case", 24), ("Screen Protector", 12), ("Wireless Charger", 39),
        ("Bluetooth Earbuds", 89), ("Laptop", 1199), ("Laptop Sleeve", 29), ("USB-C Hub", 49),
        ("Tablet", 399), ("Tablet Stylus", 59), ("Smartwatch", 249), ("Charging Cable", 15),
        ("Portable Speaker", 79), ("Gaming Mouse", 44), ("Mechanical Keyboard", 99), ("Webcam", 65),
        ("Monitor", 229), ("HDMI Cable", 14), ("Power Bank", 35), ("Router", 89),
    ],
    "Groceries": [
        ("Bread", 3), ("Butter", 4), ("Milk", 3), ("Cereal", 5), ("Coffee", 11), ("Coffee Filters", 4),
        ("Pasta", 3), ("Tomato Sauce", 4), ("Rice", 7), ("Beans", 2), ("Eggs", 5), ("Cheese", 6),
        ("Yogurt", 5), ("Granola", 6), ("Apples", 4), ("Bananas", 2), ("Chicken Breast", 12),
        ("Salad Mix", 5), ("Olive Oil", 12), ("Sparkling Water", 6),
    ],
    "Apparel": [
        ("T-Shirt", 19), ("Jeans", 49), ("Sneakers", 79), ("Socks", 9), ("Hoodie", 45),
        ("Jacket", 99), ("Dress", 69), ("Belt", 22), ("Workout Shorts", 25), ("Leggings", 39),
        ("Cap", 18), ("Scarf", 24), ("Polo Shirt", 34), ("Chinos", 54), ("Sandals", 42),
        ("Raincoat", 85), ("Gloves", 16), ("Tie", 25), ("Blouse", 44),
    ],
    "Home": [
        ("Pillow", 25), ("Bedsheet Set", 55), ("Towel Set", 34), ("Scented Candle", 18),
        ("Coffee Mug", 12), ("Dinner Plate Set", 48), ("Throw Blanket", 39), ("Storage Bin", 22),
        ("Desk Lamp", 45), ("Extension Cord", 16), ("Air Purifier", 149), ("Vacuum Bags", 19),
        ("Cookware Set", 129), ("Cutting Board", 21), ("Knife Set", 89), ("Laundry Basket", 28),
        ("Dish Soap", 5), ("Sponge Pack", 4), ("Plant Pot", 17),
    ],
    "Beauty": [
        ("Shampoo", 8), ("Conditioner", 8), ("Body Wash", 7), ("Face Moisturizer", 18),
        ("Sunscreen", 14), ("Lip Balm", 4), ("Mascara", 12), ("Makeup Remover", 10),
        ("Razor", 11), ("Shaving Cream", 6), ("Toothbrush", 5), ("Toothpaste", 4),
        ("Perfume", 59), ("Nail Polish", 8), ("Hair Gel", 7), ("Hand Cream", 9),
        ("Cleanser", 15), ("Serum", 28), ("Deodorant", 6),
    ],
    "Sports": [
        ("Yoga Mat", 29), ("Water Bottle", 16), ("Dumbbells", 45), ("Resistance Bands", 18),
        ("Running Shoes", 95), ("Fitness Tracker", 119), ("Basketball", 24), ("Soccer Ball", 22),
        ("Tennis Racket", 79), ("Tennis Balls", 8), ("Bike Helmet", 49), ("Cycling Gloves", 18),
        ("Protein Powder", 39), ("Shaker Bottle", 12), ("Gym Bag", 35), ("Jump Rope", 11),
        ("Foam Roller", 27), ("Swim Goggles", 15), ("Hiking Backpack", 89),
    ],
    "Books": [
        ("Mystery Novel", 14), ("Science Fiction Novel", 15), ("Cookbook", 24), ("Business Book", 22),
        ("Children's Book", 10), ("Coloring Book", 8), ("Notebook", 6), ("Gel Pens", 7),
        ("History Book", 19), ("Travel Guide", 17), ("Self-Help Book", 18), ("Biography", 20),
        ("Fantasy Novel", 16), ("Book Light", 12), ("Bookmark Set", 5), ("Planner", 14),
        ("Art Book", 28), ("Language Workbook", 21),
    ],
    "Toys": [
        ("Building Blocks", 34), ("Puzzle", 18), ("Board Game", 29), ("Action Figure", 16),
        ("Doll", 22), ("Toy Car", 9), ("Remote Control Car", 45), ("Stuffed Animal", 15),
        ("Craft Kit", 24), ("Crayons", 5), ("Play Dough", 8), ("Kite", 12), ("Train Set", 55),
        ("Science Kit", 32), ("Card Game", 11), ("Baby Rattle", 7), ("Bath Toys", 10), ("Toy Storage Box", 27),
    ],
}

PATTERNS = [
    ["Bread", "Butter"], ["Milk", "Cereal"], ["Coffee", "Coffee Filters"], ["Pasta", "Tomato Sauce"],
    ["Smartphone", "Phone Case", "Screen Protector"], ["Laptop", "Laptop Sleeve", "USB-C Hub"],
    ["Shampoo", "Conditioner"], ["Razor", "Shaving Cream"], ["Toothbrush", "Toothpaste"],
    ["Yoga Mat", "Water Bottle"], ["Protein Powder", "Shaker Bottle"], ["Tennis Racket", "Tennis Balls"],
    ["Notebook", "Gel Pens"], ["Coloring Book", "Crayons"], ["Board Game", "Card Game"],
    ["Bedsheet Set", "Pillow"], ["Dish Soap", "Sponge Pack"], ["Dinner Plate Set", "Coffee Mug"],
]

SEGMENT_WEIGHTS = {
    "Budget Shopper": {"max_price": 45, "basket_bias": 2, "category_focus": ["Groceries", "Beauty", "Books"]},
    "Premium Shopper": {"max_price": 2000, "basket_bias": 3, "category_focus": ["Electronics", "Home", "Sports"]},
    "Occasional Buyer": {"max_price": 120, "basket_bias": 1, "category_focus": list(CATEGORIES)},
    "Bulk Buyer": {"max_price": 80, "basket_bias": 5, "category_focus": ["Groceries", "Home", "Beauty"]},
}


def generate_products() -> pd.DataFrame:
    rows = []
    product_id = 1
    for category, products in CATEGORIES.items():
        for name, price in products:
            rows.append({"product_id": product_id, "name": name, "category": category, "price": float(price)})
            product_id += 1
    return pd.DataFrame(rows)


def generate_customers(n_customers: int = 5_000) -> pd.DataFrame:
    segment_names = list(SEGMENT_WEIGHTS)
    segment_probs = [0.35, 0.18, 0.32, 0.15]
    start = datetime.now() - timedelta(days=730)
    rows = []
    for customer_id in range(1, n_customers + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "signup_date": start + timedelta(days=random.randint(0, 720)),
                "segment_hint": np.random.choice(segment_names, p=segment_probs),
            }
        )
    return pd.DataFrame(rows)


def _weighted_product_choice(products: pd.DataFrame, segment_hint: str) -> int:
    prefs = SEGMENT_WEIGHTS[segment_hint]
    candidates = products[products["category"].isin(prefs["category_focus"])].copy()
    if candidates.empty:
        candidates = products.copy()

    # POS baskets are price-sensitive: lower-priced products appear more often,
    # but premium buyers still have a chance to choose expensive electronics.
    price_penalty = np.where(candidates["price"] <= prefs["max_price"], 1.0, 0.15)
    inverse_price = 1 / np.sqrt(candidates["price"].to_numpy())
    weights = inverse_price * price_penalty
    weights = weights / weights.sum()
    return int(np.random.choice(candidates["product_id"], p=weights))


def generate_transactions(products: pd.DataFrame, customers: pd.DataFrame, n_transactions: int = 40_000) -> pd.DataFrame:
    name_to_id = dict(zip(products["name"], products["product_id"]))
    customer_segments = dict(zip(customers["customer_id"], customers["segment_hint"]))
    customer_ids = customers["customer_id"].to_numpy()
    start = datetime.now() - timedelta(days=365)
    rows = []

    for transaction_id in range(1, n_transactions + 1):
        customer_id = int(np.random.choice(customer_ids))
        segment = customer_segments[customer_id]
        basket_size = min(8, max(1, np.random.poisson(SEGMENT_WEIGHTS[segment]["basket_bias"]) + 1))
        basket: set[int] = set()

        # Real carts contain repeated motifs. Injecting co-purchase patterns gives
        # association mining meaningful signal while noise keeps the data realistic.
        if random.random() < 0.42:
            pattern = random.choice(PATTERNS)
            basket.update(name_to_id[name] for name in pattern if name in name_to_id)

        while len(basket) < basket_size:
            basket.add(_weighted_product_choice(products, segment))

        timestamp = start + timedelta(minutes=random.randint(0, 365 * 24 * 60))
        for product_id in basket:
            rows.append(
                {
                    "transaction_id": transaction_id,
                    "customer_id": customer_id,
                    "timestamp": timestamp,
                    "product_id": product_id,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    products = generate_products()
    customers = generate_customers()
    transactions = generate_transactions(products, customers)
    products.to_csv(RAW_DIR / "products.csv", index=False)
    customers.to_csv(RAW_DIR / "customers.csv", index=False)
    transactions.to_csv(RAW_DIR / "transactions.csv", index=False)
    print(f"Generated {len(products)} products, {len(customers)} customers, {transactions['transaction_id'].nunique()} transactions.")


if __name__ == "__main__":
    main()
