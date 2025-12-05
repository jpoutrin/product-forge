---
name: Chunking Strategies
description: Deep-dive chunking patterns for RAG optimization with document-type-specific strategies and evaluation metrics
version: 1.0.0
triggers:
  - chunking
  - chunk
  - text splitting
  - document splitting
  - chunk size
  - chunk overlap
  - semantic chunking
  - late chunking
  - contextual chunking
  - agentic chunking
  - code chunking
  - pdf chunking
  - table extraction
  - recursive character
  - text splitter
---

# Chunking Strategies Skill

This skill provides deep technical guidance on document chunking for RAG systems. It complements the `rag-cag-security` skill with detailed implementation patterns and document-type-specific strategies.

## Core Principle

**Chunking quality directly determines retrieval quality. Match strategy to document type.**

```
CHUNKING IMPACT ON RAG
════════════════════════════════════════════════════════════════

Poor Chunking → Lost context → Irrelevant retrieval → Bad answers
Good Chunking → Preserved meaning → Accurate retrieval → Good answers

Key insight: A 10% improvement in chunking can yield 30%+ retrieval gains
```

## 1. Chunking Fundamentals

### Chunk Size vs. Retrieval Quality Tradeoffs

```
CHUNK SIZE SPECTRUM
════════════════════════════════════════════════════════════════

TOO SMALL (< 100 tokens)          TOO LARGE (> 1500 tokens)
├── High precision                 ├── Low precision
├── Lost context                   ├── Noise dilution
├── Fragmented ideas               ├── Multiple topics per chunk
└── Many chunks to search          └── Missed specific matches

SWEET SPOT: 200-800 tokens (depends on domain)
├── Complete thoughts
├── Sufficient context
├── Manageable search space
└── Good embedding representation
```

### Token Counting

```python
import tiktoken

# OpenAI models
def count_tokens_openai(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Approximate: 1 token ≈ 4 characters (English)
def estimate_tokens(text: str) -> int:
    return len(text) // 4

# For chunk sizing
def chunk_by_tokens(text: str, max_tokens: int = 500) -> list[str]:
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunks.append(encoding.decode(chunk_tokens))

    return chunks
```

### Overlap Strategies

```python
# Fixed overlap (character-based)
def fixed_overlap_chunks(text: str, size: int = 1000, overlap: int = 200):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

# Sentence-aware overlap (better semantic boundaries)
import re

def sentence_aware_overlap(text: str, size: int = 1000, overlap_sentences: int = 2):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        if current_size + len(sentence) > size and current_chunk:
            chunks.append(' '.join(current_chunk))
            # Keep last N sentences for overlap
            current_chunk = current_chunk[-overlap_sentences:]
            current_size = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_size += len(sentence)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
```

## 2. Strategy Deep-Dives

### Strategy 1: Fixed-Size (RecursiveCharacterTextSplitter)

The most common starting point. Recursively tries separators until chunks fit.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Standard configuration
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=[
        "\n\n",      # Paragraphs first
        "\n",        # Then lines
        ". ",        # Then sentences
        ", ",        # Then clauses
        " ",         # Then words
        ""           # Finally characters
    ],
    length_function=len,
    is_separator_regex=False,
)

chunks = splitter.split_documents(documents)

# Token-based (more accurate for LLMs)
from langchain.text_splitter import TokenTextSplitter

