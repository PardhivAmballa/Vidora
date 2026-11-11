# System Architecture and Design Documentation

## 1. System Overview
Vidora acts as a controlled integration layer between an MCP-capable conversational AI client and YouTube's official Data API v3. The architecture isolates external API dependencies behind a provider interface, enforces strict server-side validation and quota pre-flight checks, and maintains an Obsidian Second Brain for knowledge traceability.

---

## 2. System Component Diagram & Responsibilities

The architecture is divided into clear functional boundaries:

[ User ]
│ (Natural Language Intent)
▼
[ MCP Client ] (Claude / Gemini / ChatGPT)
│ (MCP Tool Request / JSON-RPC over stdio)
▼
[ Vidora MCP Server ] (src/server.py)
├── Input Validation Middleware (NFR-SEC-5)
├── Quota & Pre-flight Accounting (NFR-PERF-2)
└── Confirmation Gate Controller (FR-5)
│
├──────────────────────────────┐
▼                              ▼
[ YouTube Provider Adapter ]    [ Local Analysis Engine ]
(src/provider.py)             (src/similarity.py)
│                              │
▼                              ▼
[ YouTube Data API v3 ]         [ scikit-learn TF-IDF ]
(External HTTPS API)            (Cosine Similarity Scoring)

### Component Responsibilities:
* **MCP Client:** Conversational interface that collects user intent, renders structured results, and presents playlist proposals for explicit confirmation.
* **Vidora MCP Server (`src/server.py`):** Exposes tools, registers handlers, validates incoming arguments, enforces security policies, and coordinates workflow execution.
* **YouTube Provider Adapter (`src/provider.py`):** Encapsulates calls to the official YouTube Data API v3, isolating external API mechanics and error handling.
* **Metadata Analysis Engine (`src/similarity.py`):** Computes TF-IDF feature matrices and cosine similarity locally over retrieved metadata.
* **Quota & Cache Service:** Pre-flights API cost estimations against remaining daily budgets and optionally caches responses using SQLite.