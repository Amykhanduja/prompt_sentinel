# PromptSentinel

PromptSentinel is an advanced, multi-stage middleware security platform designed to detect, classify, and mitigate prompt injections, jailbreaks, and other adversarial inputs targeting Large Language Models (LLMs). It intercepts user inputs before they reach the core LLM and blocks or flags malicious activity with high accuracy and explainability.

## 1. Project Overview

PromptSentinel functions as a robust security layer implementing:
* **Advanced Preprocessing:** Text normalization, decoding (Base64, Hex, URL, Unicode), and zero-width character stripping.
* **OCR / Image Support:** Extraction and scanning of text embedded within images (PNG, JPG, TIFF) via EasyOCR.
* **Deterministic / Rule-Based Detection:** High-speed Regex matching for well-known evasion signatures and stored injections.
* **Semantic Detection:** E5-based multilingual embedding retrieval matching user prompts against a comprehensive taxonomy of malicious and benign examples.
* **CrossEncoder Reranking:** Precision-targeted reranking of retrieved semantic matches.
* **Confidence / Risk Fusion:** Algorithmic merging of deterministic and semantic signals to produce a unified risk score.
* **Conditional LLM Judge:** An authoritative secondary LLM evaluator (Gemini) triggered only on uncertain fusion boundaries.
* **Alert / Observability System:** PostgreSQL-backed persistence of telemetry and decisions.
* **WebSocket / Live Dashboard:** A React-based operational dashboard mapping real-time detections and benchmark telemetry.
* **Feedback Learning Architecture:** Semi-supervised (Phase 18) reinforcement learning mechanism converting borderline production scans into permanent taxonomy enhancements.
* **Benchmark / Evaluation Framework:** A repeatable offline evaluation pipeline ensuring robust performance tracking without polluting production statistics.

## 2. Architecture

PromptSentinel operates a sophisticated multi-layered defense-in-depth pipeline. The diagram below illustrates the actual implementation flow:

```mermaid
flowchart TD

    A[User / Application Input] --> B{Input Type}

    B -->|Text| C[Prompt Input]
    B -->|Image| D[Image Input]
    
    D --> E[EasyOCR Parsing]
    E --> C

    C --> F[Advanced Preprocessing]

    F --> F1[Unicode Normalization]
    F1 --> F2[Confusable / Homoglyph]
    F2 --> F3[OCR Normalization]
    F3 --> F4[Markdown Cleanup]
    F4 --> F5[Whitespace Normalization]
    F5 --> F6[Contextual Leetspeak]

    F6 --> G[Detection Engine]

    G --> H[Deterministic Regex Detectors]
    G --> I[Semantic Detection]
    G --> J[Fuzzy / Anomaly Detectors]

    I --> I1[Multilingual E5 Embedding]
    I1 --> I2[FAISS Candidate Retrieval]
    I2 --> I3[Top-20 Candidates]
    I3 --> I4[CrossEncoder Reranking]
    I4 --> I5[Top-3 Candidates]
    I5 --> I6[Semantic Classifier]

    H --> K[Detection Fusion]
    I6 --> K
    J --> K

    K --> L[Confidence / Risk Assessment]

    L --> M{Confidence Level}

    M -->|Very High / High| N[Deterministic Decision]
    M -->|Medium / Low| O{LLM Judge Enabled?}

    O -->|No| N
    O -->|Yes| P[LLM Judge via Gemini]

    P --> Q[Structured Judge Result]
    Q --> R[Safe Decision Merge]

    N --> S[Final Risk Score Calculation]
    R --> S

    S --> T[Final Policy Decision]

    T --> U[API Response]
    T --> V[PostgreSQL Persistence]
    V --> W[WebSocket Broadcast to Dashboard]
```

## 3. End-to-End Pipeline Stages

### 3.1 Input Layer
PromptSentinel supports multiple input channels via its REST API:
* **Text Scanning:** `/api/v1/scan`
* **File/Image Scanning:** `/api/v1/scan-file`

