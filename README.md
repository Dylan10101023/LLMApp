# StudyBuddy RAG

Small LLM app that helps a student study using their own notes (RAG-based Q&A and quiz generation).

## Goal

- Answer questions using local notes (`data/notes/`).
- Generate quiz questions for a topic from those notes.
- Demonstrate:
  - Core LLM feature
  - RAG enhancement
  - Safety/robustness guardrails
  - Telemetry (latency, pathway, tokens)
  - Offline evaluation with tests.json
  - Reproducible setup

## Stack

- Language: Python 3.10+
- Model: OpenAI Chat (e.g., `gpt-4.1-mini`)
- Embeddings: `text-embedding-3-small`
- Interface: CLI

## Setup

1. Clone this repo.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate

## Youtube Link
https://youtu.be/olW-EeU91fY
