---
name: dlt Data Loading
description: dlt (data load tool) best practices for building Python data pipelines, schema management, and incremental loading
version: 1.0.0
triggers:
  - dlt
  - dlthub
  - data load tool
  - python etl
  - data pipeline
  - extract load
  - data ingestion
---

# dlt Data Loading Skill

This skill automatically activates when working with dlt to ensure best practices for data extraction, loading, schema management, and pipeline reliability.

## Core Principle

**DECLARATIVE, INCREMENTAL, SCHEMA-AWARE DATA PIPELINES**

```
❌ Manual schema management, full loads, brittle pipelines
✅ Auto-schema evolution, incremental loading, type-safe extraction
```

## Project Structure

```
dlt_project/
├── .dlt/
│   ├── config.toml           # Configuration
│   └── secrets.toml          # Credentials (gitignored)
├── pipelines/
│   ├── __init__.py
│   ├── github_pipeline.py    # Source-specific pipeline
│   └── api_pipeline.py
├── sources/
│   ├── __init__.py
│   ├── github/
│   │   ├── __init__.py
│   │   ├── source.py         # Source definition
│   │   └── helpers.py
│   └── rest_api/
│       ├── __init__.py
│       └── source.py
├── tests/
│   ├── test_sources.py
│   └── test_pipelines.py
├── schemas/
│   └── export/               # Exported schemas
├── pyproject.toml
└── requirements.txt
```

## Configuration

```toml
# .dlt/config.toml
[runtime]
log_level = "INFO"
dlthub_telemetry = false

[normalize]
loader_file_format = "parquet"

[load]
workers = 4

# Source-specific config
[sources.github]
api_version = "2022-11-28"
```

```toml
# .dlt/secrets.toml (NEVER commit this file)
[sources.github]
access_token = "ghp_xxx"

[destination.bigquery]
project_id = "my-project"
location = "US"

[destination.snowflake]
database = "ANALYTICS"
warehouse = "COMPUTE_WH"
username = "dlt_user"
password = "secret"
host = "account.snowflakecomputing.com"
```

## Source Definition

```python
# sources/github/source.py
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import HeaderLinkPaginator

@dlt.source(name="github", max_table_nesting=1)
def github_source(
    access_token: str = dlt.secrets.value,
    org: str = dlt.config.value,
) -> Iterator[DltResource]:
    """
    GitHub source for repositories, issues, and pull requests.

    Args:
        access_token: GitHub personal access token
        org: GitHub organization name
    """
    client = RESTClient(
        base_url="https://api.github.com",
        headers={"Authorization": f"Bearer {access_token}"},
        paginator=HeaderLinkPaginator(),
    )

    yield repositories(client, org)
    yield issues(client, org)
    yield pull_requests(client, org)


@dlt.resource(
    name="repositories",
    write_disposition="merge",
    primary_key="id",
    columns={"updated_at": {"data_type": "timestamp"}},
)
def repositories(
    client: RESTClient,
    org: str,
    updated_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "updated_at",
        initial_value="2024-01-01T00:00:00Z",
    ),
) -> Iterator[dict]:
    """Load repositories with incremental updates."""
    for page in client.paginate(
        f"/orgs/{org}/repos",
        params={
            "sort": "updated",
            "direction": "desc",
            "per_page": 100,
        },
    ):
        for repo in page.json():
            if repo["updated_at"] > updated_at.last_value:
                yield repo
            else:
                return  # Stop when reaching already loaded data


@dlt.resource(
    name="issues",
    write_disposition="merge",
    primary_key="id",
)
def issues(
    client: RESTClient,
    org: str,
    updated_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "updated_at",
        initial_value="2024-01-01T00:00:00Z",
    ),
) -> Iterator[dict]:
    """Load issues incrementally by update time."""
    # Get all repos first
    repos = list(client.paginate(f"/orgs/{org}/repos"))

    for repo_page in repos:
        for repo in repo_page.json():
            for page in client.paginate(
                f"/repos/{org}/{repo['name']}/issues",
                params={
                    "state": "all",
                    "sort": "updated",
                    "since": updated_at.last_value,
                },
            ):
                yield from page.json()
```

## Pipeline Definition

