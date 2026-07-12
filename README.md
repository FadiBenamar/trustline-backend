# TrustLine Backend Engine

TrustLine is a lightweight, asynchronous FastAPI backend designed to verify social media and messaging app content for misinformation, sensationalism, and synthetic text. Built for the **UNESCO Youth Hackathon 2026 (Media and Information Literacy Track)**, it implements a decoupled 5-Step MIL Loop architecture tailored for low-bandwidth environments, teens/20s, and non-native English speakers.

---

## Technical Stack & Architecture

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python) for asynchronous performance and native Pydantic validation.
- **Scraping Engine**: BeautifulSoup4 & HTTPX for clean main text extraction from direct URLs.
- **AI Text Parsing**: OpenAI API (`gpt-4o-mini` with structured JSON outputs) + a high-fidelity rule-based heuristic local fallback.
- **Rate Limiting & Cost Control**: sliding-window rate limiter per client IP + global USD budget protection cap.

---

## 5-Step Media Information Literacy (MIL) Ingestion

1. **Access (Data Ingestion)**: Supports text pasting or direct URL scraping. In Lite Mode, heavy data structures are bypassed.
2. **Analyze & Reflect (Nutrition Label Engine)**: Returns a JSON payload mapping to a Traffic-Light summary (🟢 Low, 🟡 Moderate, 🔴 High Risk) and parses four critical metrics:
   - _Emotional Manipulation_: Sensationalism, fear-mongering, and loaded language.
   - _Missing Sources / Context_: Unverified assertions or claims lacking references.
   - _Signals Associated with Synthetic Text_: Wording patterns or generic text structures typical of generative AI (presented as a pattern detection rather than a confident binary verdict).
   - _Logical Fallacies_: Systemic cognitive flaws (ad hominem, false authority, appeal to emotion).
3. **Create & Act (Correction & Distribution)**: Generates a polite, fact-based correction snippet suitable for one-tap copy/pasting back into group chats (e.g. WhatsApp, Telegram).

---

## API Endpoints

### 1. Ingest & Analyze

- **Endpoint**: `POST /analyze/`
- **Request Payload**:
  ```json
  {
    "content": "Pasted message text OR https://example-news-link.com",
    "lite_mode": false
  }
  ```
- **Response Payload**: Contains traffic light levels, consolidates scores (0–100), flag severities with educational explanations, fact correction snippets, and API usage cost metrics.

### 2. WhatsApp/Telegram Webhook Simulation

- **Endpoint**: `POST /mock/webhook`
- **Request Payload**:
  ```json
  {
    "sender": "+123456789",
    "message_body": "Sensational message text...",
    "platform": "whatsapp"
  }
  ```
- **Response Payload**: Returns a formatted response replicating a messaging bot's automatic fact-checking reply in the group chat.

### 3. Usage Analytics (Admin Panel)

- **Endpoint**: `GET /admin/stats`
  - Exposes total requests, estimated API costs, active fallback count, and cost caps.
- **Endpoint**: `POST /admin/reset-stats`
  - Resets internal request statistics.

---

## Setup & Running the Server

### 1. Initialize Virtual Environment & Install Dependencies

Ensure you run within the virtual environment:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Environment Variables (`.env`)

Create a `.env` file from the example:

```bash
cp .env.example .env
```

_Note: If `OPENAI_API_KEY` is not provided or left blank, the server automatically defaults to a high-fidelity local heuristic rules engine so that frontend development and judging demos can be executed immediately without API cost._

### 3. Start the Server

```bash
.venv/bin/uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`. You can inspect endpoints and run test requests via the interactive OpenAPI Docs at `http://127.0.0.1:8000/docs`.

### 4. Run Verification Tests

To run the end-to-end TestClient verification suite:

```bash
.venv/bin/python3 scratch/test_endpoints.py
```