token_splitter = TokenTextSplitter(
    chunk_size=500,      # tokens, not characters
    chunk_overlap=50,
    encoding_name="cl100k_base"
)
```

**When to use**: Prototyping, homogeneous text, baseline comparison
**Limitations**: Ignores semantic boundaries, splits mid-thought

---

### Strategy 2: Semantic Chunking

Split based on embedding similarity changes between sentences.

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

class SemanticChunkerConfig:
    """Configuration for semantic chunking"""

    # Percentile: Split when similarity drops below threshold
    PERCENTILE = {
        "breakpoint_threshold_type": "percentile",
        "breakpoint_threshold_amount": 95,  # Top 5% drops = break
    }

    # Standard deviation: Split at statistical outliers
    STANDARD_DEV = {
        "breakpoint_threshold_type": "standard_deviation",
        "breakpoint_threshold_amount": 2,  # 2 std devs from mean
    }

    # Gradient: Detect sharp similarity changes
    GRADIENT = {
        "breakpoint_threshold_type": "gradient",
        "breakpoint_threshold_amount": 0.1,
    }

    # Interquartile: Use IQR for outlier detection
    INTERQUARTILE = {
        "breakpoint_threshold_type": "interquartile",
    }

# Production implementation
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

semantic_chunker = SemanticChunker(
    embeddings=embeddings,
    **SemanticChunkerConfig.PERCENTILE,
    buffer_size=1,  # Sentences to include around breakpoints
)

chunks = semantic_chunker.split_documents(documents)
```

**Threshold tuning**:
```python
def find_optimal_threshold(
    documents: list,
    thresholds: list[float] = [90, 92, 95, 97, 99],
    target_chunk_count: int = None
) -> float:
    """Find threshold that produces optimal chunk count"""
    results = []

    for threshold in thresholds:
        chunker = SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=threshold,
        )
        chunks = chunker.split_documents(documents)

        avg_size = sum(len(c.page_content) for c in chunks) / len(chunks)
        results.append({
            "threshold": threshold,
            "chunk_count": len(chunks),
            "avg_size": avg_size,
        })

    return results
```

**When to use**: Mixed-topic documents, complex prose, high-value content
**Cost**: Requires embedding API calls during chunking

---

### Strategy 3: Hierarchical Chunking (Parent-Child)

Store chunks at multiple granularities with relationships.

```python
from llama_index.core.node_parser import HierarchicalNodeParser
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core import StorageContext, VectorStoreIndex

# Create hierarchy: large → medium → small
parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128],  # Parent, child, leaf
)

nodes = parser.get_nodes_from_documents(documents)

# Build index with parent references
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)

index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
)

# Auto-merging retriever: if most children match, return parent
retriever = AutoMergingRetriever(
    index,
    storage_context=storage_context,
    simple_ratio_thresh=0.5,  # 50% children match → merge to parent
    verbose=True,
)

# Query returns parent if children cluster
results = retriever.retrieve("detailed query about topic")
```

**Visualization**:
```
Parent Chunk (2048 tokens)
├── Child Chunk 1 (512 tokens)
│   ├── Leaf 1a (128 tokens) ← Query matches
│   ├── Leaf 1b (128 tokens) ← Query matches
│   ├── Leaf 1c (128 tokens) ← Query matches
│   └── Leaf 1d (128 tokens)
├── Child Chunk 2 (512 tokens)
└── Child Chunk 3 (512 tokens)

Result: Return Child Chunk 1 (auto-merged from leaves)
```

**When to use**: Queries needing both detail and context, multi-resolution search

---

### Strategy 4: RAPTOR (Recursive Abstractive Tree)

Build a tree of increasingly abstract summaries.