All requests are strongly validated using Pydantic schemas. 

### 3.2 OCR & Image Processing
PromptSentinel natively processes images containing text (e.g., screenshots of prompts). 
When an image is submitted:
1. `connectors.image_parser` invokes EasyOCR.
2. Extracted text is channeled back into the primary text pipeline.
3. The image context is preserved for logging.

```mermaid
flowchart LR
    A[Image Payload] --> B[EasyOCR Extraction]
    B --> C[Extracted Text]
    C --> D[Standard Preprocessing]
    D --> E[Detection Engine]
```

### 3.3 Advanced Preprocessing
Attackers frequently use obfuscation (zero-width characters, homoglyphs, invisible formatting) to evade detection. 
PromptSentinel applies a rigid sequence of normalization passes:
1. Unicode Normalization (NFC)
2. Confusable/Homoglyph resolution
3. OCR noise reduction
4. Markdown stripping
5. Whitespace normalization
6. Contextual Leetspeak decoding

**Crucially**, preprocessing does *not* destroy the original input. The API and database persist the `original_text` while feeding the `normalized_text` to the detection engines.

## 4. Detection Architecture

PromptSentinel avoids relying on a single "magic" model. It fuses multiple independent layers.

### 4.1 Deterministic Detection
Implemented in `detectors/`, these are high-speed regular expressions and heuristic rules targeting explicit, well-known signatures.
* **Why it exists:** Regex rules provide 100% precision for known malicious patterns (e.g., common stored injections or framework-specific jailbreaks).
* **Behavior:** Extremely fast; strongly overrides weaker ML classification if a definitive malicious pattern is found.

### 4.2 Semantic Detection
Implemented in `semantic/semantic_engine.py`, the semantic pipeline performs similarity matching against a curated taxonomy.

```mermaid
flowchart LR
    A[Preprocessed Prompt] --> B[E5 Multilingual Embedding dim:768]
    B --> C[FAISS Index Search]
    C --> D[Top 20 Taxonomy Examples]
    D --> E[MiniLM CrossEncoder Reranking]
    E --> F[Top 3 Reranked Examples]
    F --> G[Linear Classifier]
    G --> H[Semantic Risk Output]
```
* **Embedding Model:** `intfloat/multilingual-e5-base`
* **CrossEncoder Reranking:** `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
* **Behavior:** The engine retrieves similar historical attacks and applies a classifier (Logistic Regression) to score the current prompt based on the retrieved neighbors. 

### 4.3 Multilingual Detection
Phase 19 heavily validated multilingual capabilities. The architecture transitioned from an English-only BGE baseline to the current `multilingual-e5-base` paired with a multilingual CrossEncoder. This significantly boosted detection of translated attacks (e.g., Hindi) without regressing English baseline accuracy.

### 4.4 Fusion & Risk Calculation
Implemented in `fusion.py` and `scoring/`, multiple detector signals (Regex, Semantic, Fuzzy) are combined.

```mermaid
flowchart TD
    A[Regex Detections] --> D[Evidence Collection]
    B[Semantic Score] --> D
    C[Fuzzy Anomalies] --> D
    
    D --> E[Confidence Resolution]
    E --> F[Risk Calculation Formula]
    F --> G[Final Risk Score 0-100+]
    G --> H{Policy Rule}
    H -->|Score > Threshold| I[Block]
    H -->|Score < Threshold| J[Allow]
