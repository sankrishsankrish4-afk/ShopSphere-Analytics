# ShopSphere Analytics

ShopSphere Analytics is a full-stack market basket analysis application for upselling and cross-selling. It generates synthetic POS transactions, loads them through an ETL pipeline, mines association rules with Apriori, FP-Growth, and ECLAT, clusters customers with K-Means, and exposes the results through a FastAPI API and Next.js dashboard.

## Key Deliverables

- Rule Engine API: submit cart product IDs and receive complementary recommendations ranked by lift and confidence.
- Association Matrix Dashboard: browse support, confidence, lift, category heatmaps, and customer-persona-specific rules.
- Customer Segmentation: K-Means personas based on frequency, basket size, spend, and category diversity.

## Screenshot Placeholder

Add dashboard screenshots here after running the app locally.

## Docker Setup

```bash
docker compose up --build
```

After containers start, seed the database from the backend container:

```bash
docker compose exec backend python data/seed_database.py
```

Open `http://localhost:3000` for the dashboard and `http://localhost:8000/docs` for Swagger UI.

## Manual Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python data/generate_synthetic_data.py
python data/seed_database.py
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Tests

```bash
cd backend
pytest
```

## Why These Algorithms

- Apriori is easy to explain and useful for learning because it expands candidate itemsets level by level.
- FP-Growth is usually faster on larger baskets because it compresses transactions into an FP-tree instead of generating candidates repeatedly.
- ECLAT uses vertical item-to-transaction-ID sets and intersections, making it a strong portfolio addition because the implementation shows algorithm understanding from scratch.

Run `benchmark_all()` in `backend/app/ml/eclat_engine.py` against a transaction DataFrame to compare rule counts and runtime.