```python
from typing import List
import numpy as np
from sklearn.mixture import GaussianMixture
from umap import UMAP

class RAPTORBuilder:
    """
    RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

    Level 0: Original chunks
    Level 1: Cluster summaries
    Level 2: Higher-level summaries
    Level 3: Executive summary
    """

    def __init__(
        self,
        embedding_model,
        summarizer_llm,
        max_levels: int = 3,
        min_cluster_size: int = 5,
    ):
        self.embedder = embedding_model
        self.summarizer = summarizer_llm
        self.max_levels = max_levels
        self.min_cluster_size = min_cluster_size

    def build_tree(self, chunks: List[str]) -> dict:
        """Build RAPTOR tree from leaf chunks"""
        tree = {0: chunks}
        current_level = chunks

        for level in range(1, self.max_levels + 1):
            if len(current_level) < self.min_cluster_size:
                break

            # Embed current level
            embeddings = self.embedder.embed(current_level)
            embeddings = np.array(embeddings)

            # Reduce dimensions with UMAP
            n_components = min(10, len(current_level) - 1)
            reduced = UMAP(
                n_components=n_components,
                metric='cosine'
            ).fit_transform(embeddings)

            # Determine optimal cluster count
            n_clusters = self._optimal_clusters(reduced)

            # Cluster similar content
            gmm = GaussianMixture(
                n_components=n_clusters,
                covariance_type='full',
                random_state=42
            )
            labels = gmm.fit_predict(reduced)

            # Group by cluster
            clusters = {}
            for idx, label in enumerate(labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(current_level[idx])

            # Summarize each cluster
            summaries = []
            for cluster_id, cluster_chunks in clusters.items():
                summary = self._summarize_cluster(cluster_chunks)
                summaries.append(summary)

            tree[level] = summaries
            current_level = summaries

        return tree

    def _optimal_clusters(self, embeddings: np.ndarray) -> int:
        """Find optimal cluster count using BIC"""
        max_clusters = min(len(embeddings) // 5, 20)
        best_bic = float('inf')
        best_n = 2

        for n in range(2, max_clusters + 1):
            gmm = GaussianMixture(n_components=n)
            gmm.fit(embeddings)
            bic = gmm.bic(embeddings)
            if bic < best_bic:
                best_bic = bic
                best_n = n

        return best_n

    def _summarize_cluster(self, chunks: List[str]) -> str:
        """Generate summary for a cluster of chunks"""
        combined = "\n\n---\n\n".join(chunks)
        prompt = f"""Summarize the following related content into a coherent summary.
Preserve key facts, entities, and relationships.
Keep the summary dense with information.

Content:
{combined}

Summary:"""
        return self.summarizer.generate(prompt)

    def create_collapsed_index(self, tree: dict) -> List[dict]:
        """Flatten tree for unified search across all levels"""
        all_nodes = []
        for level, nodes in tree.items():
            for node in nodes:
                all_nodes.append({
                    "text": node,
                    "level": level,
                    "type": "summary" if level > 0 else "chunk"
                })
        return all_nodes
```

**Search strategies**:
```python
class RAPTORRetriever:
    def tree_traversal(self, query: str, tree: dict, k: int = 5):
        """Top-down: Start from summaries, drill into details"""
        # Search highest level first
        top_level = max(tree.keys())
        matches = self.search(query, tree[top_level], k=3)

        # Drill down through matched branches
        for level in range(top_level - 1, -1, -1):
            # Find children of matched parents
            children = self.get_children(matches, tree[level])
            matches = self.search(query, children, k=k)

        return matches

    def collapsed_search(self, query: str, tree: dict, k: int = 5):
        """Search all levels simultaneously, merge results"""
        all_nodes = self.create_collapsed_index(tree)
        return self.search(query, all_nodes, k=k)
```

**When to use**: Long documents (books, reports), global/thematic queries, "summarize" requests
**Benchmark**: RAPTOR + GPT-4 improved QuALITY benchmark by 20%

---

### Strategy 5: Late Chunking (Contextual Embeddings)

Embed the full document first, then chunk the embeddings.