```python
# pipelines/github_pipeline.py
import dlt
from sources.github import github_source

def run_github_pipeline(
    destination: str = "bigquery",
    dataset_name: str = "github_data",
    full_refresh: bool = False,
) -> dlt.Pipeline:
    """
    Run the GitHub data pipeline.

    Args:
        destination: Target destination (bigquery, snowflake, duckdb)
        dataset_name: Target dataset/schema name
        full_refresh: If True, drop and reload all data
    """
    # Create pipeline
    pipeline = dlt.pipeline(
        pipeline_name="github",
        destination=destination,
        dataset_name=dataset_name,
        progress="log",
    )

    # Configure source
    source = github_source()

    # Optionally filter resources
    # source = source.with_resources("repositories", "issues")

    # Run the pipeline
    if full_refresh:
        load_info = pipeline.run(
            source,
            write_disposition="replace",
        )
    else:
        load_info = pipeline.run(source)

    # Print load results
    print(f"Pipeline completed: {load_info}")
    print(f"Load package: {load_info.load_packages}")

    # Check for errors
    if load_info.has_failed_jobs:
        for job in load_info.load_packages[0].jobs["failed_jobs"]:
            print(f"Failed job: {job.file_path}")
            print(f"Error: {job.failed_message}")
        raise RuntimeError("Pipeline has failed jobs")

    return pipeline


if __name__ == "__main__":
    run_github_pipeline()
```

## Incremental Loading Patterns

```python
# Pattern 1: Cursor-based incremental (most common)
@dlt.resource(write_disposition="merge", primary_key="id")
def orders(
    updated_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "updated_at",
        initial_value="2024-01-01T00:00:00Z",
    ),
) -> Iterator[dict]:
    """Incrementally load orders by updated_at cursor."""
    response = api.get_orders(since=updated_at.last_value)
    yield from response["orders"]


# Pattern 2: Append-only (logs, events)
@dlt.resource(write_disposition="append")
def events(
    created_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "created_at",
        initial_value="2024-01-01T00:00:00Z",
    ),
) -> Iterator[dict]:
    """Append new events without deduplication."""
    for event in api.get_events(after=created_at.last_value):
        yield event


# Pattern 3: Full replace (small reference tables)
@dlt.resource(write_disposition="replace")
def countries() -> Iterator[dict]:
    """Full refresh of country reference data."""
    yield from api.get_countries()


# Pattern 4: Merge with delete detection
@dlt.resource(
    write_disposition="merge",
    primary_key="id",
    merge_key="id",  # Use for SCD Type 1
)
def customers(
    updated_at: dlt.sources.incremental[str] = dlt.sources.incremental(
        "updated_at",
    ),
) -> Iterator[dict]:
    """Merge customers with upsert logic."""
    for customer in api.get_customers(modified_since=updated_at.last_value):
        yield customer
```

## Schema Management

```python
# Explicit schema definition
@dlt.resource(
    columns={
        "id": {"data_type": "bigint", "nullable": False},
        "name": {"data_type": "text", "nullable": False},
        "email": {"data_type": "text", "nullable": True},
        "created_at": {"data_type": "timestamp", "nullable": False},
        "metadata": {"data_type": "json"},  # Complex nested data
    },
    primary_key="id",
)
def users() -> Iterator[dict]:
    yield from api.get_users()


# Schema contracts for strict validation
@dlt.source(schema_contract="freeze")  # No schema changes allowed
def strict_source():
    ...


@dlt.source(schema_contract={
    "tables": "evolve",      # Allow new tables
    "columns": "freeze",     # No new columns
    "data_type": "discard_value",  # Discard rows with wrong types
})
def controlled_source():
    ...


# Export and version schemas
pipeline = dlt.pipeline(...)
pipeline.run(source)

# Export current schema
schema = pipeline.default_schema
schema.to_yaml("schemas/export/github_schema.yaml")

# Import and apply schema
from dlt import Schema
schema = Schema.from_yaml("schemas/export/github_schema.yaml")
```

## Transformers and Processing

```python
# Add computed columns during extraction
@dlt.transformer(
    data_from=orders,
    write_disposition="merge",
    primary_key="id",
)
def enriched_orders(order: dict) -> dict:
    """Enrich orders with computed fields."""
    order["total_with_tax"] = order["total"] * 1.2
    order["order_year"] = order["created_at"][:4]
    return order


# Filter and transform in streaming fashion
@dlt.transformer(data_from=events)
def filtered_events(event: dict) -> Iterator[dict]:
    """Filter events by type."""
    if event["type"] in ["purchase", "signup"]:
        yield {
            "event_id": event["id"],
            "event_type": event["type"],
            "user_id": event["user_id"],
            "timestamp": event["timestamp"],
        }


# Parallel resource loading
source = my_source()
source.repositories.parallelize()
source.issues.parallelize()
```

