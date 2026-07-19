"""Offline regression tests for the pre-authored technique lesson packs."""

import unittest
from pathlib import Path

from content.symbols import technique_symbol_svg
from content.techniques import TECHNIQUES, list_techniques, resolve_techniques
from knitcoach import create_knitcoach, invoke_turn


class TechniqueLessonTests(unittest.TestCase):
    def test_chain_pilot_video_is_ready_for_offline_playback(self) -> None:
        chain = next(technique for technique in TECHNIQUES if technique.slug == "crochet-chain-stitch")
        video_path = Path(__file__).resolve().parent.parent / chain.video_asset_path
        self.assertEqual("ready", chain.video_status)
        self.assertEqual(2, len(chain.reference_videos))
        self.assertTrue(all("바늘이야기" in item["title"] for item in chain.reference_videos))
        self.assertIn("eCiESFasa0g", chain.reference_videos[1]["url"])
        self.assertEqual(5, len(chain.reference_card_paths))
        self.assertEqual(5, len(chain.reference_cards))
        self.assertTrue(all((Path(__file__).resolve().parent.parent / path).is_file() for path in chain.reference_card_paths))
        self.assertTrue((Path(__file__).resolve().parent.parent / chain.reference_board_path).is_file())
        self.assertTrue(video_path.is_file())
        self.assertGreater(video_path.stat().st_size, 100_000)

    def test_source_frame_review_cards_are_available_for_core_crochet_lessons(self) -> None:
        card_slugs = {
            "crochet-chain-stitch",
            "single-crochet",
            "half-double-crochet",
            "double-crochet",
            "magic-ring",
            "round-crochet",
            "slip-stitch",
            "slip-knot",
            "treble-crochet",
            "single-crochet-increase",
            "single-crochet-decrease",
            "double-crochet-decrease",
            "front-loop-only",
            "back-loop-only",
            "front-post-double-crochet",
            "back-post-double-crochet",
            "three-dc-cluster",
            "puff-stitch",
            "popcorn-stitch",
            "shell-stitch",
            "casting-on",
            "knit-stitch",
            "purl-stitch",
            "ribbing",
            "bind-off",
            "stockinette-stitch",
            "garter-stitch",
            "seed-stitch",
        }
        card_slugs = {technique.slug for technique in TECHNIQUES}
        base_dir = Path(__file__).resolve().parent.parent
        for technique in (item for item in TECHNIQUES if item.slug in card_slugs):
            with self.subTest(technique=technique.slug):
                self.assertTrue(technique.reference_videos)
                self.assertGreaterEqual(len(technique.reference_cards), 5)
                self.assertTrue(all((base_dir / card["path"]).is_file() for card in technique.reference_cards))
                self.assertTrue(all(card["title"] and card["description"] for card in technique.reference_cards))

    def test_review_cards_follow_each_techniques_actual_core_motion(self) -> None:
        expected_titles = {
            "single-crochet": ["완성 사슬 준비", "사슬 뒷산 찾기", "바늘 넣기", "두 고리 만들기", "한 코 완성"],
            "half-double-crochet": ["실 한 번 감기", "사슬 뒷산에 넣기", "고리 끌어오기", "세 고리 확인", "한 코 완성"],
            "double-crochet": ["실 한 번 감기", "사슬 뒷산에 넣기", "세 고리 만들기", "두 고리만 통과", "남은 두 고리 통과"],
            "magic-ring": ["손가락에 실 걸기", "실을 교차해 링 만들기", "링 안으로 바늘 넣기", "작업실 끌어오기", "사슬로 시작 고정"],
            "round-crochet": ["완성 매직링에 넣기", "첫 짧은뜨기 완성", "첫 코 표시", "한 바퀴 뜨고 중심 조이기", "첫 코에 단 연결"],
            "slip-stitch": ["연결할 코 찾기", "바늘 넣기", "작업실 걸기", "두 고리 연속 통과", "낮은 연결 확인"],
            "slip-knot": ["실로 원 만들기", "실 교차하기", "고리 안으로 바늘 넣기", "작업실 잡기", "새 고리 끌어오기", "바늘 굵기에 맞추기"],
            "treble-crochet": ["기둥 높이 준비", "실 두 번 감기", "다음 코에 넣기", "네 고리 만들기", "첫 두 고리 통과", "둘째 두 고리 통과", "마지막 두 고리 통과", "높이와 머리 확인"],
            "single-crochet-increase": ["늘릴 한 코 찾기", "첫 짧은뜨기 완성", "같은 코에 다시 넣기", "두 고리 만들기", "둘째 짧은뜨기 완성", "두 V 머리 확인"],
            "single-crochet-decrease": ["모을 두 코 찾기", "첫 코에 넣기", "첫 고리 끌어오기", "다음 코에 넣기", "세 고리 만들기", "세 고리 함께 통과", "한 V 머리 확인"],
            "double-crochet-decrease": ["모을 두 코 준비", "첫 코에 넣기", "첫 세 고리 확인", "첫 코 미완성으로 남기기", "둘째 코에 넣기", "둘째 고리 끌어오기", "둘째 코도 미완성", "세 고리 함께 마무리"],
            "front-loop-only": ["V 머리 두 가닥 확인", "앞고리 한 가닥에 넣기", "작업실 끌어오기", "짧은뜨기 완성", "남은 뒤고리 선 확인"],
            "back-loop-only": ["V 머리 두 가닥 확인", "뒤고리 한 가닥에 넣기", "작업실 끌어오기", "짧은뜨기 완성", "남은 앞고리 능선 확인"],
            "front-post-double-crochet": ["실 한 번 감기", "감쌀 기둥 찾기", "앞에서 뒤로 넣기", "뒤에서 다시 앞으로", "기둥 둘레로 고리 끌기", "솟은 기둥코 완성"],
            "back-post-double-crochet": ["실 한 번 감기", "감쌀 기둥 찾기", "뒤에서 앞으로 넣기", "기둥을 바늘 뒤에 두기", "앞에서 다시 뒤로", "기둥 둘레로 고리 끌기", "들어간 기둥코 완성"],
            "three-dc-cluster": ["첫 코를 시작할 위치", "첫 기둥 미완성", "둘째 기둥 시작", "둘째 기둥도 미완성", "셋째 기둥 시작", "기둥 3개·고리 4개 확인", "모든 고리 닫기", "꼭짓점 하나 확인"],
            "puff-stitch": ["실 한 번 감기", "같은 공간에 넣기", "긴 고리 끌어올리기", "같은 위치에서 반복", "고리 높이 맞추기", "모인 고리 한 번에 닫기", "사슬로 고정"],
            "popcorn-stitch": ["다섯 코를 넣을 위치", "첫 한길긴뜨기 완성", "같은 위치에 계속 뜨기", "다섯 번째 코 완성", "다섯 V 머리 확인", "바늘을 빼 첫 코에 넣기", "마지막 고리 다시 걸기", "첫 코 사이로 당겨 완성"],
            "shell-stitch": ["조개를 넣을 한 코", "첫 한길긴뜨기", "같은 밑코에 둘째 코", "왼쪽 기둥 두 코 확인", "가운데 사슬 1코", "같은 밑코로 돌아가기", "한길긴뜨기 두 코 더", "2코·사슬·2코 확인"],
            "casting-on": ["꼬리실 길이 준비", "엄지·검지에 실 걸기", "엄지 고리 아래로 넣기", "검지 작업실 걸기", "엄지 고리로 끌어오기", "새 코 조이기", "같은 방향의 코 확인"],
            "knit-stitch": ["작업실을 뒤에 두기", "앞에서 뒤로 바늘 넣기", "작업실 감기", "새 고리 끌어오기", "헌 코 빼기", "V 방향 확인"],
            "purl-stitch": ["작업실을 앞으로 옮기기", "오른쪽에서 왼쪽으로 넣기", "앞쪽에서 실 감기", "새 고리를 뒤로 빼기", "헌 코 빼기", "가로 마디 확인"],
            "ribbing": ["겉뜨기 1코", "실을 바늘 사이로 앞으로", "안뜨기 1코", "실을 바늘 사이로 뒤로", "K1·P1 반복", "세로 골 확인"],
            "bind-off": ["첫 두 코 겉뜨기", "앞 코와 뒤 코 구분", "왼바늘로 앞 코 잡기", "뒤 코 위로 덮어씌우기", "오른바늘 한 코 확인", "다음 코 뜨고 반복", "느슨한 마감선 확인"],
            "stockinette-stitch": ["겉면에서 겉뜨기", "겉면 단 끝 확인", "뒷면에서 실 앞으로", "뒷면에서 안뜨기", "앞뒤 한 단씩 반복", "겉면 V 조직 확인"],
            "garter-stitch": ["첫 단 모두 겉뜨기", "단 끝에서 편물 돌리기", "뒷면도 모두 겉뜨기", "두 단을 한 쌍으로 반복", "가로 능선 세기", "양면 조직 확인"],
            "seed-stitch": ["1코 1단 배열 확인", "첫 단 겉뜨기 1코", "안뜨기 1코와 반복", "편물을 돌려 아래 코 읽기", "겉코 위에는 안뜨기", "안코 위에는 겉뜨기", "바둑판 질감 확인"],
        }
        by_slug = {technique.slug: technique for technique in TECHNIQUES}
        for slug, titles in expected_titles.items():
            with self.subTest(technique=slug):
                self.assertEqual(titles, [card["title"] for card in by_slug[slug].reference_cards])

    def test_all_lesson_packs_are_complete(self) -> None:
        self.assertEqual(40, len(TECHNIQUES))
        self.assertEqual(20, len(list_techniques(tool="crochet")))
        self.assertEqual(20, len(list_techniques(tool="needle_knitting")))
        self.assertEqual(40, len({technique.slug for technique in TECHNIQUES}))
        self.assertEqual(40, len({technique.name for technique in TECHNIQUES}))
        for technique in TECHNIQUES:
            with self.subTest(technique=technique.name):
                self.assertTrue(technique.steps)
                self.assertEqual(len(technique.common_mistakes), len(technique.mistake_fixes))
                self.assertTrue(technique.learning_goal)
                self.assertTrue(technique.practice)
                self.assertTrue(technique.success_check)
                self.assertTrue(technique.aliases)
                self.assertIn("8-second", technique.video_generation_prompt)
                self.assertIn("<svg", technique_symbol_svg(technique.symbol_key, technique.abbreviation))

    def test_each_named_technique_routes_to_its_own_lesson(self) -> None:
        for technique in TECHNIQUES:
            korean_name = technique.name.split("(")[0]
            with self.subTest(technique=korean_name):
                result = invoke_turn(create_knitcoach(), f"{korean_name}를 알려줘", f"lesson-{technique.slug}")
                self.assertEqual("learn_technique", result["intent"])
                self.assertEqual([technique.name], result["detected_techniques"])
                self.assertIn(korean_name, result["user_response"])
                self.assertIn(technique.learning_goal, result["user_response"])

    def test_chain_request_does_not_return_generic_single_crochet_pattern(self) -> None:
        result = invoke_turn(create_knitcoach(), "사슬뜨기를 알려줘", "chain-regression")
        self.assertEqual("text", result["input_type"])
        self.assertEqual("learn_technique", result["intent"])
        self.assertNotIn("짧은뜨기 5단", result["user_response"])

    def test_actual_pattern_text_still_routes_to_conversion(self) -> None:
        result = invoke_turn(create_knitcoach(), "ch 12, sc in each ch", "pattern-regression")
        self.assertEqual("pattern_text", result["input_type"])
        self.assertEqual("convert_pattern", result["intent"])

    def test_search_and_category_filters_expand_with_catalog(self) -> None:
        self.assertEqual(["바늘비우기(yarn over)"], [item.name for item in list_techniques(query="YO")])
        self.assertIn("조개뜨기(shell stitch)", [item.name for item in list_techniques(tool="crochet", category="texture")])
        self.assertIn("덮어씌워 코막음(basic bind off)", [item.name for item in list_techniques(tool="needle_knitting", category="finishing")])

    def test_names_and_symbol_roles_do_not_present_learning_icons_as_chart_symbols(self) -> None:
        by_slug = {technique.slug: technique for technique in TECHNIQUES}
        self.assertEqual(
            "매직링으로 원형 시작하기(crocheting in the round)",
            by_slug["round-crochet"].name,
        )
        self.assertEqual("in rounds", by_slug["round-crochet"].abbreviation)
        self.assertEqual("learning", by_slug["round-crochet"].display_symbol_kind)
        self.assertFalse(by_slug["round-crochet"].abbreviation_standard)
        self.assertEqual("learning", by_slug["magic-ring"].display_symbol_kind)
        self.assertFalse(by_slug["magic-ring"].abbreviation_standard)
        self.assertEqual("modifier", by_slug["front-loop-only"].display_symbol_kind)
        self.assertEqual("modifier", by_slug["back-loop-only"].display_symbol_kind)
        self.assertEqual("한길긴뜨기 3코 구슬뜨기(3-dc cluster)", by_slug["three-dc-cluster"].name)
        self.assertEqual("standard", by_slug["three-dc-cluster"].display_symbol_kind)
        self.assertEqual("긴 고리 구슬뜨기(puff stitch)", by_slug["puff-stitch"].name)
        self.assertEqual("learning", by_slug["puff-stitch"].display_symbol_kind)
        self.assertFalse(by_slug["puff-stitch"].abbreviation_standard)
        self.assertEqual("조개뜨기(shell stitch)", by_slug["shell-stitch"].name)
        self.assertEqual("learning", by_slug["shell-stitch"].display_symbol_kind)
        self.assertFalse(by_slug["shell-stitch"].abbreviation_standard)
        self.assertEqual("1×1 고무뜨기(1x1 ribbing)", by_slug["ribbing"].name)
        self.assertEqual("롱테일 코잡기(long-tail cast on)", by_slug["casting-on"].name)
        self.assertEqual("덮어씌워 코막음(basic bind off)", by_slug["bind-off"].name)
        self.assertEqual("sl1p wyib", by_slug["slip-stitch-knitting"].abbreviation)
        self.assertTrue(all(
            technique.display_symbol_kind == "learning"
            for technique in TECHNIQUES
            if technique.tool_type == "needle_knitting"
        ))

    def test_legacy_beginner_terms_still_find_the_more_precise_lesson_names(self) -> None:
        self.assertEqual(
            ["매직링으로 원형 시작하기(crocheting in the round)"],
            [item.name for item in resolve_techniques("원형뜨기 늘림을 배우고 싶어요")],
        )
        self.assertEqual(
            ["1×1 고무뜨기(1x1 ribbing)"],
            [item.name for item in resolve_techniques("고무뜨기를 연습하고 싶어요")],
        )

    def test_longest_aliases_win_without_losing_multiple_pattern_stitches(self) -> None:
        self.assertEqual(
            ["한길긴뜨기(double crochet)"],
            [item.name for item in resolve_techniques("한길긴뜨기를 알려줘")],
        )
        self.assertEqual(
            ["긴뜨기(half double crochet)"],
            [item.name for item in resolve_techniques("hdc를 알려줘")],
        )
        names = [item.name for item in resolve_techniques("ch 12, sc in each ch, then dc")]
        self.assertEqual(
            ["사슬뜨기(chain stitch)", "짧은뜨기(single crochet)", "한길긴뜨기(double crochet)"],
            names,
        )
        self.assertEqual(
            ["왼코 늘림(make one left)"],
            [item.name for item in resolve_techniques("M1L을 연습하고 싶어")],
        )


if __name__ == "__main__":
    unittest.main()
