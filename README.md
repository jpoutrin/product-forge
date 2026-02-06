# Product Forge

A comprehensive Claude Code marketplace plugin for product development, PRD management, task tracking, and secure technical implementation. Features CPO/CTO/Marketing/UX/DPO/DevOps/Data Engineering/RAG-CAG expertise with specialized technical agents (Django, FastAPI, FastMCP, React/TypeScript, Celery, Playwright) that research current documentation before coding. Includes design system management, cloud infrastructure (AWS, GCP, Ansible), data transformation (dbt, SQLMesh), RAG/CAG architecture with multi-tenant security, MCP security with 5-layer defense, OAuth/OIDC, and privacy compliance (GDPR/CCPA).

## Forge CLI Utilities

Product Forge includes a unified `forge` CLI tool for skill-related utilities:

### YouTube Transcript Fetcher

Fetch YouTube video transcripts as readable text files:

```bash
# Install with YouTube support
uv tool install . --with youtube-transcript-api

# Fetch transcript
forge youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
forge youtube "https://youtu.be/dQw4w9WgXcQ" --output transcripts/
forge youtube dQw4w9WgXcQ
```

### Feedback Management

Manage Product Forge learnings and feedback:

```bash
# Initialize learnings directory
forge feedback init

# Show statistics
forge feedback stats

# List feedback items
forge feedback list
forge feedback list --project product-forge
forge feedback list --type improvement

# Save feedback (used by hooks)
cat feedback.json | forge feedback save
```

**See [FORGE_CLI_IMPLEMENTATION_SUMMARY.md](FORGE_CLI_IMPLEMENTATION_SUMMARY.md) for complete CLI documentation.**

## Features

### Skills (Automatic Context Activation)

Skills automatically activate when Claude detects relevant context, providing expert guidance without explicit commands.

| Skill | Triggers | Description |
|-------|----------|-------------|
| **PRD Management** | prd, requirements | Automatic lifecycle management and organization |
| **Task Orchestration** | task, implement | Documentation-first execution with quality checks |
| **Product Strategy** | strategy, market | Chief Product Officer expertise with proven frameworks |
| **Documentation Research** | code, build, develop | Enforces online documentation research before implementation |
| **MCP Security** | mcp security, prompt injection, authorization | 5-layer defense architecture for multi-agent systems |
| **Design System** | design system, components, tokens | Build and reuse UI components, tokens, and patterns |
| **Python Style** | python, django, fastapi, celery | PEP standards, type hints, and modern Python patterns |
| **TypeScript Style** | typescript, react, node, eslint | Strict typing, ESLint, and modern TS/JS patterns |
| **Privacy Compliance** | gdpr, ccpa, privacy, data protection | GDPR, CCPA/CPRA, and regional compliance |
| **AWS Cloud** | aws, ec2, s3, lambda, iam | AWS services best practices and IAM security |
| **GCP Cloud** | gcp, gce, bigquery, cloud run | Google Cloud best practices and IAM security |
| **Ansible** | ansible, playbook, vault | Ansible automation for infrastructure |
| **OAuth** | oauth, oidc, jwt, pkce | OAuth 2.0 and OpenID Connect implementation |
| **dbt** | dbt, data transformation | dbt modeling, testing, and documentation |
| **SQLMesh** | sqlmesh, virtual environments | SQLMesh incremental models and CI/CD |
| **RAG/CAG Architecture** | rag, cag, vector database, embeddings | RAG/CAG patterns, chunking, multi-tenant security |
| **Chunking Strategies** | chunking, text splitting, semantic chunking | Document-type-specific chunking, RAPTOR, evaluation |

### Commands (Explicit User Actions)

Commands you invoke when you need specific functionality.

