# PromptSentinel

PromptSentinel is an advanced, multi-stage middleware platform for detecting, classifying, and mitigating prompt injections, jailbreaks, and other adversarial inputs targeting Large Language Models (LLMs). It intercepts user inputs before they reach the core LLM and blocks or flags malicious activity with high accuracy and explainability.

## 1. Project Overview

PromptSentinel functions as a robust security layer implementing:
* **Advanced Preprocessing:** Text normalization, decoding (Base64, Hex, URL, Unicode), and zero-width character stripping.
* **Deterministic / Rule-Based Detection:** High-speed Regex matching for well-known evasion signatures.
* **Semantic Detection:** Embedding-based retrieval matching user prompts against a comprehensive taxonomy of malicious and benign examples.
* **Multilingual Semantic Evaluation:** Robust cross-lingual matching (e.g., Hindi, English) via multilingual embedding spaces and CrossEncoders.
* **CrossEncoder Reranking:** Precision-targeted reranking of retrieved semantic matches.
* **Confidence / Risk Fusion:** Algorithmic merging of deterministic and semantic signals to produce a unified risk score.
* **Conditional LLM Judge:** An authoritative secondary LLM evaluator triggered only on uncertain fusion boundaries.
* **Alert / Observability System:** PostgreSQL-backed persistence of telemetry and decisions.
* **OCR / Image Support:** Extraction and scanning of text embedded within images (PNG, JPG, TIFF) via EasyOCR.
* **WebSocket / Live Dashboard:** A React-based operational dashboard mapping real-time detections and benchmark telemetry.
* **Feedback Learning Architecture:** Semi-supervised (Phase 18) reinforcement learning mechanism converting borderline production scans into permanent taxonomy enhancements.
* **Benchmark / Evaluation Framework:** A repeatable pipeline for large-scale dataset evaluations without polluting production statistics.

## 2. Architecture

```text
Input (Text / Image / File)
  ↓
Advanced Preprocessing (Decoders, OCR, Normalization)
  ↓
┌─────────────────────────────────────────┐
│ Detection Pipeline                      │
│                                         │
│ 1. Regex / Deterministic                │
│ 2. Semantic Retrieval (Embeddings)      │
│ 3. CrossEncoder Reranking               │
│ 4. Anomaly / Baseline Measurement       │
└─────────────────────────────────────────┘
  ↓
Fusion / Confidence Scoring
  ↓
Conditional LLM Judge
  ↓
Risk Calculation (Score & Severity)
  ↓
Alert Persistence / API / Dashboard
```

