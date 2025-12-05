---
name: RAG & CAG Architecture
description: Automatic architecture guidance for Retrieval-Augmented Generation and Cache-Augmented Generation systems with security-first multi-tenant design
version: 1.0.0
triggers:
  - rag
  - cag
  - retrieval augmented generation
  - cache augmented generation
  - vector database
  - embeddings
  - semantic search
  - chunking
  - hybrid search
  - graphrag
  - knowledge base
  - document processing
  - multi-tenant rag
---

# RAG & CAG Architecture Skill

This skill automatically activates when designing or implementing RAG/CAG systems. It provides architecture patterns, chunking strategies, security considerations, and volume-based scaling guidance.

## Core Principle

**Choose architecture based on volume and query complexity, not just features.**

```
ARCHITECTURE SELECTION
════════════════════════════════════════════════════════════════

Corpus < 100K tokens?           → CAG (Cache-Augmented Generation)
Documents < 10K?                → Simple RAG + Semantic Cache
Documents 10K-500K?             → Hybrid RAG + Federated Indexes
Documents 500K-5M?              → Agentic RAG + Sharded Storage
Documents 5M+?                  → Multi-cluster + GraphRAG
Need cross-document reasoning?  → Add GraphRAG layer
```

## Automatic Behaviors

When this skill activates, Claude will:

### 1. Identify RAG/CAG Requirements

Automatically assess when code involves:
- Document ingestion pipelines (chunking strategy needed)
- Vector store configuration (tenant isolation required)
- Query routing (complexity classification needed)
- Semantic caching (cache invalidation patterns)
- Multi-tenant data access (isolation level selection)

### 2. Recommend Hybrid Architecture Patterns

For any RAG implementation, evaluate the three hybridization levels:

```
HYBRID RAG LEVELS
════════════════════════════════════════════════════════════════

LEVEL 1: HYBRID SEARCH (Dense + Sparse)
├── Dense vectors: Semantic similarity
├── Sparse vectors: BM25 keyword matching
├── Fusion: Reciprocal Rank Fusion (RRF)
└── When: Almost always (default recommendation)

LEVEL 2: HYBRIDRAG (Vector + Graph)
├── VectorRAG: Semantic search
├── GraphRAG: Entity relationships, multi-hop
├── Benchmark: 80% accuracy vs 50% individual
└── When: Complex queries requiring relationship reasoning

LEVEL 3: MULTI-PATTERN (Router Architecture)
├── Simple RAG: Direct fact lookup
├── Graph RAG: Entity relationships
├── RAPTOR: Global themes, summaries
├── Agentic RAG: Multi-step reasoning
└── When: Varied query complexity
```

### 3. Enforce Chunking Strategy Selection

When reviewing or writing ingestion code, recommend appropriate chunking:

```python
# Strategy Selection Matrix
CHUNKING_STRATEGIES = {
    "fixed_size": {
        "speed": "fast",
        "cost": "low",
        "quality": "medium",
        "best_for": ["prototyping", "homogeneous_text"]
    },
    "semantic": {
        "speed": "medium",
        "cost": "medium",
        "quality": "high",
        "best_for": ["mixed_topics", "complex_documents"]
    },
    "hierarchical": {
        "speed": "medium",
        "cost": "medium",
        "quality": "high",
        "best_for": ["multi_level_queries", "detailed_and_context"]
    },
    "raptor": {
        "speed": "slow",
        "cost": "high",
        "quality": "very_high",
        "best_for": ["long_documents", "global_queries"]
    },
    "late_chunking": {
        "speed": "medium",
        "cost": "medium",
        "quality": "very_high",
        "best_for": ["cross_references", "legal_technical"]
    },
    "agentic": {
        "speed": "slow",
        "cost": "very_high",
        "quality": "very_high",
        "best_for": ["high_value_documents", "contracts"]
    }
}
```

### 4. Recommend Volume-Based Architecture

#### Tier 1: Small Scale (< 10K documents)

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Gateway                       │
│              (Auth + Rate Limiting)                      │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Semantic │  │ Single   │  │   LLM    │
        │  Cache   │  │  Index   │  │ (Claude/ │
        │ (Redis)  │  │ (Chroma) │  │  GPT-4)  │
        └──────────┘  └──────────┘  └──────────┘
