"""Structured model providers used during development and final API verification.

`codex_exec` intentionally targets trusted local development only. It reuses the
Codex CLI's saved ChatGPT authentication and never forwards Platform API keys.
"""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import subprocess
import tempfile
from pathlib import Path
from typing import TypeVar

from langchain_core.messages import HumanMessage
from pydantic import BaseModel


StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)


class ModelProviderError(RuntimeError):
    """A configured model provider could not return a valid structured result."""


def active_provider_name() -> str:
    """Return the configured provider without reading or exposing credentials."""
    configured = os.getenv("KNITCOACH_MODEL_PROVIDER", "").strip().casefold()
    if configured:
        return configured
    if os.getenv("OPENAI_API_KEY"):
        return "openai_api"
    return "rules"


def structured_model_available() -> bool:
    return active_provider_name() in {"codex_exec", "openai_api"}


def provider_status_label() -> tuple[str, str]:
    provider = active_provider_name()
    if provider == "codex_exec":
        return "Codex 구독 모델 개발 모드", "API 키 없이 저장된 ChatGPT/Codex 인증으로 사진을 분석해요."
    if provider == "openai_api":
        return "AI 문맥 코칭 모드", "대화 의도와 문맥은 모델이 판단하고, 도안과 진도는 검수된 데이터로 관리해요."
    return "오프라인 규칙 테스트 모드", "모델 호출 없이 fixture와 규칙으로 동작해요."


def run_structured_model(
    prompt: str,
    output_model: type[StructuredOutput],
    *,
    image_path: str | Path | None = None,
    model_name: str = "gpt-4.1-mini",
) -> StructuredOutput:
    provider = active_provider_name()
    if provider == "codex_exec":
        return _run_codex_exec(prompt, output_model, image_path=image_path)
    if provider == "openai_api":
        return _run_openai_api(prompt, output_model, image_path=image_path, model_name=model_name)
    raise ModelProviderError("구조화 모델 provider가 비활성화되어 있습니다.")


def _cache_key(prompt: str, output_model: type[BaseModel], image_path: str | Path | None) -> str:
    digest = hashlib.sha256()
    digest.update(output_model.__name__.encode())
    digest.update(prompt.encode())
    if image_path:
        path = Path(image_path)
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _cache_path(key: str) -> Path:
    root = Path(
        os.getenv(
            "KNITCOACH_CODEX_CACHE_DIR",
            str(Path(tempfile.gettempdir()) / "knitcoach-codex-cache"),
        )
    )
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{key}.json"


def _run_codex_exec(
    prompt: str,
    output_model: type[StructuredOutput],
    *,
    image_path: str | Path | None,
) -> StructuredOutput:
    image = Path(image_path).resolve() if image_path else None
    if image and not image.is_file():
        raise ModelProviderError(f"분석할 이미지 파일이 없습니다: {image}")

    cache = _cache_path(_cache_key(prompt, output_model, image))
    if os.getenv("KNITCOACH_CODEX_CACHE", "1") != "0" and cache.is_file():
        try:
            return output_model.model_validate_json(cache.read_text())
        except Exception:
            cache.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="knitcoach-codex-") as temp_dir:
        temp = Path(temp_dir)
        schema_path = temp / "schema.json"
        result_path = temp / "result.json"
        schema_path.write_text(json.dumps(output_model.model_json_schema(), ensure_ascii=False))

        command = [
            "codex",
            "exec",
            "--ephemeral",
            "--sandbox",
            "read-only",
            "--ignore-rules",
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(result_path),
        ]
        if image:
            command.extend(["--image", str(image)])

        env = os.environ.copy()
        # Force saved ChatGPT/Codex authentication instead of accidental API billing.
        env.pop("OPENAI_API_KEY", None)
        env.pop("CODEX_API_KEY", None)
        timeout = int(os.getenv("KNITCOACH_CODEX_TIMEOUT", "180"))
        try:
            completed = subprocess.run(
                command,
                cwd=Path(__file__).resolve().parent,
                env=env,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise ModelProviderError("Codex CLI를 찾을 수 없습니다.") from exc
        except subprocess.TimeoutExpired as exc:
            raise ModelProviderError(f"Codex 분석이 {timeout}초 안에 끝나지 않았습니다.") from exc

        if completed.returncode != 0 or not result_path.is_file():
            detail = (completed.stderr or completed.stdout or "알 수 없는 실행 오류").strip()
            raise ModelProviderError(f"Codex 실행 실패: {detail[-500:]}")
        try:
            result = output_model.model_validate_json(result_path.read_text())
        except Exception as exc:
            raise ModelProviderError("Codex가 유효한 구조화 결과를 반환하지 않았습니다.") from exc

    if os.getenv("KNITCOACH_CODEX_CACHE", "1") != "0":
        cache.write_text(result.model_dump_json())
    return result


def _run_openai_api(
    prompt: str,
    output_model: type[StructuredOutput],
    *,
    image_path: str | Path | None,
    model_name: str,
) -> StructuredOutput:
    if not os.getenv("OPENAI_API_KEY"):
        raise ModelProviderError("OPENAI_API_KEY가 설정되지 않았습니다.")
    try:
        from langchain_openai import ChatOpenAI

        content: list[dict] = [{"type": "text", "text": prompt}]
        if image_path:
            path = Path(image_path)
            if not path.is_file():
                raise ModelProviderError(f"분석할 이미지 파일이 없습니다: {path}")
            mime_type = mimetypes.guess_type(path.name)[0] or "image/png"
            encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}})
        model = ChatOpenAI(model=model_name, temperature=0).with_structured_output(output_model)
        return model.invoke([HumanMessage(content=content)])
    except ModelProviderError:
        raise
    except Exception as exc:
        raise ModelProviderError(f"OpenAI API 구조화 호출 실패: {exc.__class__.__name__}") from exc
