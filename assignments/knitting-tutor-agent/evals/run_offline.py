"""Run deterministic routing checks without loading an API credential."""

import json
import os
import sys
from pathlib import Path

os.environ["OPENAI_API_KEY"] = ""
os.environ["KNITCOACH_ENABLE_VISION"] = "0"

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from domain.journeys import infer_journey  # noqa: E402
from knitcoach import detect_input_type, detect_intent  # noqa: E402

BASE_DIR = PROJECT_DIR / "evals"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in (BASE_DIR / "cases.jsonl").read_text().splitlines() if line.strip()]


def evaluate_case(case: dict) -> dict:
    input_type = "image_path" if case.get("has_image") else detect_input_type(case["input"])
    intent = "generate_pattern" if case.get("task") == "generate_pattern" else detect_intent(case["input"], input_type)
    actual = infer_journey(
        case["input"],
        input_type=input_type,
        intent=intent,
        has_image=case.get("has_image", False),
        task=case.get("task", "tutor"),
    )
    return {
        "id": case["id"],
        "expected": case["journey"],
        "actual": actual.value,
        "passed": actual.value == case["journey"],
    }


def main() -> None:
    results = [evaluate_case(case) for case in load_cases()]
    for result in results:
        print(json.dumps(result, ensure_ascii=False))
    failed = [result for result in results if not result["passed"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} journey routes passed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
