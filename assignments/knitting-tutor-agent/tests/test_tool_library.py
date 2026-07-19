import unittest
from pathlib import Path

from content.tools import BRAND_GUIDES, TOOL_DIAMETER_TABLES, TOOL_GUIDES, TOOL_IMAGE_PATHS, TOOL_LENGTH_TABLES, calculate_gauge, list_tools, recommend_tools, resolve_tools


class ToolLibraryTests(unittest.TestCase):
    def test_catalog_has_expected_families(self):
        slugs = {item.slug for item in TOOL_GUIDES}
        self.assertTrue({"single-crochet-hook", "tunisian-hook", "fixed-circular", "interchangeable-needles", "dpn", "short-long-tips"} <= slugs)
        self.assertGreaterEqual(len(list_tools(craft="crochet")), 7)
        self.assertGreaterEqual(len(list_tools(craft="needle_knitting")), 10)

    def test_aliases_resolve_korean_tool_names(self):
        self.assertEqual("tunisian-hook", resolve_tools("아후강 바늘이 궁금해")[0].slug)
        self.assertEqual("dpn", resolve_tools("장갑 바늘로 양말 가능해?")[0].slug)
        self.assertEqual(["tunisian-hook"], [item.slug for item in resolve_tools("아후강 코바늘")])

    def test_beginner_recommendation_is_budget_first(self):
        advice = " ".join(recommend_tools("첫 목도리 가성비 대바늘 추천", "needle_knitting", "beginner"))
        self.assertIn("입문용", advice)
        self.assertNotIn("큰 세트를 사", advice)

    def test_gauge_calculation_and_direction(self):
        tight = calculate_gauge(24, 30, 10, 10, target_stitches=20)
        loose = calculate_gauge(16, 24, 10, 10, target_stitches=20)
        self.assertEqual(24, tight["stitches_10cm"])
        self.assertIn("더 큰 바늘", tight["advice"])
        self.assertIn("더 작은 바늘", loose["advice"])

    def test_brand_guidance_includes_budget_and_named_systems(self):
        names = {brand.name for brand in BRAND_GUIDES}
        self.assertTrue({"다이소·무명 입문 제품", "Tulip", "KnitPro", "ChiaoGoo", "addi"} <= names)

    def test_every_tool_has_a_local_illustration(self):
        root = Path(__file__).resolve().parent.parent
        self.assertEqual({item.slug for item in TOOL_GUIDES}, set(TOOL_IMAGE_PATHS))
        for path in TOOL_IMAGE_PATHS.values():
            self.assertTrue((root / path).is_file(), path)

    def test_basic_crochet_hook_has_korean_size_to_mm_table(self):
        rows = TOOL_DIAMETER_TABLES["single-crochet-hook"]
        by_size = {row["marking"]: row["mm"] for row in rows}
        self.assertEqual("2.50mm", by_size["4/0"])
        self.assertEqual("6.00mm", by_size["10/0"])

    def test_needle_diameter_and_length_are_separate_dimensions(self):
        needle_slugs = {"straight-needles", "fixed-circular", "interchangeable-needles", "dpn", "short-long-tips"}
        self.assertTrue(needle_slugs <= set(TOOL_DIAMETER_TABLES))
        self.assertTrue(needle_slugs <= set(TOOL_LENGTH_TABLES))
        for slug in needle_slugs:
            self.assertTrue(all("mm" in row and "length" not in row for row in TOOL_DIAMETER_TABLES[slug]))
            self.assertTrue(all("length" in row and "mm" not in row for row in TOOL_LENGTH_TABLES[slug]))

    def test_circular_needle_length_measurement_is_explicit(self):
        fixed = TOOL_LENGTH_TABLES["fixed-circular"][0]
        self.assertIn("완성 길이", fixed["measured_as"])
        interchangeable = {row["length"]: row["measured_as"] for row in TOOL_LENGTH_TABLES["interchangeable-needles"]}
        self.assertEqual("팁 결합 후 약 60cm", interchangeable["실제 케이블 35cm"])

    def test_tunisian_hook_uses_corrected_illustration(self):
        self.assertEqual("assets/tools/tunisian-hook-v2.png", TOOL_IMAGE_PATHS["tunisian-hook"])


if __name__ == "__main__":
    unittest.main()