```python
from transformers import AutoModel, AutoTokenizer
import torch

class LateChunker:
    """
    Late Chunking: Embed first, chunk second

    Traditional: Document → Chunk → Embed (each chunk loses context)
    Late:        Document → Embed → Chunk (each chunk has full context)

    Key insight: "the city" in chunk 5 knows it refers to "Berlin"
    from chunk 1 because all tokens were embedded together.
    """

    def __init__(
        self,
        model_name: str = "jinaai/jina-embeddings-v2-base-en",
        max_length: int = 8192,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True
        )
        self.max_length = max_length

    def late_chunk(
        self,
        document: str,
        chunk_size: int = 512,
    ) -> list[tuple[str, list[float]]]:
        """
        1. Tokenize entire document
        2. Get token-level embeddings (with full context)
        3. Chunk the embeddings, not the text
        4. Mean pool each chunk
        """
        # Tokenize full document
        tokens = self.tokenizer(
            document,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True,
            return_offsets_mapping=True,
        )

        # Get token embeddings with full document context
        with torch.no_grad():
            outputs = self.model(
                input_ids=tokens["input_ids"],
                attention_mask=tokens["attention_mask"],
            )
            token_embeddings = outputs.last_hidden_state[0]

        # Find chunk boundaries in token space
        input_ids = tokens["input_ids"][0]
        boundaries = self._find_boundaries(input_ids, chunk_size)

        # Pool each chunk's embeddings
        chunks_with_embeddings = []
        for start, end in boundaries:
            # Decode chunk text
            chunk_tokens = input_ids[start:end]
            chunk_text = self.tokenizer.decode(
                chunk_tokens,
                skip_special_tokens=True
            )

            # Mean pool this chunk's contextual embeddings
            chunk_embedding = token_embeddings[start:end].mean(dim=0)

            chunks_with_embeddings.append((
                chunk_text,
                chunk_embedding.tolist()
            ))

        return chunks_with_embeddings

    def _find_boundaries(
        self,
        input_ids: torch.Tensor,
        chunk_size: int
    ) -> list[tuple[int, int]]:
        """Find chunk boundaries, preferring sentence ends"""
        boundaries = []
        start = 0

        # Token IDs for sentence endings (model-specific)
        sentence_end_tokens = self.tokenizer.encode(
            ". ! ?",
            add_special_tokens=False
        )

        while start < len(input_ids):
            end = min(start + chunk_size, len(input_ids))

            # Try to break at sentence boundary
            if end < len(input_ids):
                for i in range(end, start, -1):
                    if input_ids[i].item() in sentence_end_tokens:
                        end = i + 1
                        break

            boundaries.append((start, end))
            start = end

        return boundaries
```

**When to use**: Cross-references, pronouns, legal/technical docs with anaphora
**Requirement**: Long-context embedding model (8K+ tokens)

---

### Strategy 6: Agentic Chunking (LLM-Driven)

Let the LLM decide optimal boundaries.

```python
import json
from typing import List, Dict

class AgenticChunker:
    """
    Use LLM to determine semantically optimal chunk boundaries.
    Most expensive but highest quality for important documents.
    """

    def __init__(self, llm_client, max_context: int = 10000):
        self.llm = llm_client
        self.max_context = max_context

    async def chunk(self, document: str) -> List[Dict]:
        """Let LLM determine chunk boundaries"""

        # For long documents, process in windows
        if len(document) > self.max_context:
            return await self._chunk_long_document(document)

        prompt = f"""Analyze this document and identify semantically coherent chunks.

For each chunk, provide:
1. start_sentence: First few words of the chunk
2. end_sentence: Last few words of the chunk
3. title: Brief descriptive title (3-7 words)
4. entities: Key entities mentioned
5. summary: One-sentence summary
6. size: small (1-2 paragraphs), medium (section), large (chapter)

Guidelines:
- Keep related concepts together
- Don't split mid-argument or mid-example
- Respect natural document structure
- Ensure each chunk is self-contained

Document:
{document}

Respond with valid JSON array:
[{{"start_sentence": "...", "end_sentence": "...", "title": "...", "entities": [...], "summary": "...", "size": "..."}}]
"""

        response = await self.llm.generate(prompt)
        chunk_specs = json.loads(response)

        # Extract actual text based on LLM boundaries
        chunks = self._extract_chunks(document, chunk_specs)
        return chunks

    def _extract_chunks(
        self,
        document: str,
        specs: List[Dict]
    ) -> List[Dict]:
        """Extract chunk text based on LLM-identified boundaries"""
        chunks = []
        remaining = document

        for spec in specs:
            start_marker = spec["start_sentence"]
            end_marker = spec["end_sentence"]

            # Find boundaries in text
            start_idx = remaining.find(start_marker[:50])
            if start_idx == -1:
                continue

            # Search for end after start
            search_text = remaining[start_idx:]
            end_idx = search_text.find(end_marker[-50:])
            if end_idx == -1:
                end_idx = len(search_text)
            else:
                end_idx += len(end_marker[-50:])

            chunk_text = search_text[:end_idx]

            chunks.append({
                "text": chunk_text.strip(),
                "title": spec["title"],
                "entities": spec["entities"],
                "summary": spec["summary"],
                "size": spec["size"],
            })

            remaining = remaining[start_idx + end_idx:]

        return chunks
```

