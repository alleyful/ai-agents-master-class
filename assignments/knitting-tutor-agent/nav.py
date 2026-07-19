"""Information architecture for the work-oriented KnitCoach LNB."""

import os


PHOTO_PATTERN_UI_ENABLED = os.getenv("KNITCOACH_ENABLE_PHOTO_PATTERN_UI") == "1"

WORKSHOP_TOOLS = [
    ("technique_library", "⌘", "기법 보관함"),
    ("tool_library", "◫", "도구 보관함"),
]

if PHOTO_PATTERN_UI_ENABLED:
    WORKSHOP_TOOLS.insert(0, ("pattern", "▧", "사진 속 작품 만들기"))