## Error Handling and Retry

```python
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import BearerTokenAuth
from tenacity import retry, stop_after_attempt, wait_exponential

# Built-in retry configuration
client = RESTClient(
    base_url="https://api.example.com",
    auth=BearerTokenAuth(token=dlt.secrets["api_token"]),
    # Retry configuration
    request_timeout=30,
    retry_status_codes=[429, 500, 502, 503, 504],
    max_retries=5,
)

# Custom retry logic
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
)
def fetch_with_retry(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# Handle partial failures gracefully
@dlt.resource
def resilient_resource() -> Iterator[dict]:
    for item_id in get_item_ids():
        try:
            item = fetch_item(item_id)
            yield item
        except Exception as e:
            # Log error but continue processing
            dlt.current.source_state()["failed_items"].append(item_id)
            continue
```

## Testing

```python
# tests/test_sources.py
import pytest
import dlt
from sources.github import github_source

def test_github_source_schema():
    """Test that source produces expected schema."""
    source = github_source()

    # Get schema without running
    schema = source.discover_schema()

    assert "repositories" in schema.tables
    assert "id" in schema.tables["repositories"].columns


def test_github_source_data():
    """Test source with local DuckDB destination."""
    pipeline = dlt.pipeline(
        pipeline_name="test_github",
        destination="duckdb",
        dataset_name="test_data",
    )

    source = github_source()
    # Limit data for testing
    source.repositories.add_limit(10)

    load_info = pipeline.run(source)

    assert not load_info.has_failed_jobs

    # Verify data loaded
    with pipeline.sql_client() as client:
        result = client.execute_sql("SELECT COUNT(*) FROM repositories")
        assert result[0][0] > 0


def test_incremental_loading():
    """Test incremental loading behavior."""
    pipeline = dlt.pipeline(
        pipeline_name="test_incremental",
        destination="duckdb",
    )

    # First run
    load_info_1 = pipeline.run(my_source())

    # Second run should load less data
    load_info_2 = pipeline.run(my_source())

    # Verify incremental state
    state = pipeline.state
    assert "sources" in state
```

## Common Destinations

```python
# DuckDB (local development)
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",
    dataset_name="my_data",
)

# BigQuery
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="bigquery",
    dataset_name="my_data",
)

# Snowflake
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="snowflake",
    dataset_name="my_data",
)

# PostgreSQL
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="postgres",
    dataset_name="my_data",
)

# Filesystem (S3, GCS, local)
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="filesystem",
    dataset_name="my_data",
)
```

## CLI Commands

```bash
# Initialize a new dlt project
dlt init <source> <destination>

# Example: Initialize GitHub to BigQuery pipeline
dlt init github bigquery

# Run a pipeline
python pipelines/github_pipeline.py

# Check pipeline state
dlt pipeline github info

# Show loaded data
dlt pipeline github show

# Trace and debug
dlt pipeline github trace

# Drop and recreate dataset
dlt pipeline github drop

# Sync schema
dlt pipeline github sync-schema
```

## dlt Checklist

```
📋 dlt Best Practices Checklist

□ SOURCE DESIGN
  □ Use @dlt.source decorator for grouping resources
  □ Define primary_key for merge operations
  □ Configure incremental loading where applicable
  □ Set appropriate write_disposition

□ SCHEMA MANAGEMENT
  □ Define explicit column types for critical fields
  □ Use schema contracts in production
  □ Export and version control schemas
  □ Test schema evolution

□ RELIABILITY
  □ Handle API rate limits and retries
  □ Implement proper error handling
  □ Use transactions for related resources
  □ Add monitoring and alerting

□ TESTING
  □ Unit tests for transformers
  □ Integration tests with DuckDB
  □ Schema validation tests
  □ Incremental loading tests

□ SECRETS
  □ Use .dlt/secrets.toml locally
  □ Environment variables in production
  □ Never commit secrets to git
```

## Warning Triggers

Automatically warn when:

1. **Missing primary key for merge**
   > "⚠️ DLT: Add primary_key to resource using write_disposition='merge'"

2. **No incremental loading**
   > "⚠️ DLT: Consider dlt.sources.incremental for large datasets"

3. **Secrets in code**
   > "⚠️ DLT: Use dlt.secrets.value instead of hardcoded credentials"

4. **No error handling**
   > "⚠️ DLT: Add try/except for API calls in resource functions"

5. **Missing schema contract**
   > "⚠️ DLT: Consider schema_contract for production pipelines"