```

**Key decisions**:
- CAG viable if corpus < 100K tokens
- Single embedding model: `text-embedding-3-small`
- No sharding: Single Chroma or pgvector
- Basic caching: Redis with exact + fuzzy match

#### Tier 2: Medium Scale (10K-500K documents)

```
┌─────────────────────────────────────────────────────────────────┐
│                      Load Balancer + WAF                         │
└─────────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application Cluster                   │
│    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│    │ Auth    │  │ Router  │  │ Query   │  │ Response│          │
│    │Middleware│ │ Agent   │  │ Rewriter│  │ Synth   │          │
│    └─────────┘  └─────────┘  └─────────┘  └─────────┘          │
└─────────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
    ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────┐
    │ Semantic │  │   Federated   │  │ Reranker │  │   LLM    │
    │  Cache   │  │    Indexes    │  │ (Cross-  │  │ Gateway  │
    └──────────┘  │   (Qdrant)    │  │ encoder) │  └──────────┘
                  └──────────────┘  └──────────┘
```

**Key decisions**:
- Federated indexes by source type
- Hybrid search + cross-encoder reranking
- Document routing by type

#### Tier 3: Large Scale (500K-5M documents)

- Multi-region deployment
- Agentic RAG router
- Tiered storage (hot/warm/cold)
- Milvus cluster with sharding

#### Tier 4: Massive Scale (5M+ documents)

- Multi-cluster + GraphRAG
- Hierarchical retrieval (RAPTOR)
- Global theme indexing

### 5. Enforce Multi-Tenant Isolation

```python
# ✅ CORRECT: Tenant isolation based on compliance
class IsolationLevel(Enum):
    CLUSTER = "cluster"        # Dedicated cluster (most isolated)
    COLLECTION = "collection"  # Separate collections per tenant
    NAMESPACE = "namespace"    # Namespaces within shared collection
    FILTER = "filter"          # Metadata filtering (least isolated)

def get_isolation_strategy(tenant: Tenant) -> IsolationLevel:
    if tenant.compliance_level == "high":  # HIPAA, SOC2
        return IsolationLevel.CLUSTER
    elif tenant.data_sensitivity == "high":
        return IsolationLevel.COLLECTION
    elif tenant.scale == "enterprise":
        return IsolationLevel.NAMESPACE
    else:
        return IsolationLevel.FILTER

# ❌ WRONG: Single collection without tenant filtering
async def search(query: str):
    return await index.search(query)  # No tenant isolation!
```

### 6. Flag RAG Anti-Patterns

Automatically warn when detecting:

| Anti-Pattern | Warning |
|--------------|---------|
| No hybrid search | "Consider dense + sparse for better recall" |
| Missing reranking | "Add cross-encoder reranking for precision" |
| No semantic caching | "60%+ cost savings possible with semantic cache" |
| Single chunking strategy | "Match chunking to document type" |
| No tenant isolation | "Multi-tenant requires isolation strategy" |
| Missing query routing | "Complex queries need agentic routing" |
| No PII detection | "Add PII detection in ingestion pipeline" |

## Document Processing Guidelines

### PDF Processing Decision Tree

```
PDF Document
    │
    ├─ Scanned/image-based? → OCR Pipeline (Tesseract/Textract)
    ├─ Complex tables? → LlamaParse or Docling
    ├─ Diagrams/charts? → Vision LLM description
    ├─ Multi-column layout? → Layout-aware parser
    └─ Simple text? → PyMuPDF / pypdfium2
```

### Parser Selection

| Parser | Accuracy | Speed | Tables | Images | Cost |
|--------|----------|-------|--------|--------|------|
| LlamaParse | 99% | Medium | Excellent | VLM | Paid |
| Docling (IBM) | 95% | Fast | Good | Yes | Free |
| Unstructured | 90% | Medium | Good | Yes | Free/Paid |
| PyMuPDF | 85% | Fast | Basic | No | Free |

### Multimodal Strategy

```python
# ✅ CORRECT: Text grounding for unified retrieval
class MultimodalProcessor:
    """Ground all modalities in text (2x faster, 6x cheaper)"""

    async def process_image(self, image_path: str) -> str:
        # Vision LLM description → text embedding
        return await self.vision_llm.describe(image_path)

    async def process_video(self, video_path: str) -> list[dict]:
        # Whisper transcription + key frame descriptions
        transcript = await self.whisper.transcribe(video_path)
        frames = self.extract_key_frames(video_path)
        return self.align_and_blend(transcript, frames)
