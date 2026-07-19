"""Contracts for the local Codex subscription provider."""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from knitcoach import ImageObservation
from model_provider import run_structured_model


class CodexExecProviderTests(unittest.TestCase):
    def test_codex_exec_uses_saved_auth_image_and_json_schema(self) -> None:
        observed: dict = {}

        def fake_run(command, **kwargs):
            observed["command"] = command
            observed["env"] = kwargs["env"]
            observed["input"] = kwargs["input"]
            output_path = Path(command[command.index("--output-last-message") + 1])
            output_path.write_text(json.dumps({
                "summary": "사진에서 코바늘 가방의 앞면을 확인했습니다.",
                "tool_type": "crochet",
                "project_type": "가방",
                "confidence": "medium",
                "visible_facts": ["망사 형태의 반복 무늬가 보입니다."],
                "likely_techniques": ["사슬뜨기", "한길긴뜨기"],
                "construction": ["몸판과 손잡이가 연결되어 보입니다."],
                "diagnoses": [],
                "suggested_actions": ["무늬 반복 한 칸을 먼저 떠 보세요."],
                "uncertainties": ["바닥 구조는 보이지 않습니다."],
                "additional_photos": ["가방 바닥"],
            }, ensure_ascii=False))
            return subprocess.CompletedProcess(command, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "bag.png"
            image_path.write_bytes(b"test-image")
            environment = {
                "KNITCOACH_MODEL_PROVIDER": "codex_exec",
                "KNITCOACH_CODEX_CACHE": "0",
                "OPENAI_API_KEY": "must-not-be-forwarded",
                "CODEX_API_KEY": "must-not-be-forwarded",
            }
            with patch.dict(os.environ, environment, clear=False), patch(
                "model_provider.subprocess.run", side_effect=fake_run
            ):
                result = run_structured_model("사진을 분석하세요.", ImageObservation, image_path=image_path)

        command = observed["command"]
        self.assertEqual(["codex", "exec"], command[:2])
        self.assertIn("--ephemeral", command)
        self.assertIn("--sandbox", command)
        self.assertIn("read-only", command)
        self.assertIn("--output-schema", command)
        self.assertIn("--image", command)
        self.assertNotIn("OPENAI_API_KEY", observed["env"])
        self.assertNotIn("CODEX_API_KEY", observed["env"])
        self.assertEqual("사진을 분석하세요.", observed["input"])
        self.assertEqual("crochet", result.tool_type)
        self.assertEqual(["가방 바닥"], result.additional_photos)


if __name__ == "__main__":
    unittest.main()