| Command | Usage | Description |
|---------|-------|-------------|
| `/create-prd` | `/create-prd my-product` | Interactive PRD creation wizard |
| `/create-prd-feature` | `/create-prd-feature auth` | Create feature-specific PRD |
| `/generate-tasks` | `/generate-tasks prd.md` | Convert PRD to task list |
| `/prd-status` | `/prd-status prd.md --set ACTIVE` | Check/update PRD status |
| `/list-prds` | `/list-prds --status ACTIVE` | List PRDs with metadata |
| `/task-list` | `/task-list --dir focus` | List tasks with progress |
| `/task-focus` | `/task-focus TASK-001` | Focus on specific task |
| `/discovery-session` | `/discovery-session my-product` | Start product discovery |
| `/create-persona` | `/create-persona developer` | Create user persona |
| `/position-product` | `/position-product my-product` | Define positioning |
| `/brainstorm-solution` | `/brainstorm-solution "problem"` | Structured brainstorming |
| `/prd-progress` | `/prd-progress prd.md` | Show implementation progress |
| `/prd-archive` | `/prd-archive prd.md` | Archive completed PRDs |
| `/quick-start` | `/quick-start` | Quick start guide |

### Agents (Complex Multi-Step Tasks)

Agents handle autonomous, multi-step workflows.

#### Leadership Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **product-architect** | Chief Product Officer | Discovery, strategy, roadmap, launch planning |
| **cto-architect** | Chief Technology Officer | System design, tech selection, team coordination |
| **marketing-expert** | Brand Strategist | Brand guidelines, messaging, go-to-market |
| **dpo-expert** | Data Protection Officer | GDPR/CCPA compliance, privacy audits, DPIA |

#### Design & Experience Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **ui-product-expert** | UI Specialist | UI guidelines, design tokens, visual QA (Playwright MCP) |
| **ux-expert** | UX Specialist | User research, usability testing, accessibility |

#### Product Management Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **prd-orchestrator** | PRD Lifecycle Manager | Create, validate, track, archive PRDs |
| **task-executor** | Task Implementation | Documentation-first execution, quality checks |

#### Infrastructure & DevOps Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **devops-expert** | DevOps Engineer | CI/CD, Terraform, Kubernetes, Docker, GitOps |
| **data-engineering-expert** | Data Engineer | dbt, SQLMesh, ELT pipelines, data quality |

#### AI/ML Agents

| Agent | Role | Capabilities |
|-------|------|--------------|
| **rag-cag-expert** | RAG/CAG Architect | RAG architecture, chunking, vector DBs, GraphRAG, semantic caching |

#### Technical Specialist Agents

All technical specialists **research online documentation** before implementation to ensure current best practices.

| Agent | Expertise | Key Capabilities |
|-------|-----------|------------------|
| **django-expert** | Python Django | Models, views, DRF, admin, authentication |
| **fastapi-expert** | Python FastAPI | Async APIs, Pydantic, OpenAPI, JWT |
| **fastmcp-expert** | Python FastMCP | MCP tools, resources, Claude integration |
| **react-typescript-expert** | React + TypeScript | Components, hooks, state, testing |
| **python-testing-expert** | pytest | Unit tests, integration, mocking, CI/CD |
| **celery-expert** | Python Celery | Task queues, async processing, scheduling |
| **playwright-testing-expert** | Playwright | E2E testing, visual regression, accessibility |
| **mcp-security-expert** | Multi-Agent Security | 5-layer defense, prompt injection, authorization |

## Agent Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LEADERSHIP LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  product-architect   cto-architect    marketing-expert    dpo-expert        │
│  (CPO)               (CTO)            (Brand)             (Privacy)         │
│  ├─ Strategy         ├─ Architecture  ├─ Brand Guidelines ├─ GDPR/CCPA     │
│  ├─ Market Analysis  ├─ Tech Select   ├─ Messaging        ├─ Privacy Audits│
│  └─ Roadmap          └─ Coordinates → └─ Go-to-Market     └─ DPIA          │
│                              │                                               │
└──────────────────────────────┼───────────────────────────────────────────────┘
                               │
     ┌─────────────────────────┼─────────────────────────┐
     │                         │                         │
     ▼                         ▼                         ▼