**When to use**: Legal contracts, compliance documents, high-value content
**Cost**: $0.01-0.10 per page (LLM API calls)

---

## 3. Document-Type Patterns

### Code (AST-Aware)

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

class CodeChunker:
    """Chunk code by AST structure, not text"""

    SIGNIFICANT_NODES = {
        "python": [
            "function_definition",
            "class_definition",
            "decorated_definition",
        ],
        "javascript": [
            "function_declaration",
            "class_declaration",
            "arrow_function",
            "method_definition",
        ],
        "typescript": [
            "function_declaration",
            "class_declaration",
            "interface_declaration",
            "type_alias_declaration",
        ],
    }

    def __init__(self, language: str = "python"):
        self.language = language
        self.parser = Parser()

        if language == "python":
            self.parser.set_language(Language(tspython.language(), "python"))

    def chunk(self, code: str) -> list[dict]:
        """Extract functions/classes as chunks with metadata"""
        tree = self.parser.parse(code.encode())
        chunks = []

        for node in self._walk_tree(tree.root_node):
            if node.type in self.SIGNIFICANT_NODES.get(self.language, []):
                chunk_text = code[node.start_byte:node.end_byte]

                # Extract metadata
                name = self._extract_name(node, code)
                docstring = self._extract_docstring(node, code)

                chunks.append({
                    "text": chunk_text,
                    "type": node.type,
                    "name": name,
                    "docstring": docstring,
                    "start_line": node.start_point[0],
                    "end_line": node.end_point[0],
                    "imports": self._get_imports(tree.root_node, code),
                })

        return chunks

    def _walk_tree(self, node):
        """Depth-first traversal"""
        yield node
        for child in node.children:
            yield from self._walk_tree(child)

    def _extract_name(self, node, code: str) -> str:
        """Extract function/class name"""
        for child in node.children:
            if child.type == "identifier":
                return code[child.start_byte:child.end_byte]
        return "unknown"

    def _extract_docstring(self, node, code: str) -> str:
        """Extract docstring if present"""
        for child in node.children:
            if child.type == "expression_statement":
                for grandchild in child.children:
                    if grandchild.type == "string":
                        return code[grandchild.start_byte:grandchild.end_byte]
        return ""
```

---

### Legal/Contracts

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class LegalChunk:
    text: str
    section_number: str
    section_title: str
    parent_section: Optional[str]
    cross_references: list[str]
    defined_terms: list[str]

class LegalChunker:
    """Clause-aware chunking for legal documents"""

    SECTION_PATTERNS = [
        r'^(\d+\.)+\s+([A-Z][^.]+)\.',           # 1.2.3 Title.
        r'^Section\s+(\d+)\.\s*(.+)',             # Section 1. Title
        r'^Article\s+([IVXLCDM]+)\.\s*(.+)',      # Article IV. Title
        r'^SCHEDULE\s+([A-Z])\s*[:\-]?\s*(.+)',   # SCHEDULE A: Title
    ]

    DEFINED_TERM_PATTERNS = [
        r'"([^"]+)"',                             # "Defined Term"
        r'\(the\s+"([^"]+)"\)',                  # (the "Term")
    ]

    def chunk(self, document: str) -> list[LegalChunk]:
        """Split legal document by sections while preserving structure"""
        sections = self._identify_sections(document)
        chunks = []

        for section in sections:
            # Extract cross-references
            xrefs = self._find_cross_references(section["text"])

            # Extract defined terms
            terms = self._find_defined_terms(section["text"])

            chunks.append(LegalChunk(
                text=section["text"],
                section_number=section["number"],
                section_title=section["title"],
                parent_section=section.get("parent"),
                cross_references=xrefs,
                defined_terms=terms,
            ))

        return chunks

    def _find_cross_references(self, text: str) -> list[str]:
        """Find references to other sections"""
        patterns = [
            r'Section\s+(\d+(?:\.\d+)*)',
            r'Article\s+([IVXLCDM]+)',
            r'Schedule\s+([A-Z])',
            r'Exhibit\s+([A-Z])',
        ]

        refs = []
        for pattern in patterns:
            refs.extend(re.findall(pattern, text))
        return refs

    def _find_defined_terms(self, text: str) -> list[str]:
        """Extract defined terms for glossary linking"""
        terms = []
        for pattern in self.DEFINED_TERM_PATTERNS:
            terms.extend(re.findall(pattern, text))
        return list(set(terms))
```

