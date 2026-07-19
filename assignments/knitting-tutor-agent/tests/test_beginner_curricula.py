"""Contracts for the pre-authored visual beginner project menu."""

import unittest
from pathlib import Path

from content.techniques import TECHNIQUE_CATALOG
from content.pattern_charts import mini_hat_chart_svg, radial_crochet_chart_svg
from content.purchases import PROJECT_PURCHASE_SPECS, build_purchase_plan
from domain.curricula import CURATED_BEGINNER_PROJECT_IDS, CURRICULA, detect_curriculum
from domain.project_patterns import MINI_HAT_CHART, PROJECT_PHASES, RADIAL_CROCHET_CHARTS, phase_index_for_step


class BeginnerCurriculaTests(unittest.TestCase):
    def test_curated_projects_are_complete_and_have_local_cover_images(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        self.assertEqual(6, len(CURATED_BEGINNER_PROJECT_IDS))
        for curriculum_id in CURATED_BEGINNER_PROJECT_IDS:
            with self.subTest(curriculum_id=curriculum_id):
                curriculum = CURRICULA[curriculum_id]
                self.assertTrue((project_root / curriculum.cover_image).is_file())
                self.assertGreaterEqual(len(curriculum.starter_kit), 3)
                self.assertGreaterEqual(len(curriculum.steps), 3)
                self.assertGreaterEqual(len(curriculum.project_guide), 4)
                self.assertTrue(curriculum.recommended_for)
                self.assertTrue(curriculum.yarn_requirement)
                self.assertTrue(curriculum.needle_size)
                self.assertTrue(curriculum.gauge)
                self.assertTrue(curriculum.finished_size)
                self.assertTrue(curriculum.construction)
                self.assertEqual("기호·영문 약어 기본 도안 + 초보자 한글 설명", curriculum.pattern_format)
                self.assertGreaterEqual(len(curriculum.beginner_pattern), 5)
                self.assertGreaterEqual(len(curriculum.written_pattern), 5)
                self.assertGreaterEqual(len(curriculum.symbol_legend), 3)
                for step in curriculum.steps:
                    self.assertIn(step.technique, TECHNIQUE_CATALOG)

    def test_each_visual_project_can_be_selected_by_its_korean_title(self) -> None:
        for curriculum_id in CURATED_BEGINNER_PROJECT_IDS:
            curriculum = CURRICULA[curriculum_id]
            with self.subTest(title=curriculum.title):
                self.assertEqual(curriculum_id, detect_curriculum(f"{curriculum.title}을 선택할게요"))

    def test_coaster_has_a_complete_symbol_pattern_and_round_by_round_steps(self) -> None:
        coaster = CURRICULA["crochet-round-coaster"]
        self.assertEqual(9, len(coaster.steps))
        self.assertEqual(9, len(coaster.written_pattern))
        self.assertIn("MR = 매직링", coaster.symbol_legend)
        self.assertEqual(["매직링", "짧은뜨기", "짧은뜨기 늘려뜨기", "빼뜨기"], coaster.pattern_techniques)
        self.assertIn("1단", coaster.steps[0].title)
        self.assertIn("8단", coaster.steps[7].title)
        self.assertIn("마무리", coaster.steps[8].title)

    def test_every_curated_project_has_pre_authored_semantic_phases(self) -> None:
        self.assertEqual(set(CURATED_BEGINNER_PROJECT_IDS), set(PROJECT_PHASES))
        for curriculum_id in CURATED_BEGINNER_PROJECT_IDS:
            curriculum = CURRICULA[curriculum_id]
            covered = [step_id for phase in PROJECT_PHASES[curriculum_id] for step_id in phase.step_ids]
            self.assertEqual([step.id for step in curriculum.steps], covered)

    def test_first_garter_scarf_starts_with_cast_on_without_a_gauge_swatch(self) -> None:
        scarf = CURRICULA["needle-garter-scarf"]
        first = scarf.steps[0]
        self.assertEqual("cast-on", first.id)
        self.assertIn("코잡기 18코", first.title)
        self.assertNotIn("게이지", first.title)
        self.assertNotIn("게이지", first.practice)
        self.assertNotIn("샘플", scarf.gauge)
        whole_pattern = " ".join(scarf.written_pattern)
        self.assertIn("1–18단", whole_pattern)
        self.assertIn("코막음", whole_pattern)

    def test_coaster_chart_is_deterministic_and_matches_eight_round_spiral(self) -> None:
        chart = RADIAL_CROCHET_CHARTS["crochet-round-coaster"]
        self.assertEqual("continuous_spiral", chart.construction)
        self.assertEqual([6, 12, 18, 24, 30, 36, 42, 48], [item.stitch_count for item in chart.rounds])
        svg = radial_crochet_chart_svg(chart, 2)
        self.assertIn("MR", svg)
        self.assertIn("chart-current", svg)
        self.assertNotIn("chain", svg)
        self.assertEqual(1, phase_index_for_step("crochet-round-coaster", "round-8"))

    def test_mini_hat_has_a_complete_count_checked_symbol_chart(self) -> None:
        self.assertEqual("crochet-mini-hat-keyring", MINI_HAT_CHART.project_id)
        self.assertEqual(
            [6, 12, 18, 24, 24, 24, 24, 24, 30, 36, 36],
            [item.stitch_count for item in MINI_HAT_CHART.rounds],
        )
        self.assertEqual("BLO X 24", MINI_HAT_CHART.rounds[4].notation)
        svg = mini_hat_chart_svg(MINI_HAT_CHART, [5, 6, 7, 8])
        self.assertIn("5단 · 24코 · BLO", svg)
        self.assertIn("11단 · 36코", svg)

    def test_fishbread_matches_the_12_round_video_pattern(self) -> None:
        fishbread = CURRICULA["crochet-fishbread-keyring"]
        pattern = "\n".join(fishbread.written_pattern)
        self.assertIn("GNK16UCra7Q", fishbread.reference_video_url)
        self.assertIn("(X 1, V 1) × 3", pattern)
        self.assertIn("(X 3, A 1) × 3", pattern)
        self.assertIn("6INC", pattern)
        self.assertIn("3HDC", pattern)
        self.assertNotIn("3DC", pattern)
        self.assertIn("솜", pattern)
        self.assertIn("기둥 사슬 1코", " ".join(fishbread.assumptions))
        self.assertEqual(13, len(fishbread.steps))
        self.assertIn("12단", fishbread.steps[11].title)
        self.assertIn("마무리", fishbread.steps[12].title)
        beginner_pattern = "\n".join(fishbread.beginner_pattern)
        self.assertIn("짧은뜨기 3코와 늘려뜨기 1회", beginner_pattern)
        self.assertIn("이 순서를 네 번 반복", beginner_pattern)
        self.assertNotIn("CH1", beginner_pattern)
        self.assertNotIn("3HDC", beginner_pattern)

    def test_crochet_pouch_is_worked_in_joined_rounds_without_side_seams(self) -> None:
        pouch = CURRICULA["crochet-flat-pouch"]
        standard = "\n".join(pouch.written_pattern)
        beginner = "\n".join(pouch.beginner_pattern)
        self.assertIn("foundation CH 반대쪽", standard)
        self.assertIn("SLST [40]", standard)
        self.assertIn("R2–24 · CH1, SC 40, SLST [40]", standard)
        self.assertIn("사슬의 반대쪽", beginner)
        self.assertIn("편물을 뒤집지", beginner)
        self.assertIn("기둥 사슬 1코", beginner)
        self.assertNotIn("반으로 접", beginner)
        self.assertNotIn("옆선", beginner)
        self.assertNotIn("seams", [step.id for step in pouch.steps])
        self.assertEqual("base-round-1", pouch.steps[0].id)
        self.assertEqual(5, len(pouch.steps))

    def test_every_curated_project_pattern_has_a_finish_stage(self) -> None:
        finish_terms = ("마무리", "실 정리", "키링", "조임끈")
        for curriculum_id in CURATED_BEGINNER_PROJECT_IDS:
            with self.subTest(curriculum_id=curriculum_id):
                pattern = " ".join(CURRICULA[curriculum_id].written_pattern)
                self.assertTrue(any(term in pattern for term in finish_terms))

    def test_each_curated_project_has_a_visual_purchase_plan_and_preview(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        for curriculum_id in CURATED_BEGINNER_PROJECT_IDS:
            with self.subTest(curriculum_id=curriculum_id):
                self.assertIn(curriculum_id, PROJECT_PURCHASE_SPECS)
                plan = build_purchase_plan(curriculum_id)
                self.assertTrue(plan["yarn"]["name"])
                self.assertGreaterEqual(len(plan["tools"]), 4)
                self.assertGreaterEqual(len(plan["project_guide"]), 4)
                self.assertTrue(plan["written_pattern"])
                self.assertTrue(plan["gauge"])
                self.assertTrue(plan["finished_size"])
                self.assertTrue(plan["construction"])
                self.assertTrue(plan["techniques"])
                for tool in plan["tools"]:
                    self.assertTrue(tool["image"])
                    self.assertTrue((project_root / tool["image"]).is_file())


if __name__ == "__main__":
    unittest.main()
