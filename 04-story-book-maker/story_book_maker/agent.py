from typing import List

from google.adk.agents import Agent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from pydantic import BaseModel, Field

from .prompt import (
    ILLUSTRATOR_DESCRIPTION,
    ILLUSTRATOR_PROMPT,
    STORY_WRITER_DESCRIPTION,
    STORY_WRITER_PROMPT,
)
from .tools import generate_illustrations

MODEL = LiteLlm(model="openai/gpt-4o")


# ---------------------------------------------------------------------------
# 구조화 출력 스키마 — Story Writer 가 State 에 저장하는 데이터
# ---------------------------------------------------------------------------

class StoryPage(BaseModel):
    page_number: int = Field(description="페이지 번호 (1~5)")
    text: str = Field(description="해당 페이지의 동화 본문 (어린이 친화적, 한국어)")
    visual_description: str = Field(description="삽화 생성을 위한 상세 시각 묘사")


class StoryBook(BaseModel):
    title: str = Field(description="동화 제목")
    theme: str = Field(description="동화의 테마/주제")
    pages: List[StoryPage] = Field(description="5개의 페이지")


# ---------------------------------------------------------------------------
# Story Writer Agent — 테마 → 5페이지 구조화 동화 → state["story_book"]
# ---------------------------------------------------------------------------

story_writer_agent = Agent(
    name="StoryWriterAgent",
    model=MODEL,
    description=STORY_WRITER_DESCRIPTION,
    instruction=STORY_WRITER_PROMPT,
    output_schema=StoryBook,
    output_key="story_book",
)


# ---------------------------------------------------------------------------
# Illustrator Agent — state["story_book"] 읽어 페이지별 이미지 → Artifact
# ---------------------------------------------------------------------------

illustrator_agent = Agent(
    name="IllustratorAgent",
    model=MODEL,
    description=ILLUSTRATOR_DESCRIPTION,
    instruction=ILLUSTRATOR_PROMPT,
    tools=[generate_illustrations],
    output_key="illustrator_output",
)


# ---------------------------------------------------------------------------
# 파이프라인 — Writer 먼저(State 기록) → Illustrator(State 읽어 이미지)
# ---------------------------------------------------------------------------

root_agent = SequentialAgent(
    name="StoryBookMakerAgent",
    description="어린이 동화를 작성하고 각 페이지 삽화를 생성하는 파이프라인.",
    sub_agents=[story_writer_agent, illustrator_agent],
)
