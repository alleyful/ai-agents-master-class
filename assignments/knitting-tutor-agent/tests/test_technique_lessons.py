"""Offline regression tests for the pre-authored technique lesson packs."""

import unittest

from content.symbols import technique_symbol_svg
from content.techniques import TECHNIQUES, list_techniques, resolve_techniques
from knitcoach import create_knitcoach, invoke_turn


class TechniqueLessonTests(unittest.TestCase):
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
        self.assertIn("쉘뜨기(shell stitch)", [item.name for item in list_techniques(tool="crochet", category="texture")])
        self.assertIn("코 막음(bind off)", [item.name for item in list_techniques(tool="needle_knitting", category="finishing")])

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