┌─────────────────┐ ┌───────────────────┐ ┌─────────────────────┐
│   DESIGN/UX     │ │  BACKEND          │ │  FRONTEND/QA        │
├─────────────────┤ ├───────────────────┤ ├─────────────────────┤
│                 │ │                   │ │                     │
│ ui-product-     │ │ django-expert     │ │ react-typescript-   │
│ expert          │ │ fastapi-expert    │ │ expert              │
│ ux-expert       │ │ fastmcp-expert    │ │ playwright-testing  │
│                 │ │ celery-expert     │ │ expert              │
│ Uses Playwright │ │                   │ │                     │
│ MCP for QA      │ │                   │ │                     │
└─────────────────┘ └───────────────────┘ └─────────────────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       │                       │                       │
       ▼                       ▼                       ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────┐
│ INFRASTRUCTURE   │ │  DATA            │ │  AI/ML               │
├──────────────────┤ ├──────────────────┤ ├──────────────────────┤
│                  │ │                  │ │                      │
│ devops-expert    │ │ data-engineering │ │ rag-cag-expert       │
│ ├─ CI/CD         │ │ expert           │ │ ├─ RAG Architecture  │
│ ├─ Terraform     │ │ ├─ dbt           │ │ ├─ Chunking          │
│ ├─ Kubernetes    │ │ ├─ SQLMesh       │ │ ├─ Vector DBs        │
│ └─ AWS/GCP       │ │ └─ Data Quality  │ │ └─ GraphRAG          │
└──────────────────┘ └──────────────────┘ └──────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌──────────────────────┐    ┌──────────────────────┐
    │  SECURITY            │    │  TESTING             │
    ├──────────────────────┤    ├──────────────────────┤
    │                      │    │                      │
    │ mcp-security-expert  │    │ python-testing-expert│
    │ ├─ 5-layer defense   │    │ ├─ pytest            │
    │ ├─ Prompt injection  │    │ ├─ Mocking           │
    │ └─ Authorization     │    │ └─ Coverage          │
    └──────────────────────┘    └──────────────────────┘

              🔬 ALL SPECIALISTS RESEARCH DOCS FIRST 🔬
```

## Documentation-First Approach

All technical specialists follow a strict documentation-first approach:

```
Before ANY implementation:

1. SEARCH official documentation online
2. READ current best practices
3. IDENTIFY deprecated patterns
4. REPORT findings to user
5. PROCEED with implementation

Example output:
┌────────────────────────────────────────────┐
│ Documentation Research Summary              │
├────────────────────────────────────────────┤
│ Technology: Django 5.0                      │
│                                            │
│ CURRENT BEST PRACTICES                     │
│ * Use AbstractUser for custom users        │
│ * Define AUTH_USER_MODEL early             │
│                                            │
│ DEPRECATED PATTERNS                        │
│ * Profile model extension (legacy)         │
│                                            │
│ SOURCE: docs.djangoproject.com             │
└────────────────────────────────────────────┘
```

## MCP Security: 5-Layer Defense Architecture

For MCP servers, multi-agent systems, and text-to-SQL pipelines, the plugin enforces a 5-layer defense architecture:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 1: INPUT GUARDRAILS          ┃
┃ * Rate limiting  * Length limits   ┃
┃ * Injection detection (ML+regex)   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 2: AUTHORIZATION GATE        ┃
┃ * User→Role mapping  * RBAC/ABAC  ┃
┃ * Schema filtering before agent    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 3: SQL VALIDATION            ┃
┃ * AST parsing  * DDL/DML blocklist ┃
┃ * Table allowlist  * RLS injection ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 4: EXECUTION SANDBOX         ┃
┃ * Read-only conn  * Timeout        ┃
┃ * Cost limits  * Row limits        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
           │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Layer 5: OUTPUT GUARDRAILS         ┃
┃ * PII masking  * Audit logging     ┃
┃ * Result limits  * SIEM export     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Core Principle**: Security is NOT a peer agent. Security is INFRASTRUCTURE.

```
BAD: Security Agent (can be prompt-injected)
GOOD: Security Guardrails (deterministic, cannot be "convinced")
```

The `mcp-security` skill automatically activates and warns when detecting:
- User input going directly to LLM without validation
- Generated SQL without proper validation
- Agents trusting previous agent's authorization checks
- Mutable or unsigned user context
- Missing audit logging

## Installation

### From Claude Code Marketplace

```bash
/plugin marketplace add jpoutrin/product-forge
```

### Manual Installation

Clone the repository to your Claude Code plugins directory:

```bash
git clone https://github.com/jpoutrin/product-forge.git ~/.claude/plugins/product-forge
```

## Quick Start

### 1. Product Planning (CPO Path)

```bash
# Full discovery session with CPO guidance
/discovery-session my-awesome-product

