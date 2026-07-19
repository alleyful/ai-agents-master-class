"""Build annotated chain-stitch learning cards from licensed/internal reference frames.

The source geometry is never regenerated. This script only adds deterministic
labels, focus rings, and arrows so hands, hook, yarn, and loops remain faithful
to the original instruction video.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = ROOT / "assets/techniques/crochet-chain-stitch/reference-frames"
CARD_DIR = ROOT / "assets/techniques/crochet-chain-stitch/reference-cards"
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

CORAL = (255, 92, 84, 255)
TEAL = (20, 113, 108, 255)
INK = (42, 48, 46, 255)
CREAM = (255, 251, 244, 238)
WHITE = (255, 255, 255, 255)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size=size)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color=CORAL) -> None:
    draw.line((start, end), fill=color, width=10)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    wing = 24
    spread = 0.58
    points = [
        end,
        (end[0] - wing * math.cos(angle - spread), end[1] - wing * math.sin(angle - spread)),
        (end[0] - wing * math.cos(angle + spread), end[1] - wing * math.sin(angle + spread)),
    ]
    draw.polygon(points, fill=color)


def focus_ring(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: tuple[int, int]) -> None:
    x, y = center
    rx, ry = radius
    draw.ellipse((x - rx, y - ry, x + rx, y + ry), outline=CORAL, width=10)


def info_panel(draw: ImageDraw.ImageDraw, step: int, title: str, instruction: str, timestamp: str) -> None:
    box = (748, 26, 1254, 170)
    draw.rounded_rectangle(box, radius=24, fill=CREAM, outline=(225, 210, 190, 255), width=2)
    draw.rounded_rectangle((770, 45, 878, 82), radius=18, fill=CORAL)
    draw.text((790, 48), f"STEP {step}", font=font(22), fill=WHITE)
    draw.text((770, 91), title, font=font(32), fill=INK)
    draw.text((770, 132), instruction, font=font(23), fill=TEAL)
    draw.rounded_rectangle((22, 664, 505, 706), radius=14, fill=(30, 34, 33, 176))
    draw.text((40, 672), f"바늘이야기 코바늘 마스터 #2 · {timestamp}", font=font(19), fill=WHITE)


CARDS = [
    {
        "file": "01-ready.png",
        "title": "활성 고리 확인",
        "instruction": "바늘 위 고리는 아직 세지 않아요",
        "timestamp": "02:10",
        "focus": ((704, 230), (62, 55)),
        "arrow": ((950, 190), (765, 220)),
    },
    {
        "file": "02-yarn-over.png",
        "title": "실을 바늘 홈에 걸기",
        "instruction": "작업실 아래로 바늘 홈을 가져가요",
        "timestamp": "02:34",
        "focus": ((590, 390), (84, 72)),
        "arrow": ((900, 190), (650, 345)),
    },
    {
        "file": "03-pull-through.png",
        "title": "기존 고리 통과",
        "instruction": "잡은 실만 고리 안으로 당겨요",
        "timestamp": "02:40",
        "focus": ((620, 465), (88, 78)),
        "arrow": ((900, 190), (690, 420)),
    },
    {
        "file": "04-new-loop.png",
        "title": "새 활성 고리",
        "instruction": "바늘에는 다시 고리 하나만 남아요",
        "timestamp": "02:55",
        "focus": ((662, 400), (86, 70)),
        "arrow": ((915, 190), (720, 360)),
    },
    {
        "file": "05-count-chain.png",
        "title": "완성된 V만 세기",
        "instruction": "바늘 아래 V가 사슬 1코예요",
        "timestamp": "12:00",
        "focus": ((690, 470), (70, 178)),
        "arrow": ((925, 190), (744, 360)),
    },
]


def main() -> None:
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    for index, spec in enumerate(CARDS, start=1):
        image = Image.open(FRAME_DIR / spec["file"]).convert("RGBA")
        focus_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        focus_draw = ImageDraw.Draw(focus_overlay)
        focus_ring(focus_draw, *spec["focus"])
        arrow(focus_draw, *spec["arrow"])
        focused = Image.alpha_composite(image, focus_overlay).convert("RGB")
        focused.save(CARD_DIR / f"focus-{index:02d}.jpg", quality=92, optimize=True)

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        info_panel(draw, index, spec["title"], spec["instruction"], spec["timestamp"])
        focus_ring(draw, *spec["focus"])
        arrow(draw, *spec["arrow"])
        if index == 5:
            draw.rounded_rectangle((565, 294, 752, 330), radius=16, fill=(20, 113, 108, 220))
            draw.text((586, 299), "활성 고리 · 제외", font=font(20), fill=WHITE)
        result = Image.alpha_composite(image, overlay).convert("RGB")
        result.save(CARD_DIR / f"card-{index:02d}.jpg", quality=92, optimize=True)

    board = Image.new("RGB", (1920, 1080), (249, 245, 238))
    board_draw = ImageDraw.Draw(board)
    board_draw.text((72, 42), "사슬뜨기 · 핵심 장면 5단계", font=font(54), fill=INK)
    board_draw.text(
        (74, 108),
        "실제 손·바늘·실의 위치를 그대로 두고, 확인할 지점만 표시했어요.",
        font=font(28),
        fill=TEAL,
    )
    positions = [(70, 175), (680, 175), (1290, 175), (375, 585), (985, 585)]
    for index, position in enumerate(positions, start=1):
        card = Image.open(CARD_DIR / f"card-{index:02d}.jpg").convert("RGB")
        card.thumbnail((560, 315), Image.Resampling.LANCZOS)
        shadow = Image.new("RGBA", (580, 335), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle((8, 8, 572, 327), radius=22, fill=(70, 55, 40, 28))
        board.paste(shadow, (position[0] - 10, position[1] - 8), shadow)
        board.paste(card, position)
    board_draw.text(
        (72, 1020),
        "출처 · 바늘이야기 코바늘 마스터 #2 사슬뜨기  |  내부 학습용 편집",
        font=font(22),
        fill=(100, 96, 90),
    )
    board.save(CARD_DIR / "overview-board.jpg", quality=92, optimize=True)


if __name__ == "__main__":
    main()
