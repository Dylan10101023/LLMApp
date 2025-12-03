import os
import time
import json

from dotenv import load_dotenv
from openai import OpenAI

from colorama import init as colorama_init, Fore, Style

from rag import RAGEngine
from prompts import build_system_prompt, build_user_prompt_qa, build_user_prompt_quiz
from safety import is_input_too_long, check_prompt_injection, MAX_INPUT_CHARS
from telemetry import log_request

# Initialize env + colors
load_dotenv()
colorama_init(autoreset=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

client = OpenAI(api_key=OPENAI_API_KEY)

rag_engine = RAGEngine(
    data_dir="data/notes",
    embedding_model=EMBEDDING_MODEL
)


def call_llm(pathway: str, user_text: str, mode: str):
    """
    pathway: 'rag' or 'none'
    mode: 'qa' or 'quiz'
    """
    if is_input_too_long(user_text):
        print(
            Fore.RED
            + f"[Error] Input is too long (>{MAX_INPUT_CHARS} characters). "
              "Please shorten your question."
        )
        return

    injection_flag, reason = check_prompt_injection(user_text)
    if injection_flag:
        print(Fore.RED + "[Safety] Your input looks like a prompt-injection attempt.")
        print(
            Fore.YELLOW
            + "I can't follow instructions that try to override my safety rules."
        )
        print(Fore.BLUE + f"(Detected: {reason})")
        return

    retrieved_context = ""
    if pathway == "rag":
        print(Fore.CYAN + "🔍 Searching your notes for relevant content...")
        retrieved_docs = rag_engine.search(user_text, k=4)
        retrieved_context = "\n\n".join(
            [f"[DOC {i+1}]\n{chunk}" for i, chunk in enumerate(retrieved_docs)]
        )

    system_prompt = build_system_prompt()
    if mode == "qa":
        user_prompt = build_user_prompt_qa(user_text, retrieved_context)
    else:
        user_prompt = build_user_prompt_quiz(user_text, retrieved_context)

    print(Fore.CYAN + "🤖 Thinking...")
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
            # Optional: approximate cost here if you want

        log_request(
            pathway=pathway,
            latency=latency,
            tokens=tokens,
            cost=cost,
            mode=mode
        )

        print(Fore.GREEN + "\n=== STUDYBUDDY RESPONSE ===")
        print(Style.BRIGHT + content)
        print(Fore.GREEN + "============================\n")
        print(Fore.MAGENTA + f"(Latency: {latency:.2f}s | Tokens: {tokens})\n")

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
        print(Fore.RED + "[Error] Something went wrong with the LLM call.")
        print(Fore.RED + str(e))


def print_banner():
    print(Fore.CYAN + Style.BRIGHT + "===============================")
    print(Fore.CYAN + Style.BRIGHT + "        StudyBuddy RAG         ")
    print(Fore.CYAN + "  Study from your own HCI notes")
    print(Fore.CYAN + "===============================\n")


def print_menu():
    print(Fore.YELLOW + "What would you like to do?")
    print(Fore.YELLOW + "  [1] Ask a question about your notes")
    print(Fore.YELLOW + "  [2] Generate quiz questions")
    print(Fore.YELLOW + "  [q] Quit")


def main():
    print_banner()

    if not OPENAI_API_KEY:
        print(
            Fore.RED
            + "[Setup Error] OPENAI_API_KEY is not set. "
              "Create a .env file with your key."
        )
        return

    while True:
        try:
            print_menu()
            choice = input(Fore.GREEN + "> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n" + Fore.CYAN + "Goodbye! 👋")
            break

        if choice == "q":
            print(Fore.CYAN + "Good luck with your studying! 📚")
            break

        elif choice == "1":
            question = input(
                Fore.GREEN + "Enter your study question (or blank to cancel): "
            ).strip()
            if not question:
                print(Fore.BLUE + "Cancelled. Returning to main menu.\n")
                continue
            call_llm(pathway="rag", user_text=question, mode="qa")

        elif choice == "2":
            topic = input(
                Fore.GREEN + "Enter a topic for quiz questions (or blank to cancel): "
            ).strip()
            if not topic:
                print(Fore.BLUE + "Cancelled. Returning to main menu.\n")
                continue
            call_llm(pathway="rag", user_text=topic, mode="quiz")

        else:
            print(Fore.RED + "Invalid option. Please choose 1, 2, or q.\n")


if __name__ == "__main__":
    main()