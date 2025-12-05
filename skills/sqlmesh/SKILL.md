---
name: SQLMesh Data Transformation
description: SQLMesh best practices for data modeling, virtual data environments, and CI/CD-friendly transformations
version: 1.0.0
triggers:
  - sqlmesh
  - sql mesh
  - virtual environments
  - data transformation
  - column-level lineage
---

# SQLMesh Data Transformation Skill

This skill automatically activates when working with SQLMesh to leverage its virtual data environments, automatic column lineage, and CI/CD-friendly features.

## Core Principle

**EFFICIENT, ISOLATED, AUDITABLE DATA TRANSFORMATIONS**

```
❌ Full table scans, no environment isolation, manual lineage
✅ Incremental processing, virtual environments, automatic lineage
```

## Project Structure

```
sqlmesh_project/
├── config.yaml              # Project configuration
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/
│   │   └── int_customer_orders.sql
│   └── marts/
│       ├── dim_customers.sql
│       └── fct_orders.sql
├── macros/
│   └── common.py
├── seeds/
│   └── country_codes.csv
├── audits/
│   └── row_count.sql
└── tests/
    └── test_models.yaml
```

## Configuration

```yaml
# config.yaml
gateways:
  local:
    connection:
      type: duckdb
      database: data/warehouse.db

  prod:
    connection:
      type: snowflake
      account: myaccount
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      warehouse: COMPUTE_WH
      database: ANALYTICS

default_gateway: local

model_defaults:
  dialect: snowflake
  start: 2024-01-01

plan:
  auto_apply: false
  forward_only: false
  include_unmodified: false
```

## Model Definitions

```sql
-- models/staging/stg_orders.sql
MODEL (
  name staging.stg_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column ordered_at,
    batch_size 7,
    lookback 1
  ),
  cron '@daily',
  grain order_id,
  owner 'data-team',
  tags ['staging', 'orders']
);

SELECT
    id AS order_id,
    customer_id,
    LOWER(status) AS order_status,
    created_at::TIMESTAMP AS ordered_at,
    total_amount_cents / 100.0 AS total_amount,
    @start_date AS _start_date,
    @end_date AS _end_date
FROM raw.orders
WHERE created_at BETWEEN @start_date AND @end_date
  AND id IS NOT NULL;

-- models/intermediate/int_customer_orders.sql
MODEL (
  name intermediate.int_customer_orders,
  kind FULL,
  cron '@daily',
  grain customer_id,
  audits (
    NOT_NULL(columns := [customer_id]),
    UNIQUE(columns := [customer_id])
  )
);

WITH customers AS (
    SELECT * FROM staging.stg_customers
),

orders AS (
    SELECT * FROM staging.stg_orders
),

customer_orders AS (
    SELECT
        c.customer_id,
        c.customer_name,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS lifetime_value,
        MIN(o.ordered_at) AS first_order_at,
        MAX(o.ordered_at) AS last_order_at
    FROM customers c
    LEFT JOIN orders o USING (customer_id)
    GROUP BY 1, 2
)

SELECT * FROM customer_orders;

-- models/marts/dim_customers.sql
MODEL (
  name marts.dim_customers,
  kind SCD_TYPE_2 (
    unique_key customer_id,
    valid_from_name valid_from,
    valid_to_name valid_to,
    invalidate_hard_deletes true
  ),
  cron '@daily',
  grain customer_id,
  owner 'analytics-team'
);

@DEF(
  customer_segment,
  CASE
    WHEN total_orders = 0 THEN 'prospect'
    WHEN total_orders = 1 THEN 'new'
    WHEN total_orders < 5 THEN 'developing'
    ELSE 'loyal'
  END
);

SELECT
    customer_id,
    customer_name,
    total_orders,
    lifetime_value,
    first_order_at,
    last_order_at,
    DATEDIFF('day', first_order_at, CURRENT_DATE) AS customer_age_days,
    @customer_segment AS customer_segment
FROM intermediate.int_customer_orders;
```

## Virtual Data Environments

```bash
# Create a virtual environment for development
sqlmesh plan dev

# Preview changes without applying
sqlmesh plan dev --select-model marts.dim_customers

# Apply changes to dev environment
sqlmesh plan dev --auto-apply

# Run specific models
sqlmesh run --select-model marts.dim_customers

# Promote to production
sqlmesh plan prod

# Compare environments
sqlmesh diff dev prod
```

## Audits and Tests

```yaml
# tests/test_models.yaml
tests:
  - model: marts.dim_customers
    description: Validate customer dimension
    tests:
      - name: primary_key_unique
        sql: |
          SELECT customer_id, COUNT(*)
          FROM marts.dim_customers
          WHERE valid_to IS NULL
          GROUP BY 1
          HAVING COUNT(*) > 1

      - name: no_negative_lifetime_value
        sql: |
          SELECT *
          FROM marts.dim_customers
          WHERE lifetime_value < 0
```

```sql
-- audits/row_count.sql
AUDIT (
  name row_count_check,
  dialect snowflake
);

@DEF(min_rows, 1000);

SELECT COUNT(*) AS cnt
FROM @this_model
HAVING COUNT(*) < @min_rows;
```

## Python Models

```python
# models/ml/customer_predictions.py
import typing as t
from sqlmesh import model
from sqlmesh.core.model.kind import ModelKindName
import pandas as pd

@model(
    "ml.customer_predictions",
    kind=dict(
        name=ModelKindName.FULL,
    ),
    columns={
        "customer_id": "VARCHAR",
        "churn_probability": "FLOAT",
        "predicted_at": "TIMESTAMP",
    },
    cron="@daily",
)
def execute(
    context,
    start: str,
    end: str,
    **kwargs,
) -> pd.DataFrame:
    # Load data from upstream model
    df = context.fetchdf("SELECT * FROM marts.dim_customers")

    # Apply ML model
    predictions = predict_churn(df)

    return predictions
```

## SQLMesh vs dbt Comparison

```
FEATURE COMPARISON
════════════════════════════════════════════════════════════

Feature              │ SQLMesh           │ dbt
─────────────────────┼───────────────────┼──────────────────
Virtual Environments │ ✅ Built-in       │ ❌ Clone schemas
Column Lineage       │ ✅ Automatic      │ ⚠️ Manual/paid
Incremental Logic    │ ✅ Automatic      │ ⚠️ Manual macros
CI/CD Preview        │ ✅ Zero-copy      │ ❌ Clone schemas
Python Models        │ ✅ First-class    │ ⚠️ Limited
Plan/Apply           │ ✅ Built-in       │ ❌ Requires tools
```

## SQLMesh Checklist

```
📋 SQLMesh Best Practices Checklist

□ MODEL CONFIGURATION
  □ Appropriate model kind (FULL/INCREMENTAL/SCD)
  □ Grain defined for all models
  □ Cron schedule configured
  □ Owner assigned

□ QUALITY
  □ Audits on critical models
  □ Tests for business logic
  □ Column-level lineage validated

□ PERFORMANCE
  □ Incremental for large tables
  □ Batch size optimized
  □ Lookback period appropriate

□ CI/CD
  □ Virtual environments in PRs
  □ Plan before apply
  □ Forward-only migrations for prod
```

## Warning Triggers

Automatically warn when:

1. **Missing grain**
   > "⚠️ SQLMESH: Define grain for model to enable proper incremental processing"

2. **No audits on marts**
   > "⚠️ SQLMESH: Add audits to mart models for data quality"

3. **Full refresh on large tables**
   > "⚠️ SQLMESH: Consider INCREMENTAL_BY_TIME_RANGE for large tables"
