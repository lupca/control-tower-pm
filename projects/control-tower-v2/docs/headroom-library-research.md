# CTV2-063: Research Report — Headroom Library Evaluation

> **Task ID**: CTV2-063  
> **Target Library**: [Headroom (`headroomlabs-ai/headroom`)](https://github.com/headroomlabs-ai/headroom)  
> **Target Project**: [[projects/control-tower-v2/control-tower-v2]] (LangGraph + FastAPI + PostgreSQL Stack)  
> **Date**: 2026-07-27  
> **Author**: @antigravity  

---

## 1. Overview & Core Concepts

[Headroom](https://github.com/headroomlabs-ai/headroom) is an open-source, local-first context optimization and compression layer designed for AI agents and LLM applications. Its core objective is to compress tool outputs, database results, file reads, logs, and conversation histories before sending them to LLM providers (Anthropic, OpenAI, etc.), achieving 60–95% token savings on structured data and 15–20% on coding agent workloads without degrading output quality.

### 1.1 Architecture & The 3-Stage Pipeline
Every request processed by Headroom passes through a three-stage compression pipeline:

```
┌─────────────────┐      ┌─────────────────┐      ┌────────────────────┐
│  CacheAligner   │ ───► │  ContentRouter  │ ───► │ IntelligentContext │
│                 │      │                 │      │                    │
│ Stabilizes      │      │ Auto-detects    │      │ Scores messages &  │
│ static prefixes │      │ type & routes   │      │ prunes low-value   │
│ for KV caching  │      │ to compressor   │      │ turns under budget │
└─────────────────┘      └─────────────────┘      └────────────────────┘
```

1. **CacheAligner**: Extracts dynamic parameters (timestamps, user IDs) from system prompts to keep the static prefix invariant. This maximizes provider KV cache hit rates (e.g., Anthropic/OpenAI prompt caching).
2. **ContentRouter**: Uses pattern matching and ML (via Magika) to detect payload types and route them to content-aware compressors:
   - **SmartCrusher**: Statistical JSON and array compressor. Retains schema (first $N$ items), recency (last $N$ items), anomalies/errors, and statistical properties using the Kneedle algorithm (70–90% savings).
   - **CodeAwareCompressor**: AST-aware compressor powered by tree-sitter (supports 8 languages). Preserves imports, function signatures, and type annotations while compressing bodies.
   - **LogCompressor**: Tailored for build and test output (85–95% savings), isolating stack traces, errors, and status markers.
   - **SearchCompressor & DiffCompressor**: Filters for `grep` results and unified diffs.
   - **TextCompressor / Kompress-v2-base**: Small ML model (`chopratejas/kompress-v2-base`) for general prose compression.
   - **ImageCompressor**: ML router for vision tokens (40–90% savings).
3. **IntelligentContext (Context Management)**: Evaluates conversation history across six scoring dimensions (recency, semantic similarity to user prompt, TOIN importance, error indicators, forward references, token density) and prunes lowest-ranked turns when exceeding context budgets.

### 1.2 Key Features & Mechanisms
- **Compress-Cache-Retrieve (CCR / Reversible Compression)**: When Headroom compresses tool output or prunes older messages, it caches the original uncompressed text in a local CCR store. Headroom injects a `headroom_retrieve(hash)` tool into the prompt so the LLM can fetch the exact raw data on demand. This makes aggressive compression completely lossless.
- **Output Token Reduction (Verbosity Steering & Effort Routing)**: 
  - *Verbosity Steering*: Appends a concise instruction to system prompts instructing the model to avoid preamble/restating context.
  - *Effort Routing*: Dynamically adjusts reasoning effort (`thinking.budget_tokens` / `reasoning_effort`) downward when a turn is a simple tool resumption (e.g., file read confirmation), while preserving full effort for user queries or errors.
- **Deployment Modes**:
  - *Library*: Inline call `from headroom import compress` or `import { compress } from 'headroom-ai'`.
  - *Proxy Server*: `headroom proxy --port 8787` (transparent proxy for OpenAI/Anthropic SDKs with zero code changes).
  - *Agent Wrap*: `headroom wrap claude|codex|grok` for CLI coding agents.
  - *Framework Integrations*: LangChain (`HeadroomChatModel`, `HeadroomChatMessageHistory`, `HeadroomDocumentCompressor`), Agno, LiteLLM, MCP Server (`headroom_compress`, `headroom_retrieve`).

---

## 2. Evaluation Criterion 1: Token Consumption Reduction

### 2.1 Compression Mechanisms
Headroom reduces token usage across three distinct vectors:
1. **Input Payloads (Tool Outputs & Logs)**: Structural pruning of JSON arrays (SmartCrusher), log deduplication (LogCompressor), and diff truncation.
2. **Context History (IntelligentContext)**: Scoring-based message eviction rather than simple rolling-window truncation.
3. **Output Generation (Shaper)**: Steering output verbosity and clamping reasoning tokens on routine execution steps.

### 2.2 Benchmark Evidence & Real-world Workloads
According to Headroom's official benchmarks (measured on v0.5.18, 50,000+ proxy sessions across 250+ instances):

- **Structured Data / JSON Arrays**:
  - 100-item JSON array: **90.6% reduction** (3,163 tokens $\rightarrow$ 297 tokens, 1ms latency).
  - 500-item JSON array: **83.1% reduction** (9,526 tokens $\rightarrow$ 1,614 tokens, 2ms latency).
- **Log / Shell Output**:
  - 200-line build log: **93.9% reduction** (2,412 tokens $\rightarrow$ 148 tokens, 1ms latency).
  - SRE incident debugging workflow: **92% reduction** (65,694 tokens $\rightarrow$ 5,118 tokens).
- **Agent Workloads**:
  - Code search (100 results): **92% reduction** (17,765 tokens $\rightarrow$ 1,408 tokens).
  - GitHub issue triage: **73% reduction** (54,174 tokens $\rightarrow$ 14,761 tokens).
  - Codebase exploration: **47% reduction** (78,502 tokens $\rightarrow$ 41,254 tokens).

### 2.3 Limits & Constraints (When Token Savings Do NOT Apply)
As documented in [Headroom Limitations](https://headroom-docs.vercel.app/docs/limitations):
- **Short Messages (<300 tokens)**: Silently skipped because compression overhead exceeds token savings (median compression on short conversational exchanges is only **4.8%**).
- **Source Code Files**: Code mostly passes through unchanged due to built-in safety protections (`protect_analysis_context=True`, `protect_recent_code=4`). Stripping function bodies often breaks coding task accuracy, so Headroom leaves code intact unless explicitly overridden.
- **Already-compact grep/search results**: Show 0% compression because line-oriented matches are already high-entropy.

---

## 3. Evaluation Criterion 2: Task Output Quality

### 3.1 Context Quality & Relevance Mechanisms
1. **Noise Reduction & Attention Retention**: By compressing massive JSON payloads and repetitive build logs, Headroom eliminates "needle-in-a-haystack" distractions, helping LLMs focus on high-priority signals (error codes, stack traces, key schema attributes).
2. **Multi-dimensional Importance Scoring**: `IntelligentContext` ranks past messages using recency, semantic relevance to the active prompt, TOIN learned patterns, and error indicators, ensuring critical instructions remain in context while stale steps are evicted.
3. **Lossless Safety via CCR**: Traditional lossy compression risks stripping vital details. CCR guarantees that if an LLM requires full original context, it invokes `headroom_retrieve(hash)` to pull the original data, ensuring zero permanent information loss.

### 3.2 Accuracy Benchmarks
Benchmark evaluations demonstrate that Headroom preserves accuracy across standardized model evaluation suites:

| Benchmark | Domain | Baseline | Headroom | Delta / Accuracy | Notes |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **GSM8K** | Math Reasoning | 0.870 | 0.870 | **±0.000** | Zero accuracy degradation |
| **TruthfulQA** | Factual QA | 0.530 | 0.560 | **+0.030** | Slight gain due to noise reduction |
| **SQuAD v2** | Reading Comp. | — | **97%** | — | 19% context compression |
| **BFCL** | Tool Calling | — | **97%** | — | 32% context compression |
| **Log Error Triage** | Production Logs | 4/4 | **4/4** | **0 loss** | 87.6% compression (10,144 $\rightarrow$ 1,260 tokens) |

---

## 4. Integration Assessment with `control-tower-v2`

### 4.1 `control-tower-v2` Current Architecture
- **Tech Stack**: FastAPI (`:8000`), Python 3.12+, PostgreSQL, LangGraph `StateGraph`.
- **Workflow Gates**: `spec_gate`, `plan_gate`, `dispatch_gate`, `review_order_gate`, `verdict_gate`.
- **Existing Token Efficiency**: Control Tower V2 was explicitly designed to replace unconstrained Claude Code CLI spawner loops with deterministic Python state machines. By executing commands, gate checks, routing, and DB operations in zero-token Python code, V2 ALREADY achieves an **~84% token reduction** over V1 (reducing token consumption from ~25k to ~4k tokens per task).

### 4.2 Compatibility Matrix
- **Python Native Stack**: Headroom provides a native Python SDK (`pip install headroom-ai`), making it directly importable inside FastAPI routes and LangGraph nodes.
- **LangChain Integration**: `headroom-ai[langchain]` includes `HeadroomChatModel`, `HeadroomChatMessageHistory`, and `HeadroomDocumentCompressor`, which align directly with LangGraph's message handling and retriever components.

### 4.3 Overhead & Performance Considerations
- **SDK Latency Overhead**: The median Python SDK pipeline latency is **16.9ms** (P90: 289ms). On JSON array compression (100–500 items), compression takes 189ms–943ms.
- **Proxy Overhead**: Proxy median latency overhead is **52ms** (P90: 309ms).
- **Resource Footprint**: Enabling full text ML compression (`Kompress-v2-base` ONNX/PyTorch or `Magika`) requires additional RAM and local model initialization.

---

## 5. Recommendation: NEEDS MORE EVALUATION / SELECTIVE USE

### 5.1 Final Verdict
> **RECOMMENDATION**: **NEEDS MORE EVALUATION / SELECTIVE USE**  
> *Do NOT adopt Headroom as a global proxy or mandatory wrapper for all LLM calls. DO adopt Headroom selectively for high-volume MCP/repo query payload compression and long session chat history.*

### 5.2 Rationale
1. **Diminishing Returns on Short Gate Prompts**: Control Tower V2 gate prompts (`spec_gate`, `plan_gate`) pass structured short-to-medium text prompts (500–2,000 tokens). Headroom's benchmarks confirm that short messages (<300 tokens) yield **<5% compression**, while source code passes through untouched by default.
2. **Existing 84% Token Optimization**: Control Tower V2 already reduced token usage by ~84% via LangGraph state graph routing. Adding a global Headroom proxy layer introduces proxy latency (~52ms–300ms) and operational complexity with minimal incremental token savings for standard gate execution.
3. **High Value in Specific Sub-systems**: Headroom excels at compressing large JSON payloads from external tools (e.g., `code-review-graph` MCP server returns, large vector search results, or multi-turn interactive chat sessions).

---

## 6. Proposed Integration Points & Implementation Roadmap

If selective integration is approved, Headroom should be integrated into `control-tower-v2` at two specific touchpoints:

### Integration Point 1: MCP & Code Search Result Compressor (Plan & Spec Gates)
When `plan_gate` or `spec_gate` queries the `code-review-graph` MCP server or retrieves database/file search results, wrap the JSON payload with `headroom.compress()` before formatting the system prompt.

```python
# backend/app/core/context_compressor.py
from headroom.compression import compress

def compress_mcp_output(raw_json_data: str) -> str:
    """Compresses large MCP tool responses (JSON arrays, search hits) before prompt construction."""
    if len(raw_json_data) < 1000:
        return raw_json_data
    
    result = compress(raw_json_data)
    return result.compressed
```

### Integration Point 2: Session Chat History Compression (`sessions` table)
For multi-turn chat sessions in Chainlit / FastAPI chat router, use `HeadroomChatMessageHistory` to enforce a sliding context budget without dropping critical initial instructions.

```python
# backend/app/services/chat_service.py
from langchain_community.chat_message_histories import ChatMessageHistory
from headroom.integrations import HeadroomChatMessageHistory

def get_compressed_session_history(session_id: str, base_history: ChatMessageHistory):
    return HeadroomChatMessageHistory(
        base_history,
        compress_threshold_tokens=4000,
        keep_recent_turns=5,
    )
```

---

## 7. Summary & Verification Check

| Acceptance Criteria (AC) | Status | Evidence / Reference in Document |
| :--- | :---: | :--- |
| **1. Summary of README & Core Concepts** | Completed | Section 1 (3-stage pipeline, CCR, shaper, interfaces) |
| **2. Token Reduction Evaluation** | Completed | Section 2 (SmartCrusher, LogCompressor, 83-94% JSON benchmarks, limitations) |
| **3. Task Quality Evaluation** | Completed | Section 3 (GSM8K ±0.0, TruthfulQA +0.03, SQuAD 97%, BFCL 97%, CCR losslessness) |
| **4. LangGraph + FastAPI Integration** | Completed | Section 4 (Compatibility with Python stack, LangChain wrappers, performance overhead) |
| **5. Clear Recommendation** | Completed | Section 5 (**NEEDS MORE EVALUATION / SELECTIVE USE** with detailed rationale) |
| **6. Integration Points Proposal** | Completed | Section 6 (MCP tool output compressor & Session Chat History integration) |
