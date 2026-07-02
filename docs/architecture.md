# Architecture

```text
Synthetic POS Data -> ETL Pipeline -> PostgreSQL/SQLite
                                      |
                         +------------+------------+
                         |                         |
              Association Rule Engines     K-Means Clustering
           (Apriori / FP-Growth / ECLAT)   (customer personas)
                         |                         |
                         +------------+------------+
                                      |
                               FastAPI Backend
                         (Rule Engine + Analytics API)
                                      |
                              Next.js Dashboard
                 (Matrix, Heatmap, Clusters, Demo Cart)
```

## Data Flow

1. Synthetic data generation creates products, customers, and long-format transaction items with realistic co-purchase patterns.
2. ETL validates referential integrity, deduplicates rows, and loads normalized SQL tables.
3. Association mining converts baskets into itemsets and saves rules with support, confidence, and lift.
4. K-Means builds customer personas from frequency, basket size, spend, and category diversity.
5. FastAPI serves recommendations, rules, clusters, summary KPIs, and lift matrices.
6. Next.js turns those endpoints into a merchandising dashboard and live cart recommendation demo.

The non-trivial part is the combination of batch data engineering, three rule-mining approaches, segment-aware personalization, and a UI that exposes both analytical exploration and a production-style recommendation use case.
