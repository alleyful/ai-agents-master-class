"""Use saved ChatGPT/Codex authentication to judge offline KnitCoach results."""

import json
import os
import subprocess
import sys
from pathlib import Path

os.environ["OPENAI_API_KEY"] = ""
os.environ["KNITCOACH_ENABLE_VISION"] = "0"

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from knitcoach import create_knitcoach, invoke_turn  # noqa: E402

BASE_DIR = PROJECT_DIR / "evals"


def collect_results() -> list[dict]:
    cases = [json.loads(line) for line in (BASE_DIR / "cases.jsonl").read_text().splitlines() if line.strip()]
    results = []
    for case in cases:
        if case.get("has_image"):
            continue  # Image eval fixtures are added separately; never pretend a missing image was analyzed.
        state = invoke_turn(create_knitcoach(), case["input"], f"codex-eval-{case['id']}")
        results.append({
            "scenario": case,
            "response": state.get("user_response", ""),
            "route": state.get("journey", ""),
        })
    return results


def main() -> None:
    rubric = (BASE_DIR / "rubric.md").read_text()
    prompt = (
        "You are evaluating a Korean beginner knitting tutor. Apply the rubric strictly. "
        "Do not rewrite the answers. Return JSONL only, one object per scenario.\n\n"
        f"RUBRIC:\n{rubric}\n\nCASES AND RESULTS:\n"
        + json.dumps(collect_results(), ensure_ascii=False)
    )
    env = os.environ.copy()
    env.pop("CODEX_API_KEY", None)
    completed = subprocess.run(["codex", "exec", "--json", prompt], check=False, text=True, env=env)
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