---

### PDFs (Complex)

```python
from llama_parse import LlamaParse
from docling.document_converter import DocumentConverter

class PDFChunker:
    """Handle complex PDFs with tables and images"""

    def __init__(self, parser: str = "llamaparse"):
        self.parser = parser

        if parser == "llamaparse":
            self.client = LlamaParse(
                result_type="markdown",
                parsing_instruction="""
                Extract all content including:
                - Tables as markdown tables
                - Images with detailed descriptions
                - Preserve headers and structure
                - Note page numbers for citations
                """,
                use_vendor_multimodal_model=True,
            )
        elif parser == "docling":
            self.client = DocumentConverter()

    async def chunk(self, pdf_path: str) -> list[dict]:
        """Parse and chunk PDF with structure preservation"""

        # Parse PDF to structured format
        if self.parser == "llamaparse":
            parsed = await self.client.aload_data(pdf_path)
            markdown = parsed[0].text
        else:
            result = self.client.convert(pdf_path)
            markdown = result.document.export_to_markdown()

        # Chunk by structure
        chunks = self._chunk_markdown(markdown)

        return chunks

    def _chunk_markdown(self, markdown: str) -> list[dict]:
        """Chunk markdown preserving tables and structure"""
        chunks = []
        current_chunk = []
        current_headers = []
        in_table = False
        table_content = []

        for line in markdown.split('\n'):
            # Track headers for context
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                current_headers = current_headers[:level-1] + [line.lstrip('#').strip()]

            # Handle tables as atomic units
            if line.startswith('|'):
                in_table = True
                table_content.append(line)
                continue
            elif in_table:
                # End of table
                chunks.append({
                    "text": '\n'.join(table_content),
                    "type": "table",
                    "headers": current_headers.copy(),
                })
                table_content = []
                in_table = False

            # Regular content
            current_chunk.append(line)

            # Check if chunk is large enough
            if len('\n'.join(current_chunk)) > 1000:
                chunks.append({
                    "text": '\n'.join(current_chunk),
                    "type": "text",
                    "headers": current_headers.copy(),
                })
                current_chunk = []

        # Handle remaining content
        if current_chunk:
            chunks.append({
                "text": '\n'.join(current_chunk),
                "type": "text",
                "headers": current_headers.copy(),
            })

        return chunks
```

---

### Tables/CSV

```python
import pandas as pd

class TableChunker:
    """Chunk tabular data with schema context"""

    def chunk(
        self,
        df: pd.DataFrame,
        rows_per_chunk: int = 50,
        include_schema: bool = True,
    ) -> list[dict]:
        """Convert table rows to chunks with column context"""

        # Generate schema description
        schema = self._describe_schema(df)

        chunks = []
        for i in range(0, len(df), rows_per_chunk):
            chunk_df = df.iloc[i:i + rows_per_chunk]

            # Convert rows to natural language
            chunk_text = self._rows_to_text(chunk_df, include_schema)

            chunks.append({
                "text": chunk_text,
                "type": "table_rows",
                "start_row": i,
                "end_row": min(i + rows_per_chunk, len(df)),
                "schema": schema if include_schema else None,
            })

        return chunks

    def _describe_schema(self, df: pd.DataFrame) -> str:
        """Generate natural language schema description"""
        descriptions = []
        for col in df.columns:
            dtype = df[col].dtype
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else "N/A"
            descriptions.append(f"- {col} ({dtype}): e.g., {sample}")

        return "Table columns:\n" + "\n".join(descriptions)

    def _rows_to_text(self, df: pd.DataFrame, include_schema: bool) -> str:
        """Convert rows to searchable text"""
        lines = []

        if include_schema:
            lines.append(self._describe_schema(df))
            lines.append("\nData rows:")

        for _, row in df.iterrows():
            row_text = ", ".join(f"{col}: {val}" for col, val in row.items())
            lines.append(row_text)

        return "\n".join(lines)
```

