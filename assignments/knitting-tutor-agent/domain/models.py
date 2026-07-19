"""Provider-neutral request and response contracts for KnitCoach."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class JourneyType(StrEnum):
    START_FROM_ZERO = "start_from_zero"
    CONTINUE_LEARNING = "continue_learning"
    DIAGNOSE_PROJECT = "diagnose_project"
    RECREATE_FROM_PHOTO = "recreate_from_photo"
    EXPLAIN_PATTERN = "explain_pattern"
    START_FROM_MATERIALS = "start_from_materials"


class JourneyDefinition(BaseModel):
    title: str
    description: str
    prompt: str
    placeholder: str
    mode: str
    steps: tuple[str, str, str]
    icon: str


class LearnerProfile(BaseModel):
    level: Literal["unknown", "beginner", "confident_beginner", "intermediate"] = "unknown"
    preferred_style: Literal["unknown", "hands_on", "visual", "written"] = "unknown"
    goal: str = ""


class ProjectContext(BaseModel):
    project_type: str = ""
    tool_type: Literal["crochet", "needle_knitting", "unknown"] = "unknown"
    current_techniques: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class TutorRequest(BaseModel):
    journey: JourneyType
    message: str = Field(min_length=1)
    image_path: str | None = None
    learner_profile: LearnerProfile = Field(default_factory=LearnerProfile)
    project_context: ProjectContext | None = None


class TutorResponse(BaseModel):
    summary: str
    findings: list[str] = Field(default_factory=list)
    suggested_actions: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high", "unknown"] = "unknown"
    assumptions: list[str] = Field(default_factory=list)
    next_action: str = ""