# Or quick PRD creation
/create-prd my-awesome-product
```

### 2. Technical Architecture (CTO Path)

The CTO agent will:
- Design system architecture
- Select appropriate technologies
- Delegate to specialist agents
- Coordinate implementation

### 3. Implementation

Technical specialists work with documentation research:

```bash
# Django web application
→ django-expert researches docs.djangoproject.com
→ Implements with current best practices

# FastAPI microservice
→ fastapi-expert researches fastapi.tiangolo.com
→ Implements with Pydantic V2 patterns

# React frontend
→ react-typescript-expert researches react.dev
→ Implements with React 18 patterns

# Testing
→ python-testing-expert ensures 80%+ coverage
```

### 4. Infrastructure & DevOps

```bash
# DevOps expert handles CI/CD and infrastructure
→ devops-expert configures GitHub Actions
→ Sets up Terraform for AWS/GCP
→ Deploys to Kubernetes

# Data pipelines with dbt/SQLMesh
→ data-engineering-expert designs data models
→ Implements incremental transformations
→ Sets up data quality tests
```

### 5. Task Tracking

```bash
# Generate tasks from PRD
/generate-tasks my-awesome-product-prd.md

# List and track progress
/task-list

# Focus on specific task
/task-focus TASK-001
```

## Plugin Structure

```
product-forge/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata (v1.0.0)
├── commands/ (14 commands)      # Slash commands
│   ├── create-prd.md
│   ├── discovery-session.md
│   └── ...
├── skills/ (17 skills)          # Auto-activating context
│   ├── prd-management/
│   ├── task-orchestration/
│   ├── product-strategy/
│   ├── documentation-research/
│   ├── mcp-security/            # 5-layer defense
│   ├── design-system/           # Component library
│   ├── python-style/            # Python code style
│   ├── typescript-style/        # TypeScript code style
│   ├── privacy-compliance/      # GDPR/CCPA
│   ├── aws-cloud/               # AWS best practices
│   ├── gcp-cloud/               # GCP best practices
│   ├── ansible/                 # Ansible automation
│   ├── oauth/                   # OAuth 2.0/OIDC
│   ├── dbt/                     # dbt transformation
│   ├── sqlmesh/                 # SQLMesh patterns
│   ├── rag-cag-security/        # RAG/CAG architecture
│   └── chunking-strategies/     # Document chunking deep-dive
├── agents/ (19 agents)          # Multi-step workflows
│   ├── product-architect.md     # CPO
│   ├── cto-architect.md         # CTO
│   ├── marketing-expert.md      # Brand strategy
│   ├── dpo-expert.md            # Privacy/GDPR
│   ├── ui-product-expert.md     # UI guidelines
│   ├── ux-expert.md             # User experience
│   ├── devops-expert.md         # CI/CD, Infrastructure
│   ├── data-engineering-expert.md # dbt, SQLMesh, pipelines
│   ├── rag-cag-expert.md        # RAG/CAG architecture
│   ├── prd-orchestrator.md
│   ├── task-executor.md
│   ├── django-expert.md
│   ├── fastapi-expert.md
│   ├── fastmcp-expert.md
│   ├── celery-expert.md         # Task queues
│   ├── react-typescript-expert.md
│   ├── playwright-testing-expert.md # E2E testing
│   ├── python-testing-expert.md
│   └── mcp-security-expert.md
├── templates/                   # Document templates
├── processes/                   # Process documentation
└── README.md
```

## When to Use What

| Need | Use | Why |
|------|-----|-----|
| Plan a new product | `product-architect` agent | CPO expertise for strategy |
| Design system architecture | `cto-architect` agent | CTO expertise + delegates to specialists |
| Create brand guidelines | `marketing-expert` agent | Brand strategy and messaging |
| Ensure privacy compliance | `dpo-expert` agent | GDPR/CCPA expertise |
| Design UI guidelines | `ui-product-expert` agent | Design tokens, component specs |
| Plan user experience | `ux-expert` agent | Research, journey mapping, usability |
| Build Django web app | `django-expert` agent | Researches Django docs first |
| Build FastAPI service | `fastapi-expert` agent | Researches FastAPI docs first |
| Build React frontend | `react-typescript-expert` agent | Researches React docs first |
| Create MCP server | `fastmcp-expert` agent | Researches MCP protocol first |
| Add background tasks | `celery-expert` agent | Task queues and scheduling |
| Set up CI/CD pipelines | `devops-expert` agent | GitHub Actions, Terraform, K8s |
| Build data pipelines | `data-engineering-expert` agent | dbt, SQLMesh, data quality |
| Design RAG/CAG systems | `rag-cag-expert` agent | Chunking, vector DBs, multi-tenant |
| Write E2E tests | `playwright-testing-expert` agent | Visual regression, accessibility |
| Write unit tests | `python-testing-expert` agent | pytest expertise |
| Secure multi-agent system | `mcp-security-expert` agent | 5-layer defense architecture |
| Implement OAuth/OIDC | Use `oauth` skill | Authorization Code + PKCE |
| Deploy to AWS | Use `aws-cloud` skill | IAM, EC2, S3, Lambda patterns |
| Deploy to GCP | Use `gcp-cloud` skill | IAM, Cloud Run, BigQuery patterns |
| Automate infrastructure | Use `ansible` skill | Playbooks, roles, vault |
| Build RAG pipelines | Use `rag-cag-security` skill | Architecture, chunking, security |
| Create a PRD | `/create-prd` command | Interactive wizard |
| Track tasks | `/task-list` command | Visual progress |

## Key Concepts

### CTO Orchestration

The CTO agent coordinates technical specialists:

```
User: "Build a task management API"

cto-architect:
1. Designs architecture (FastAPI + PostgreSQL)
2. Delegates API implementation → fastapi-expert
3. Delegates testing → python-testing-expert
4. Delegates CI/CD → devops-expert
5. Reviews integration
6. Ensures quality standards
```

### Documentation Research Enforcement

Technical specialists MUST research before coding:

```
django-expert receives task

STEP 1: Research
→ WebSearch("Django 5.0 [topic] best practices")
→ WebFetch("https://docs.djangoproject.com/...")
→ Report findings

STEP 2: Implement
→ Follow documented patterns
→ Avoid deprecated APIs
→ Reference docs in comments
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Credits

Based on [claude-blueprint](https://github.com/jpoutrin/claude-blueprint) CLI tool.

Inspired by:
- [claude-code-templates](https://github.com/davila7/claude-code-templates)
- [claude-code-plugins-plus](https://github.com/jeremylongshore/claude-code-plugins-plus)