---

### Audio/Video Transcripts

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class TranscriptChunk:
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str]

class TranscriptChunker:
    """Chunk transcripts with timestamp alignment"""

    def chunk(
        self,
        transcript: list[dict],  # [{"text": "...", "start": 0.0, "end": 2.5, "speaker": "A"}]
        target_duration: float = 60.0,  # seconds
        respect_speaker_turns: bool = True,
    ) -> list[TranscriptChunk]:
        """Chunk transcript by time while respecting speaker turns"""

        chunks = []
        current_chunk = []
        current_start = transcript[0]["start"] if transcript else 0
        current_duration = 0
        current_speaker = None

        for segment in transcript:
            segment_duration = segment["end"] - segment["start"]

            # Check if we should start a new chunk
            new_chunk_needed = (
                current_duration + segment_duration > target_duration
                or (respect_speaker_turns
                    and current_speaker
                    and segment.get("speaker") != current_speaker)
            )

            if new_chunk_needed and current_chunk:
                chunks.append(TranscriptChunk(
                    text=" ".join(s["text"] for s in current_chunk),
                    start_time=current_start,
                    end_time=current_chunk[-1]["end"],
                    speaker=current_speaker,
                ))
                current_chunk = []
                current_start = segment["start"]
                current_duration = 0

            current_chunk.append(segment)
            current_duration += segment_duration
            current_speaker = segment.get("speaker")

        # Handle remaining
        if current_chunk:
            chunks.append(TranscriptChunk(
                text=" ".join(s["text"] for s in current_chunk),
                start_time=current_start,
                end_time=current_chunk[-1]["end"],
                speaker=current_speaker,
            ))

        return chunks
```

---

## 4. Evaluation & Optimization

### Retrieval Quality Metrics

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    context_recall,
    faithfulness,
    answer_relevancy,
)

async def evaluate_chunking_strategy(
    chunks: list[str],
    test_queries: list[str],
    ground_truth: list[str],
    retriever,
) -> dict:
    """Evaluate chunking quality via retrieval metrics"""

    results = []
    for query, truth in zip(test_queries, ground_truth):
        # Retrieve with current chunking
        retrieved = await retriever.retrieve(query, k=5)

        results.append({
            "query": query,
            "ground_truth": truth,
            "retrieved_contexts": [r.text for r in retrieved],
        })

    # RAGAS evaluation
    scores = evaluate(
        results,
        metrics=[
            context_precision,
            context_recall,
        ]
    )

    return {
        "context_precision": scores["context_precision"],
        "context_recall": scores["context_recall"],
        "avg_chunk_size": sum(len(c) for c in chunks) / len(chunks),
        "chunk_count": len(chunks),
    }
```

### A/B Testing Framework

```python
class ChunkingABTest:
    """Compare chunking strategies on real queries"""

    def __init__(self, strategies: dict[str, callable]):
        self.strategies = strategies
        self.results = {name: [] for name in strategies}

    async def run_test(
        self,
        documents: list[str],
        test_queries: list[dict],  # {"query": "...", "relevant_doc_ids": [...]}
        retriever_factory,
    ) -> dict:
        """Run A/B test across strategies"""

        for name, chunker in self.strategies.items():
            # Chunk documents
            chunks = chunker(documents)

            # Build retriever
            retriever = retriever_factory(chunks)

            # Evaluate on queries
            for test in test_queries:
                retrieved = await retriever.retrieve(test["query"], k=10)

                # Calculate recall@k
                retrieved_ids = {r.metadata["doc_id"] for r in retrieved}
                relevant_ids = set(test["relevant_doc_ids"])
                recall = len(retrieved_ids & relevant_ids) / len(relevant_ids)

                self.results[name].append({
                    "query": test["query"],
                    "recall@10": recall,
                    "latency_ms": retrieved.latency_ms,
                })

        return self._summarize_results()

    def _summarize_results(self) -> dict:
        """Aggregate results by strategy"""
        summary = {}
        for name, results in self.results.items():
            summary[name] = {
                "avg_recall@10": sum(r["recall@10"] for r in results) / len(results),
                "avg_latency_ms": sum(r["latency_ms"] for r in results) / len(results),
            }
        return summary
```

