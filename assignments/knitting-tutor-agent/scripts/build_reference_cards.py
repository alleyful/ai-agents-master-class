"""Extract curated technique frames from locally cached reference videos.

Download sources stay under /tmp and are never copied into the app. Only the
curated JPEG frames described by reference_card_manifest.json are persisted.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MANIFEST = Path(__file__).with_name("reference_card_manifest.json")
ADDITIONAL_TIMES = Path(__file__).with_name("additional_reference_times.json")
ASSET_ROOT = ROOT / "assets" / "techniques"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if ADDITIONAL_TIMES.is_file():
        from content.techniques import TECHNIQUES

        by_slug = {technique.slug: technique for technique in TECHNIQUES}
        additional = json.loads(ADDITIONAL_TIMES.read_text(encoding="utf-8"))
        for slug, source in additional.items():
            cards = by_slug[slug].reference_cards
            if len(cards) != len(source["times"]):
                raise ValueError(f"Reference card/time mismatch for {slug}")
            manifest[slug] = {
                "video_id": source["video_id"],
                "frames": [
                    {"time": time, "title": card["title"], "description": card["description"]}
                    for time, card in zip(source["times"], cards, strict=True)
                ],
            }
    for slug, lesson in manifest.items():
        source = Path(f"/tmp/knitcoach-{lesson['video_id']}.mp4")
        if not source.is_file():
            raise FileNotFoundError(f"Missing cached source video: {source}")
        output_dir = ASSET_ROOT / slug / "reference-cards"
        output_dir.mkdir(parents=True, exist_ok=True)
        for stale in output_dir.glob("focus-*.jpg"):
            stale.unlink()
        for index, frame in enumerate(lesson["frames"], start=1):
            output = output_dir / f"focus-{index:02d}.jpg"
            subprocess.run(
                [
                    "ffmpeg", "-loglevel", "error", "-y",
                    "-ss", str(frame["time"]), "-i", str(source),
                    "-frames:v", "1", "-q:v", "2", str(output),
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
