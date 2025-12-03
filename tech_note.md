# Tech Note – StudyBuddy RAG (LLM App)

## 1. Overview

StudyBuddy RAG is a small command-line LLM app that helps students review **Human–Computer Interaction (HCI)** content using their own notes. The user can:

- Ask questions about their HCI notes.
- Generate quiz questions (short-answer + multiple choice) from a topic.

The app uses a **Retrieval-Augmented Generation (RAG)** pipeline: it embeds local notes, retrieves the most relevant chunks, and passes them to an LLM with a strict system prompt. The design focuses on: (1) a real, usable flow; (2) basic safety guardrails; (3) simple telemetry; and (4) offline evaluation.

---

## 2. Architecture

### Components

- `app.py` – CLI entrypoint, user menu, orchestrates each request.
- `rag.py` – Loads notes from `data/notes/`, chunks them, computes embeddings, and does vector search.
- `prompts.py` – Builds the system prompt and user prompts for Q&A and quiz generation.
- `safety.py` – Input length guard and simple prompt-injection detector.
- `telemetry.py` – Logs request metadata (pathway, latency, tokens, errors) to `logs/requests.log`.
- `eval_utils.py` / `eval_tests.py` – Offline evaluation pipeline using `tests.json`.

### Data Flow (ASCII diagram)

```text
User (CLI)
   │
   ▼
[ app.py ]  -- user text -->  [ safety.py ]
   │                             │
   │                             ├─ if too long or injection → error message
   │                             ▼
   │                        safe, cleaned input
   │
   ▼
[ rag.py ] -- query --> [ OpenAI Embeddings ]
   │                      (text-embedding-3-small)
   │
retrieved note chunks
   │
   ▼
[ prompts.py ] -- system + user messages -->
   │
   ▼
[ OpenAI Chat Model ] (e.g., gpt-4.1-mini)
   │
   ├─ response text → back to `app.py` (printed to user)
   └─ usage/latency → [ telemetry.py ] → logs/requests.log
