import json
from app import call_llm  # reuse core logic, but we need a small wrapper

# We slightly adapt call_llm to return content instead of printing.
# Easiest: copy its logic into a helper function here. For brevity,
# assume we wrote a function `run_llm(mode, text)` in a shared module.
from eval_utils import run_llm  # you'll create this small helper

def run_test_case(case):
    mode = case["mode"]
    user_input = case["input"]
    expected_keywords = case.get("expected_keywords", [])
    must_not_contain = case.get("must_not_contain", [])

    response = run_llm(mode=mode, user_text=user_input, pathway="rag")

    resp_lower = response.lower()
    passed = True

    for kw in expected_keywords:
        if kw.lower() not in resp_lower:
            passed = False
            break

    for bad in must_not_contain:
        if bad.lower() in resp_lower:
            passed = False
            break

    return passed, response


def main():
    with open("tests.json", "r", encoding="utf-8") as f:
        tests = json.load(f)

    passed_count = 0
    for case in tests:
        ok, _ = run_test_case(case)
        print(f"{case['id']}: {'PASS' if ok else 'FAIL'}")
        if ok:
            passed_count += 1

    total = len(tests)
    print(f"\nPass rate: {passed_count}/{total} = {passed_count / total * 100:.1f}%")

if __name__ == "__main__":
    main()