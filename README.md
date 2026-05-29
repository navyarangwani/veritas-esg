
# 🌿 Veritas ESG — Autonomous Greenwashing Detection Agent

An enterprise-grade agentic AI system that autonomously verifies ESG (Environmental, Social, Governance) claims in corporate sustainability reports against external evidence.

> *Veritas* — Latin for *truth*

---

## 🎯 Problem Statement

Companies publish ESG reports with measurable sustainability claims. These claims are rarely independently verified. Greenwashing — making misleading sustainability claims — is a growing concern for investors, regulators, and audit firms. This system automates the verification process using agentic AI.

---

## 🏗️ Architecture

### 2-Layer System Design

**Layer 1 — Document Intelligence**
Converts raw ESG PDF into structured, machine-readable claim objects.

**Layer 2 — Agentic Verification**
Autonomously verifies each claim using a ReAct reasoning loop.

### 5-Brain Design

| Brain | Responsibility | File |
|-------|---------------|------|
| Brain 1 | PDF Ingestion + Cleaning | `pdf_parser.py`, `cleaner.py` |
| Brain 2 | Claim Extraction + Normalization | `claim_extractor.py`, `chunker.py` |
| Brain 3 | Verification Strategy Planning | `strategy_brain.py` |
| Brain 4 | Evidence Retrieval | `evidence_brain.py` |
| Brain 5 | Judgment + Confidence Scoring | `judgment_brain.py` |

### ReAct Agent Loop
```
THINK → PLAN → ACT → OBSERVE → ANALYZE → JUDGE
```
The agent autonomously decides what to search for based on each claim's content. This dynamic planning — not hardcoded search queries — is what makes the system genuinely agentic.

---

## 🔍 What It Does

1. Upload any corporate ESG/sustainability/CSR report (PDF)
2. Extracts all measurable ESG claims — emissions, energy, water, waste, diversity
3. For each claim, the agent plans a verification strategy
4. Searches for independent external evidence using Tavily
5. Judges each claim as **Verified**, **Unverified**, or **Contradicted**
6. Generates confidence scores and audit reasoning
7. Renders a color-coded dashboard with evidence sources

---

## 💻 Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Groq API — Llama 3.3 70B |
| Agent Framework | LangChain ReAct |
| Search | Tavily API |
| PDF Parsing | PyMuPDF |
| Frontend | Streamlit |
| Hosting | Streamlit Community Cloud |

**Total cost: ₹0** — entirely free tier

---

## 🚀 Run Locally

```bash
git clone https://github.com/navyarangwani/veritas-esg.git
cd veritas-esg
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

```bash
streamlit run app.py
```

---

## 📁 File Structure

```
veritas-esg/
├── app.py                      # Streamlit dashboard
├── requirements.txt
└── utils/
    ├── pdf_parser.py           # Brain 1 — PDF extraction
    ├── cleaner.py              # Brain 1 — text cleaning
    ├── chunker.py              # Brain 2 — text chunking
    ├── claim_extractor.py      # Brain 2 — claim extraction
    ├── claim_normalizer.py     # Brain 2 — deduplication
    ├── strategy_brain.py       # Brain 3 — verification planning
    ├── evidence_brain.py       # Brain 4 — evidence retrieval
    ├── judgment_brain.py       # Brain 5 — verdict generation
    ├── agent_orchestrator.py   # Pipeline coordinator
    ├── confidence_engine.py    # Risk scoring
    └── prompts.py              # All LLM prompts
```

---

## 🏢 Relevance to Enterprise Audit

This system directly addresses a use case in Deloitte's ESG Assurance practice. Key enterprise design decisions:

- **Modular architecture** — each brain has one responsibility and one failure mode
- **Audit traceability** — every claim is linked back to its source page
- **Grounded judgment** — verdicts based only on retrieved evidence, not LLM knowledge
- **Graceful degradation** — pipeline never crashes on single component failure
- **Domain integrity** — company press releases excluded from evidence sources

