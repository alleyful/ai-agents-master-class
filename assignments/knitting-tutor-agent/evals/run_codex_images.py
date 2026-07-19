"""Run real image journeys through saved ChatGPT/Codex authentication.

This local-only check deliberately clears Platform API keys. Results are cached
by the provider so repeating an unchanged scenario does not spend another model
turn unless KNITCOACH_CODEX_CACHE=0 is set.
"""

import json
import os
import sys
from pathlib import Path

os.environ["OPENAI_API_KEY"] = ""
os.environ.pop("CODEX_API_KEY", None)
os.environ["KNITCOACH_ENABLE_VISION"] = "0"
os.environ["KNITCOACH_MODEL_PROVIDER"] = "codex_exec"

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from knitcoach import create_knitcoach, invoke_turn  # noqa: E402


def compact_result(name: str, state: dict) -> dict:
    return {
        "scenario": name,
        "provider": state.get("model_provider"),
        "journey": getattr(state.get("journey"), "value", state.get("journey")),
        "response": state.get("user_response", ""),
        "image_observation": state.get("image_observation", {}),
        "pattern_draft": state.get("pattern_draft", {}),
        "model_note": state.get("model_note", ""),
    }


def main() -> None:
    image = PROJECT_DIR / "samples" / "crochet-mesh-shoulder-bag.png"
    diagnosis = invoke_turn(
        create_knitcoach(),
        "이 가방 사진에서 실제로 보이는 구조와 고르게 뜨지 않은 부분이 있는지 진단해줘",
        "codex-image-diagnosis",
        image_path=str(image),
        original_image_name=image.name,
    )
    pattern = invoke_turn(
        create_knitcoach(),
        "이 사진 속 가방을 비슷하게 만들 수 있는 테스트 도안 초안을 만들어줘",
        "codex-image-pattern",
        image_path=str(image),
        original_image_name=image.name,
        task="generate_pattern",
        pattern_options={
            "tool_type": "auto",
            "finished_size": "가로 28cm × 세로 32cm",
            "yarn_weight": "중간 굵기 면사",
            "tool_size": "4.0mm",
            "gauge": "미측정",
            "skill_level": "beginner",
            "notes": "사진에서 보이지 않는 바닥과 코 수는 가정으로 표시",
        },
    )
    print(json.dumps([
        compact_result("photo_diagnosis", diagnosis),
        compact_result("photo_pattern", pattern),
    ], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