> **Note**: The exact production model configuration is defined in `config.py` and the semantic pipeline. The current integration uses `intfloat/multilingual-e5-base` and `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.

## 3. Phase History

PromptSentinel has been developed in iterative phases. The current status through Phase 20 is complete:

| Phase | Description | Status |
|---|---|---|
| **Phase 1-13** | Core engines, preprocessing, API, LLM Judge, and WebSocket dashboard. | Complete |
| **Phase 14** | Multi-modal OCR/Image extraction and PDF parsing. | Complete |
| **Phase 15** | CrossEncoder implementation and fusion tuning. | Complete |
| **Phase 16** | Comprehensive Risk Scoring and Alert persistence. | Complete |
| **Phase 17** | Context-Aware LLM Judge routing and optimization. | Complete |
| **Phase 18** | Reinforcement Feedback Learning loop and taxonomy tuning. | Complete |
| **Phase 19** | Benchmark evaluation, Multilingual Embedding analysis (E5), Taxonomy Expansion, and Deterministic Remediation. | Complete |
| **Phase 20** | Production vs. Benchmark Scan Accounting & Dashboard Separation. | Complete |
| **Phase 20.5** | Repository cleanup, test organization, and documentation. | Complete |

### Phase 19 Overview:
Phase 19 introduced a rigorous offline evaluation framework.
* **Benchmark Schema:** Standardized JSONL tracking of true/false positive/negative boundaries.
* **Dataset:** 5,000-sample `v1.0.0` evaluation set across English, Hindi, and adversarial vectors.
* **Evaluations:** 
  * Multilingual embedding analysis (`multilingual-e5-base`).
  * Multilingual CrossEncoder analysis.
  * Detection-gap analysis isolating false negative boundaries.
  * Taxonomy expansion experiments (which inadvertently collapsed the SAFE boundary due to asymmetric benign scaling).
  * Deterministic regex remediation for high-risk gaps (Stored Injection).

### Phase 20 Overview:
Phase 20 isolated telemetry paths to prevent benchmark execution from contaminating the production database or the Phase 18 learning system. Dashboard APIs dynamically surface distinct metrics.

## 4. Benchmark Baselines

### Phase 19.6 (Frozen Semantic Baseline)
* **TP:** 2556 | **TN:** 1264 | **FP:** 86 | **FN:** 1094
* **Accuracy:** 76.40%
* **Precision:** 96.74%
* **Recall:** 70.03%
* **F1:** 81.25%
* **Hindi Recall:** 38.86%

### Phase 19.8 (Taxonomy-Expansion State)
* **TP:** 2233 | **TN:** 1264 | **FP:** 86 | **FN:** 1417
* **Accuracy:** 69.94%
* **Precision:** 96.29%
* **Recall:** 61.18%
* **F1:** 74.82%
* **Hindi Recall:** 62.29%
> *Regression Note: Adding 160 benign baseline samples shifted the unified classifier `SAFE` boundary excessively, dropping overall recall.*

### Phase 19.9 (Current Integrated Detector Baseline)
* **TP:** 2457 | **TN:** 1264 | **FP:** 86 | **FN:** 1193
* **Accuracy:** 74.42%
* **Precision:** 96.62%
* **Recall:** 67.32%
* **F1:** 79.35%
* **Hindi Recall:** 62.29%
* **Stored Injection Recall:** 92.25%
> *Note: Phase 19.9 applies robust regex definitions to restore stored-injection vulnerabilities without reversing the multilingual gains found in 19.8.*

## 5. Dashboard Accounting & Phase 18 Isolation

The React dashboard now cleanly separates metrics:
* **Production Scans:** Prompts evaluated through the production API (`/api/v1/scan`) and persisted directly to the PostgreSQL database for UI review and Phase 18 Reinforcement Learning.
* **Benchmark Evaluations:** Samples processed exclusively by the benchmark runner.

### Benchmark Data Isolation (Phase 20)
* **Benchmark → production scan DB:** NO
* **Benchmark → feedback table:** NO
* **Benchmark → learning candidates:** NO
* **Benchmark → reviews:** NO
* **Benchmark → learning configuration:** NO

Benchmark evaluations intentionally bypass production alert and feedback persistence.

**Current Validation Reference (Not Hardcoded):**
* Production Scans: approximately 1051
* Benchmark Evaluations: 5000 (Dataset: `v1.0.0`)

## 6. Installation / Setup

1. **Clone the Repository**
   ```bash
   git clone <repository_url> prompt_sentinel
   cd prompt_sentinel
   ```

2. **Setup Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables & Database**
   Ensure PostgreSQL is running locally on port 5432.
   Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your LLM keys and DATABASE_URL
   ```

## 7. Running Tests

PromptSentinel uses `pytest`. Ensure `TEST_DATABASE_URL` is set to prevent tests from destroying the production database.

Run the full suite:
```bash
export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/promptsentinel_test"
python -m pytest
```

Run phase-specific tests:
```bash
python -m pytest tests/phase20 -v
python -m pytest tests/phase19 -v
```

> **Note:** The `test_gemini_live.py` test relies on real API execution. If your Gemini quota is exhausted (HTTP 429), this specific test will intentionally fail. Do not weaken the live test assertions.

## 8. Running the Application

### Backend API
Start the FastAPI backend with hot-reload enabled:
```bash
uvicorn app:app --reload --port 8000
```
API Documentation will be available at `http://localhost:8000/docs`.

### Frontend Dashboard
In a separate terminal, start the React development server:
```bash
cd dashboard
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

## 9. Repository Structure

```text
api/             API routes
connectors/      External/service connectors
context/         Context handling
database/        Database models/connection
datasets/        Datasets and benchmark data
detectors/       Detection engines
evaluation/      Evaluation framework
llm/             LLM Judge/provider logic
policies/        Security policies
preprocessing/   Input normalization
scoring/         Risk/scoring logic
scripts/         Operational/benchmark scripts
semantic/        Semantic detection
services/        Application services
taxonomy/        Detection taxonomy
tests/           Automated tests and fixtures
dashboard/       React dashboard
docs/            Documentation and reports
data/            Runtime/local data where applicable
logs/            Runtime logs where applicable
scratch/         Isolated debug artifacts
```