```
If a prompt hits a known deterministic rule, its risk skyrockets. If it only mildly triggers semantic similarity, the confidence is flagged as `medium` or `low`, delegating the final call to the LLM Judge.

## 5. LLM Judge Architecture

To minimize latency and cost, external LLMs are **not** invoked for every prompt. 

```mermaid
flowchart TD
    A[Unified Risk & Confidence] --> B{Confidence Threshold}
    B -->|Very High / High| C[Skip LLM Judge - Immediate Return]
    B -->|Medium / Low| D{LLM Judge Enabled in Config?}
    
    D -->|No| C
    D -->|Yes| E[Invoke Gemini-based LLM Judge]
    
    E --> F[Structured JSON Assessment]
    F --> G[Merge Decision with Base Risk]
    G --> H[Final Overriding Decision]
```
The Judge evaluates ambiguous prompts using a strict rubric and returns a JSON payload dictating whether the prompt is malicious or benign.

## 6. Persistence & Database Architecture

PromptSentinel uses PostgreSQL via SQLAlchemy, with Alembic for migrations.

```mermaid
erDiagram
    SCANS ||--o{ DETECTIONS : contains
    SCANS ||--o| ALERTS : triggers
    ALERTS ||--o| FEEDBACK : generates
    FEEDBACK ||--o| LEARNING_CANDIDATES : proposes
    
    SCANS {
        uuid id
        string prompt
        int risk_score
        string severity
        string action
        jsonb judge_metadata
    }
```
* **Scans:** The master record of every evaluated prompt.
* **Alerts:** Subset of scans that breached policy thresholds.
* **Feedback & Learning:** Infrastructure for Phase 18 Reinforcement Learning.

## 7. Feedback Learning Architecture (Phase 18)

PromptSentinel implements a semi-supervised Human-in-the-Loop (HITL) learning architecture.

```mermaid
flowchart TD
    A[Production Alert generated] --> B[Analyst provides Feedback]
    B --> C[Analytics Engine]
    C --> D[Learning Candidate Created]
    D --> E[Human Review Panel]
    E -->|Approve| F[Update Taxonomy Configuration]
    E -->|Reject| G[Discard]
    F --> H[Dynamic Detection System Update]
```
Instead of uncontrolled online retraining (which is vulnerable to data poisoning), feedback proposes concrete examples to be added to the frozen taxonomy. Once approved, the semantic retrieval engine inherently improves without requiring full model retraining.

## 8. Benchmark Architecture & Scan Accounting

A core architectural principle is that **Benchmark Data Must Not Contaminate Production Telemetry.**

```mermaid
flowchart LR
    A[Benchmark Runner] --> B[Detection Pipeline]
    B --> C[predictions.jsonl]
    
    A -. DOES NOT .-> D[Production DB]
    A -. DOES NOT .-> E[Feedback System]
    A -. DOES NOT .-> F[Learning Candidates]
```

### Dashboard Separation (Phase 20)
The React dashboard cleanly bifurcates metrics:
* **Production Scans:** Live data persisted to PostgreSQL via `/api/v1/scan`.
* **Benchmark Evaluations:** Static offline analytics generated from `datasets/benchmark/results/`.

## 9. Benchmark Results

PromptSentinel's performance is rigorously tracked against a 5,000-sample offline evaluation dataset (`v1.0.0`). 

**Phase 19.6 (Frozen Semantic Control - E5 Baseline)**
* Accuracy: 76.40%
* Precision: 96.74%
* Recall: 70.03%
* Hindi Recall: 38.86%

**Phase 19.8 (Taxonomy-Expansion Experiment)**
* Accuracy: 69.94%
* Recall: 61.18% 
> *Regression Analysis: Adding massive amounts of benign cybersecurity queries to the taxonomy shifted the classifier's SAFE boundary excessively, zeroing out valid attack scores.*

**Phase 19.9 (Current Integrated Detector Baseline)**
* Accuracy: 74.42%
* Precision: 96.62%
* Recall: 67.32%
* Hindi Recall: 62.29%
* **Stored Injection Recall: 92.25%**
> *Reconciliation: Phase 19.9 achieved massive gains in specific vectors (stored injections) by relying on deterministic fusion while preserving the multilingual semantic baseline.*

## 10. Project Status

| Phase | Description | Status |
|---|---|---|
| **Phase 1-13** | Core engines, API, LLM Judge, Dashboard | Complete |
| **Phase 14** | OCR / Image Extraction | Complete |
| **Phase 15** | Advanced Preprocessing | Complete |
| **Phase 16** | Risk Scoring and Alert persistence | Complete |
| **Phase 17** | Context-Aware LLM Judge | Complete |
| **Phase 18** | Feedback Learning loop | Complete |
| **Phase 19** | Benchmark evaluation & Multilingual Semantic | Complete |
| **Phase 20** | Production vs Benchmark Accounting | Complete |

## 11. Repository Structure

* `api/` - FastAPI routing and WebSocket endpoints.
* `connectors/` - External integrations (EasyOCR).
* `database/` - SQLAlchemy models, repositories, and Alembic migrations.
* `datasets/` - Static JSONL benchmark datasets.
* `detectors/` - Regex and fuzzy detection logic.
* `evaluation/` - Benchmark metric calculations.
* `llm/` - Gemini LLM Judge integration.
* `preprocessing/` - Multi-stage text normalization.
* `scoring/` - Risk score and confidence calculation.
* `scripts/` - Offline benchmark runners (`run_benchmark.py`).
* `semantic/` - E5/CrossEncoder retrieval, ranking, and classification.
* `taxonomy/` - JSON/Markdown dictionaries defining attack vectors.
* `tests/` - Comprehensive Pytest suite.
* `dashboard/` - React/Vite operational dashboard.

## 12. Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url> prompt_sentinel
   cd prompt_sentinel
   ```

2. **Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Database Setup**
   Ensure PostgreSQL is running locally on port 5432.
   ```bash
   cp .env.example .env
   # Edit .env to set DATABASE_URL (e.g., postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel)
   alembic upgrade head
   ```

4. **Dashboard Setup**
   ```bash
   cd dashboard
   npm install
   ```

## 13. Configuration
Control system behavior via `.env` or `config.py`. Important toggles include:
* `LLM_JUDGE_ENABLED` (true/false)
* `LLM_JUDGE_PROVIDER` (e.g., gemini)
* `LLM_JUDGE_API_KEY`
* `DATABASE_URL`

## 14. Running the Application

### Backend API
```bash
uvicorn app:app --reload --port 8000
```
API Docs: `http://localhost:8000/docs`

### Frontend Dashboard
```bash
cd dashboard
npm run dev
```
Dashboard: `http://localhost:5173`

## 15. Testing & Benchmarking

### Running Unit & Integration Tests
Ensure `TEST_DATABASE_URL` is set to protect the production database.
```bash
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel_test"
python3 -m pytest
```
> *Note: The `test_gemini_live.py` test relies on live external API execution and may fail with HTTP 429 if quotas are exhausted.*

### Running the Offline Benchmark
```bash
python3 scripts/run_benchmark.py --dataset datasets/benchmark/v1.0.0 --judge-mode disabled
```

## 16. Design Principles

* **Defense in Depth:** No single detector is trusted to catch everything.
* **Fail Safe:** If the LLM Judge times out, the system defaults back to the deterministic/semantic risk score.
* **Lazy Loading:** Heavy ML models (E5/CrossEncoders) only initialize when explicitly required by the pipeline.
* **Human-Governed Learning:** AI does not blindly retrain itself on unverified production inputs.

## 17. Limitations
* **Semantic Classifier Vulnerability:** The logistic regression boundary is highly sensitive to asymmetric taxonomy scaling (proven in Phase 19.8).
* **Latency:** Reranking with CrossEncoders natively requires higher computational overhead.
* **Multilingual Drift:** While Hindi performance is vastly improved via E5, low-resource languages may still present semantic blind spots.

## 18. Roadmap
* Production optimization and detection-quality improvement.
* Migration to Torch-compiled or ONNX-optimized execution for CrossEncoders.