```

## Security Checklist for RAG Systems

### Data Security
- [ ] Encryption at rest (vector store, cache, object storage)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Tenant data isolation (collection/namespace separation)
- [ ] PII detection and redaction in ingestion pipeline
- [ ] Document-level ACLs synced from source systems

### API Security
- [ ] JWT authentication with short expiration
- [ ] Rate limiting per tenant/user
- [ ] Input validation (max query length, injection prevention)
- [ ] Output filtering (prevent data leakage)
- [ ] Audit logging for all queries

### Compliance
- [ ] GDPR: Right to deletion, data portability
- [ ] SOC 2: Access controls, audit trails
- [ ] HIPAA: PHI handling, BAA with vendors
- [ ] AI Act (EU): Risk assessment, documentation

## Cost Optimization Strategies

### 1. Embedding Cost Reduction

```python
class EmbeddingOptimizer:
    """Route embeddings based on importance"""

    async def embed(self, texts: list[str], importance: str) -> list:
        if importance == "high":
            return await self._api_embed(texts, "text-embedding-3-large")
        elif importance == "normal":
            return await self._api_embed(texts, "text-embedding-3-small")
        else:
            return self._local_embed(texts)  # SentenceTransformers
```

### 2. Semantic Caching ROI

```
Without Cache:
- 10,000 queries/day × 2,000 tokens = ~$60/day

With Semantic Cache (60% hit rate):
- 4,000 LLM calls/day = ~$24/day
- Savings: 60% cost, 70% latency improvement
```

### 3. LLM Routing

```python
MODELS = {
    "simple": "claude-3-haiku",      # $0.25/1M input
    "medium": "claude-3-5-sonnet",   # $3/1M input
    "complex": "claude-sonnet-4",    # Better reasoning
}
```

## Observability Metrics

### Key Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Retrieval metrics
retrieval_latency = Histogram('rag_retrieval_latency_seconds')
retrieval_recall = Gauge('rag_retrieval_recall')

# Cache metrics
cache_hits = Counter('rag_cache_hits_total')
cache_misses = Counter('rag_cache_misses_total')

# Quality metrics
answer_relevance = Gauge('rag_answer_relevance')
faithfulness = Gauge('rag_faithfulness')
```

## Recommended Dependencies

```toml
[project]
dependencies = [
    # Core
    "fastapi>=0.109",
    "uvicorn[standard]>=0.27",

    # RAG Framework
    "llama-index>=0.10",
    "langchain>=0.2",
    "langgraph>=0.2",

    # Vector Store
    "qdrant-client>=1.9",
    "chromadb>=0.4",

    # Document Processing
    "llama-parse>=0.4",
    "docling>=1.0",
    "pymupdf>=1.24",
    "unstructured>=0.12",

    # Embeddings & Reranking
    "sentence-transformers>=2.5",
    "openai>=1.0",

    # Caching
    "redis>=5.0",
    "gptcache>=0.1",

    # Observability
    "langfuse>=2.0",
    "prometheus-client>=0.19",
]
```

## Integration with Other Skills

### Chunking Strategies (Deep-Dive)
For detailed chunking implementation, see the `chunking-strategies` skill:
- Document-type-specific patterns (code, legal, PDFs, tables)
- Strategy deep-dives (Semantic, RAPTOR, Late Chunking, Agentic)
- Evaluation metrics and A/B testing
- Production patterns and metadata enrichment

### MCP Security
When building MCP-based RAG servers:
- Apply 5-layer defense architecture
- Verify user context at retrieval
- Filter results by user permissions

### Privacy Compliance
When processing documents:
- PII detection before indexing
- Right to deletion support
- Data portability for exports

### Python/TypeScript Style
When implementing RAG pipelines:
- Follow type hints and Pydantic models
- Use async patterns for I/O operations
- Implement proper error handling

## Warning Triggers

Automatically warn user when:

1. **No tenant isolation in multi-tenant setup**
   > "RAG SECURITY: Multi-tenant systems require collection/namespace isolation"

2. **Direct embedding without caching**
   > "RAG COST: Semantic caching can reduce embedding costs by 60%+"

3. **Single chunking strategy for mixed documents**
   > "RAG QUALITY: Different document types need different chunking strategies"

4. **No reranking on retrieval**
   > "RAG PRECISION: Cross-encoder reranking improves relevance significantly"

5. **GraphRAG missing for global queries**
   > "RAG ARCHITECTURE: 'Summarize all' queries benefit from GraphRAG"

6. **No PII detection in ingestion**
   > "RAG COMPLIANCE: PII must be detected/redacted before indexing"

7. **Missing audit logging**
   > "RAG SECURITY: All queries and data access must be logged"

8. **No query complexity routing**
   > "RAG EFFICIENCY: Route simple queries to lighter models"
