# eval_utils.py
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from rag import RAGEngine
from prompts import build_system_prompt, build_user_prompt_qa, build_user_prompt_quiz
from safety import is_input_too_long, check_prompt_injection, MAX_INPUT_CHARS
from telemetry import log_request

# Load env vars
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Create a .env file with your key before running evals."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

# Reuse the same RAG engine as the main app
rag_engine = RAGEngine(
    data_dir="data/notes",
    embedding_model=EMBEDDING_MODEL
)


def run_llm(mode: str, user_text: str, pathway: str = "rag") -> str:
    """
    Run the LLM for offline evaluation and return the response text (no printing).

    mode: 'qa' or 'quiz'
    pathway: usually 'rag' for this app
    """
    # Basic safety checks (same idea as in app.py)
    if is_input_too_long(user_text):
        return (
            f"[Error] Input is too long (>{MAX_INPUT_CHARS} characters). "
            "Please shorten your question."
        )

    injection_flag, reason = check_prompt_injection(user_text)
    if injection_flag:
        # Important: this wording lines up with the tests.json expectation
        return "I cannot follow instructions that try to override my safety rules."

    # RAG retrieval (if enabled)
    retrieved_context = ""
    if pathway == "rag":
        retrieved_docs = rag_engine.search(user_text, k=4)
        retrieved_context = "\n\n".join(
            [f"[DOC {i+1}]\n{chunk}" for i, chunk in enumerate(retrieved_docs)]
        )

    system_prompt = build_system_prompt()
    if mode == "qa":
        user_prompt = build_user_prompt_qa(user_text, retrieved_context)
    else:
        user_prompt = build_user_prompt_quiz(user_text, retrieved_context)

    start_time = time.time()
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        latency = time.time() - start_time
        content = response.choices[0].message.content.strip()
        usage = getattr(response, "usage", None)

        tokens = None
        cost = None
        if usage is not None:
            tokens = usage.total_tokens
            # You could compute approximate cost here if you want

        # Log telemetry for eval runs as well
        log_request(
            pathway=pathway,
            latency=latency,
            tokens=tokens,
            cost=cost,
            mode=mode
        )

        return content

    except Exception as e:
        latency = time.time() - start_time
        log_request(
            pathway=pathway,
            latency=latency,
            tokens=None,
            cost=None,
            mode=mode,
            error=str(e)
        )
        return f"[Error] LLM call failed: {e}"
