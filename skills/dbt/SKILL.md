---
name: dbt Data Transformation
description: dbt best practices for data modeling, testing, documentation, and transformation pipelines
version: 1.0.0
triggers:
  - dbt
  - data build tool
  - data transformation
  - data modeling
  - staging models
  - mart models
  - data warehouse
---

# dbt Data Transformation Skill

This skill automatically activates when working with dbt to ensure best practices for data modeling, testing, and documentation.

## Core Principle

**MODULAR, TESTED, DOCUMENTED DATA TRANSFORMATIONS**

```
❌ Monolithic SQL, no tests, undocumented columns
✅ Layered models, comprehensive tests, full documentation
```

## Project Structure

```
dbt_project/
├── dbt_project.yml
├── profiles.yml            # Connection profiles
├── packages.yml            # Package dependencies
├── models/
│   ├── staging/           # Source cleaning
│   │   ├── _staging.yml   # Source definitions
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/      # Business logic
│   │   ├── int_orders_pivoted.sql
│   │   └── int_customer_orders.sql
│   └── marts/            # Business entities
│       ├── core/
│       │   ├── dim_customers.sql
│       │   └── fct_orders.sql
│       └── marketing/
│           └── mkt_customer_segments.sql
├── seeds/                 # Static data (CSV)
├── snapshots/            # SCD Type 2
├── macros/               # Reusable SQL
├── tests/                # Custom tests
│   ├── generic/
│   └── singular/
└── analyses/             # Ad-hoc queries
```

## Model Layers

```sql
-- models/staging/stg_orders.sql
-- Staging: Clean, rename, type-cast source data
with source as (
    select * from {{ source('raw', 'orders') }}
),

renamed as (
    select
        -- Keys
        id as order_id,
        customer_id,

        -- Dimensions
        lower(status) as order_status,

        -- Dates
        created_at::timestamp as ordered_at,
        updated_at::timestamp as updated_at,

        -- Measures
        total_amount_cents / 100.0 as total_amount,

        -- Metadata
        _loaded_at as loaded_at

    from source
    where id is not null  -- Filter invalid records
)

select * from renamed

-- models/intermediate/int_customer_orders.sql
-- Intermediate: Combine and transform
with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    select
        customers.customer_id,
        customers.customer_name,
        count(orders.order_id) as total_orders,
        sum(orders.total_amount) as lifetime_value,
        min(orders.ordered_at) as first_order_at,
        max(orders.ordered_at) as last_order_at

    from customers
    left join orders using (customer_id)
    group by 1, 2
)

select * from customer_orders

-- models/marts/core/dim_customers.sql
-- Marts: Business entities for consumption
{{
    config(
        materialized='table',
        schema='marts',
        tags=['daily']
    )
}}

with customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

final as (
    select
        customer_id,
        customer_name,
        total_orders,
        lifetime_value,
        first_order_at,
        last_order_at,
        {{ dbt_utils.datediff('first_order_at', 'current_date', 'day') }} as customer_age_days,

        case
            when total_orders = 0 then 'prospect'
            when total_orders = 1 then 'new'
            when total_orders < 5 then 'developing'
            else 'loyal'
        end as customer_segment

    from customer_orders
)

select * from final
```

## Testing

```yaml
# models/staging/_staging.yml
version: 2

sources:
  - name: raw
    database: raw_data
    schema: public
    tables:
      - name: orders
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        loaded_at_field: _loaded_at
        columns:
          - name: id
            tests:
              - not_null
              - unique

models:
  - name: stg_orders
    description: Cleaned orders from source
    columns:
      - name: order_id
        description: Primary key
        tests:
          - not_null
          - unique
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: order_status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled', 'refunded']
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"

  - name: dim_customers
    description: Customer dimension with metrics
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - customer_id
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique
      - name: lifetime_value
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

## Macros

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {% if custom_schema_name is not none %}
        {{ custom_schema_name }}
    {% else %}
        {{ target.schema }}
    {% endif %}
{% endmacro %}

-- macros/limit_rows.sql
{% macro limit_rows(n=1000) %}
    {% if target.name == 'dev' %}
        limit {{ n }}
    {% endif %}
{% endmacro %}

-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)::decimal(10,2)
{% endmacro %}
```

## dbt Checklist

```
📋 dbt Best Practices Checklist

□ STRUCTURE
  □ staging → intermediate → marts layers
  □ One model per file
  □ Consistent naming conventions
  □ Sources defined in _sources.yml

□ TESTING
  □ Primary keys: unique, not_null
  □ Foreign keys: relationships test
  □ Business rules: expression tests
  □ Source freshness configured

□ DOCUMENTATION
  □ All models documented
  □ Column descriptions
  □ Source documentation
  □ dbt docs generate passes

□ PERFORMANCE
  □ Incremental models for large tables
  □ Appropriate materializations
  □ Partitioning/clustering configured
```

## Warning Triggers

Automatically warn when:

1. **Missing tests**
   > "⚠️ DBT: Add not_null and unique tests to primary keys"

2. **No documentation**
   > "⚠️ DBT: Add descriptions to models and columns"

3. **Direct source reference**
   > "⚠️ DBT: Use staging models instead of direct source refs"