---

## 5. Production Patterns

### Hybrid Chunking Pipeline

```python
class HybridChunkingPipeline:
    """
    Production pipeline combining multiple strategies:
    1. Structure-aware first pass
    2. Semantic splitting for prose
    3. Specialized handling for code/tables
    4. RAPTOR for hierarchical index
    """

    def __init__(self):
        self.structure_parser = MarkdownParser()
        self.semantic_splitter = SemanticChunker()
        self.code_chunker = CodeChunker()
        self.table_chunker = TableChunker()
        self.raptor = RAPTORBuilder()

    async def process(self, document: str, doc_type: str) -> dict:
        # Step 1: Structure-aware parsing
        sections = self.structure_parser.parse(document)

        # Step 2: Route each section to appropriate chunker
        all_chunks = []
        for section in sections:
            if section.type == "code":
                chunks = self.code_chunker.chunk(section.content)
            elif section.type == "table":
                chunks = self.table_chunker.chunk(section.content)
            else:
                chunks = self.semantic_splitter.split(section.content)

            # Preserve section context
            for chunk in chunks:
                chunk["section_path"] = section.path

            all_chunks.extend(chunks)

        # Step 3: Build RAPTOR tree for hierarchical access
        raptor_tree = self.raptor.build_tree(
            [c["text"] for c in all_chunks]
        )

        return {
            "flat_chunks": all_chunks,
            "hierarchical_tree": raptor_tree,
            "metadata": {
                "doc_type": doc_type,
                "chunk_count": len(all_chunks),
                "raptor_levels": len(raptor_tree),
            }
        }
```

### Chunk Metadata Enrichment

```python
class ChunkEnricher:
    """Add searchable metadata to chunks"""

    async def enrich(self, chunk: dict) -> dict:
        text = chunk["text"]

        # Extract entities (lightweight NER)
        entities = await self.extract_entities(text)

        # Generate keywords
        keywords = await self.extract_keywords(text)

        # Classify topic
        topic = await self.classify_topic(text)

        # Estimate reading level
        reading_level = self.flesch_kincaid(text)

        return {
            **chunk,
            "entities": entities,
            "keywords": keywords,
            "topic": topic,
            "reading_level": reading_level,
            "token_count": self.count_tokens(text),
        }
```

---

## 6. Warning Triggers

Automatically warn when detecting:

1. **Single chunking strategy for mixed documents**
   > "CHUNKING: Different document types need different chunking strategies"

2. **No overlap in fixed-size chunking**
   > "CHUNKING: Add 10-20% overlap to preserve context across chunk boundaries"

3. **Chunk size > 2000 tokens**
   > "CHUNKING: Large chunks reduce retrieval precision - consider smaller sizes"

4. **Missing metadata preservation**
   > "CHUNKING: Preserve section headers and structure in chunk metadata"

5. **No evaluation metrics**
   > "CHUNKING: Measure retrieval recall to validate chunking strategy"

6. **Tables chunked as text**
   > "CHUNKING: Tables should be kept intact or converted with schema context"

7. **Code split mid-function**
   > "CHUNKING: Use AST-aware chunking for code to preserve function boundaries"

## Related Skills

- **rag-cag-security**: High-level RAG architecture (this skill provides the deep-dive on chunking)
- **python-style**: Python code patterns for implementation
- **documentation-research**: Research latest chunking papers before implementing
