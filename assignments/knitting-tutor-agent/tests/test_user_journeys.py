"""Offline contracts and routing regression tests for the six user journeys."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from conversation_router import ConversationAction, ConversationDecision, SupportModule
from domain.curricula import activate_learning_program, new_learning_program
from domain.journeys import JOURNEY_DEFINITIONS, infer_journey
from domain.models import JourneyType, TutorRequest, TutorResponse
from knitcoach import ImageObservation, create_knitcoach, detect_input_type, detect_intent, invoke_turn, is_knitting_scope


def make_decision(action: ConversationAction, **overrides) -> ConversationDecision:
    payload = {
        "action": action,
        "curriculum_id": "",
        "suggested_curriculum_ids": [],
        "support_modules": [],
        "technique_names": [],
        "tool_slugs": [],
        "assistant_reply": "",
        "follow_up_question": "",
        "reasoning_summary": "테스트용 분류 근거",
    }
    payload.update(overrides)
    return ConversationDecision(**payload)


class UserJourneyTests(unittest.TestCase):
    def test_model_answers_a_general_knitting_question_without_opening_project_ui(self) -> None:
        decision = make_decision(
            action=ConversationAction.GENERAL_QUESTION,
            assistant_reply="뜨개질은 실을 고리로 연결해 편물을 만드는 작업이에요. 코바늘과 대바늘이 대표적입니다.",
            reasoning_summary="작품 선택이 아닌 일반적인 뜨개 개념 질문",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=decision):
            result = invoke_turn(create_knitcoach(), "뜨개질이 뭐야?", "model-general-question")

        self.assertTrue(result["model_routed"])
        self.assertEqual("general_question", result["conversation_action"])
        self.assertFalse(result["program_turn"])
        self.assertEqual("none", result["project_view"])
        self.assertEqual(decision.assistant_reply, result["user_response"])
        self.assertEqual({}, result["learning_program"])

    def test_model_routes_curated_project_selection_into_the_pre_authored_flow(self) -> None:
        decision = make_decision(
            action=ConversationAction.SELECT_PROJECT,
            curriculum_id="crochet-round-coaster",
            reasoning_summary="사용자가 검수된 티코스터 작품 제작을 원함",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=decision):
            result = invoke_turn(create_knitcoach(), "티코스터를 떠보고 싶어", "model-project-selection")

        self.assertTrue(result["model_routed"])
        self.assertEqual("crochet-round-coaster", result["learning_program"]["curriculum_id"])
        self.assertEqual("awaiting_tools", result["learning_program"]["status"])
        self.assertIn("시작 준비물", result["user_response"])

    def test_model_distinguishes_explaining_current_step_from_advancing(self) -> None:
        program = activate_learning_program(new_learning_program("crochet-round-coaster"))
        explain = make_decision(
            action=ConversationAction.EXPLAIN_CURRENT_STEP,
            reasoning_summary="1단계 설명 요청이며 완료 보고가 아님",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=explain):
            current = invoke_turn(
                create_knitcoach(),
                "1단계부터 자세히 설명해줘",
                "model-current-step",
                learning_program=program,
            )

        self.assertEqual(0, current["learning_program"]["current_step"])
        self.assertEqual([], current["learning_program"]["completed_steps"])
        self.assertEqual("step", current["project_view"])
        self.assertIn("1단", current["user_response"])

        advance = make_decision(
            action=ConversationAction.ADVANCE_STEP,
            reasoning_summary="현재 작품에서 다음 단계 이동 요청",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=advance):
            following = invoke_turn(
                create_knitcoach(),
                "다음 단계로 가자",
                "model-next-step",
                learning_program=current["learning_program"],
            )

        self.assertEqual(1, following["learning_program"]["current_step"])
        self.assertEqual(["round-1"], following["learning_program"]["completed_steps"])
        self.assertEqual("step", following["project_view"])
        self.assertIn("2단", following["user_response"])

    def test_model_can_pair_a_contextual_answer_with_authored_technique_materials(self) -> None:
        decision = make_decision(
            action=ConversationAction.TECHNIQUE_QUESTION,
            support_modules=[SupportModule.DIRECT_ANSWER, SupportModule.TECHNIQUE_LIBRARY],
            technique_names=["짧은뜨기(single crochet)"],
            assistant_reply="짧은뜨기는 코에 바늘을 넣고 실을 끌어온 뒤, 바늘의 두 고리를 한 번에 빼는 낮고 단단한 코예요.",
            follow_up_question="사슬 바탕에 연습할까요, 원형의 다음 단에 연습할까요?",
            reasoning_summary="동작 설명과 실제 연습 자료가 함께 필요한 기법 질문",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=decision):
            result = invoke_turn(create_knitcoach(), "낮고 단단한 코는 어떻게 떠?", "model-technique-support")

        self.assertEqual(["짧은뜨기(single crochet)"], result["detected_techniques"])
        self.assertIn("technique_library", result["support_modules"])
        self.assertEqual("짧은뜨기(single crochet)", result["technique_resources"][0]["technique"])
        self.assertIn("기법 카드", result["user_response"])
        self.assertIn("사슬 바탕에 연습할까요", result["user_response"])
        self.assertTrue(result["practice_plan"])
        self.assertEqual("none", result["project_view"])

    def test_model_can_answer_a_tool_question_with_the_exact_tool_library_item(self) -> None:
        decision = make_decision(
            action=ConversationAction.TOOL_QUESTION,
            support_modules=[SupportModule.DIRECT_ANSWER, SupportModule.TOOL_LIBRARY],
            tool_slugs=["stitch-markers"],
            assistant_reply="표시링은 단의 시작이나 반복 위치를 잊지 않도록 걸어 두는 작은 표식이에요.",
            reasoning_summary="표시링 정의와 생김새 자료가 필요한 도구 질문",
        )
        program = activate_learning_program(new_learning_program("crochet-round-coaster"))
        with patch("knitcoach.route_conversation_with_model", return_value=decision):
            result = invoke_turn(
                create_knitcoach(),
                "첫 코 자리를 자꾸 잊어버리는데 뭘 걸어두면 돼?",
                "model-tool-support",
                learning_program=program,
            )

        self.assertEqual(["stitch-markers"], result["selected_tool_slugs"])
        self.assertIn("tool_library", result["support_modules"])
        self.assertTrue(any("표시링" in item for item in result["required_tools"]))
        self.assertEqual(program, result["learning_program"])
        self.assertFalse(result["program_turn"])
        self.assertEqual("none", result["project_view"])
        self.assertIn("표시링은", result["user_response"])

    def test_model_can_recommend_curated_projects_without_forcing_a_selection(self) -> None:
        decision = make_decision(
            action=ConversationAction.OTHER_KNITTING,
            support_modules=[SupportModule.DIRECT_ANSWER, SupportModule.CURATED_PROJECT],
            suggested_curriculum_ids=["crochet-round-coaster", "needle-garter-scarf"],
            assistant_reply="처음이라면 빨리 완성되는 코바늘 티코스터나 같은 동작을 반복하는 대바늘 목도리가 좋아요. 아래 두 작품을 비교해 보세요.",
            follow_up_question="단단한 작은 소품과 부드러운 목도리 중 어느 쪽이 더 끌리나요?",
            reasoning_summary="입문자가 작품 비교를 원하지만 아직 하나를 선택하지 않음",
        )
        with patch("knitcoach.route_conversation_with_model", return_value=decision):
            result = invoke_turn(create_knitcoach(), "완전 초보인데 첫 작품을 추천해줘", "model-project-recommendations")

        self.assertEqual(
            ["crochet-round-coaster", "needle-garter-scarf"],
            result["project_suggestions"],
        )
        self.assertEqual({}, result["learning_program"])
        self.assertFalse(result["program_turn"])
        self.assertIn("아래 두 작품", result["user_response"])
        self.assertIn("어느 쪽이 더 끌리나요", result["user_response"])

    def test_all_six_journeys_have_complete_ui_copy(self) -> None:
        self.assertEqual(set(JourneyType), set(JOURNEY_DEFINITIONS))
        self.assertEqual(6, len(JOURNEY_DEFINITIONS))
        for journey, definition in JOURNEY_DEFINITIONS.items():
            with self.subTest(journey=journey):
                self.assertTrue(definition.title)
                self.assertTrue(definition.placeholder)
                self.assertEqual(3, len(definition.steps))

    def test_eval_cases_route_without_a_model(self) -> None:
        path = Path(__file__).resolve().parent.parent / "evals" / "cases.jsonl"
        cases = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        self.assertEqual(19, len(cases))
        for case in cases:
            with self.subTest(case=case["id"]):
                input_type = "image_path" if case.get("has_image") else detect_input_type(case["input"])
                intent = "generate_pattern" if case.get("task") == "generate_pattern" else detect_intent(case["input"], input_type)
                actual = infer_journey(
                    case["input"],
                    input_type=input_type,
                    intent=intent,
                    has_image=case.get("has_image", False),
                    task=case.get("task", "tutor"),
                )
                self.assertEqual(case["journey"], actual.value)

    def test_graph_exposes_journey_metadata(self) -> None:
        result = invoke_turn(create_knitcoach(), "완전 처음인데 뜨개질을 시작하고 싶어요", "journey-smoke")
        self.assertEqual(JourneyType.START_FROM_ZERO, result["journey"])
        self.assertIn("완성하고 싶은 모습", result["user_response"])
        self.assertEqual(6, len(result["project_suggestions"]))
        self.assertNotIn("짧게 연습해 보기", result["user_response"])

    def test_first_time_keyring_goal_asks_before_practice(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "뜨개질은 처음인데 키링을 만들어보고 싶어요",
            "journey-keyring",
        )
        self.assertEqual(JourneyType.START_FROM_ZERO, result["journey"])
        self.assertEqual("crochet", result["tool_type"])
        self.assertEqual("키링/keyring", result["detected_project_type"])
        self.assertEqual(
            ["crochet-mini-hat-keyring", "crochet-fishbread-keyring"],
            result["project_suggestions"],
        )
        self.assertIn("사진을 보고", result["user_response"])
        self.assertNotIn("먼저 실제 손동작 보기", result["user_response"])
        self.assertNotIn("짧게 연습해 보기", result["user_response"])
        self.assertEqual("", result["practice_plan"])

    def test_first_time_bag_goal_offers_project_curricula_before_practice(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "뜨개질은 처음인데 작은 가방을 만들어보고 싶어요",
            "journey-bag-options",
        )
        self.assertEqual(JourneyType.START_FROM_ZERO, result["journey"])
        self.assertEqual(
            ["crochet-flat-pouch", "crochet-flat-mini-bag", "needle-flat-pouch"],
            result["project_suggestions"],
        )
        self.assertIn("코바늘", result["user_response"])
        self.assertIn("대바늘", result["user_response"])
        self.assertIn("아래 완성 사진", result["user_response"])
        self.assertIn("보유 도구와 준비할 재료부터", result["user_response"])
        self.assertNotIn("가지고 있는 도구를 확인한 뒤", result["user_response"])
        self.assertNotIn("짧게 연습해 보기", result["user_response"])
        self.assertEqual("", result["practice_plan"])

    def test_beginner_context_survives_when_goal_arrives_on_next_turn(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-split-beginner-bag"
        first = invoke_turn(agent, "뜨개질이 처음인데 어떻게 하나요?", thread_id)
        second = invoke_turn(agent, "작은 가방을 떠보고 싶어요", thread_id)
        self.assertEqual(JourneyType.START_FROM_ZERO, first["journey"])
        self.assertEqual(JourneyType.START_FROM_ZERO, second["journey"])
        self.assertEqual("beginner", second["learner_profile"]["level"])
        self.assertEqual(3, len(second["project_suggestions"]))
        self.assertIn("완성 사진을 보고 첫 작품을 고르세요", second["user_response"])
        self.assertIn("보유 도구와 준비할 재료부터", second["user_response"])
        self.assertNotIn("path", second["user_response"])
        self.assertEqual("", second["practice_plan"])

    def test_bag_curriculum_tracks_practice_and_unlocks_project_guide(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-bag-curriculum"

        invoke_turn(agent, "뜨개질은 처음인데 작은 가방을 만들어보고 싶어요", thread_id)
        selected = invoke_turn(agent, "코바늘 납작 미니 토트백을 선택할게요", thread_id)
        self.assertEqual("crochet-flat-mini-bag", selected["learning_program"]["curriculum_id"])
        self.assertEqual("awaiting_tools", selected["learning_program"]["status"])
        self.assertEqual(0, selected["learning_program"]["current_step"])
        self.assertIn("시작 준비물", selected["user_response"])
        self.assertIn("아직 연습은 시작하지 않고", selected["user_response"])
        self.assertEqual("", selected["practice_plan"])
        self.assertEqual([], selected["detected_techniques"])
        self.assertEqual([], selected["technique_resources"])

        missing = invoke_turn(agent, "아무것도 없어요", thread_id)
        self.assertEqual("shopping", missing["learning_program"]["status"])
        self.assertIn("같은 준비물 질문은 다시 하지 않을게요", missing["user_response"])
        self.assertIn("도구 없이 먼저 작품 과정 보기", missing["user_response"])
        self.assertEqual("crochet-flat-mini-bag", missing["purchase_plan"]["curriculum_id"])
        self.assertGreaterEqual(len(missing["purchase_plan"]["tools"]), 4)
        self.assertEqual("", missing["practice_plan"])

        repeated = invoke_turn(agent, "네, 정말 아무것도 없어요", thread_id)
        self.assertEqual("shopping", repeated["learning_program"]["status"])
        self.assertNotIn("없다면 ‘아무것도 없어요’", repeated["next_action"])
        self.assertIn("먼저 전체 과정을 둘러보거나", repeated["next_action"])

        ready = invoke_turn(agent, "중간 굵기 면사와 4mm 코바늘이 준비됐어요", thread_id)
        self.assertEqual("active", ready["learning_program"]["status"])
        self.assertIn("학습 진도 0/4", ready["user_response"])
        self.assertIn("사슬뜨기", ready["user_response"])
        self.assertIn("이번 단계 연습", ready["user_response"])
        self.assertNotIn("짧게 연습해 보기", ready["user_response"])

        next_step = invoke_turn(agent, "사슬뜨기 연습 완료했어요", thread_id)
        self.assertEqual(1, next_step["learning_program"]["current_step"])
        self.assertEqual(["chain"], next_step["learning_program"]["completed_steps"])
        self.assertIn("학습 진도 1/4", next_step["user_response"])
        self.assertIn("짧은뜨기", next_step["user_response"])

        invoke_turn(agent, "짧은뜨기 연습 완료했어요", thread_id)
        invoke_turn(agent, "빼뜨기 연습 완료했어요", thread_id)
        finished = invoke_turn(agent, "손잡이 연습 완료했어요", thread_id)
        self.assertEqual("project_ready", finished["learning_program"]["status"])
        self.assertEqual(4, len(finished["learning_program"]["completed_steps"]))
        self.assertIn("작품 제작 가이드", finished["user_response"])
        self.assertIn("사슬 21코", finished["user_response"])
        self.assertIn("몸판 2–24단", finished["user_response"])
        self.assertNotIn("이번 단계 연습", finished["user_response"])

    def test_purchase_card_can_open_non_recording_step_preview(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-coaster-preview"
        invoke_turn(agent, "코바늘 원형 티코스터를 선택할게요", thread_id)
        shopping = invoke_turn(agent, "준비물이 아무것도 없어요", thread_id)

        preview = invoke_turn(
            agent,
            "도구 없이 단계별 과정을 먼저 볼게요",
            thread_id,
            learning_program=shopping["learning_program"],
        )
        self.assertEqual("preview", preview["learning_program"]["status"])
        self.assertEqual(0, preview["learning_program"]["current_step"])
        self.assertEqual([], preview["learning_program"]["completed_steps"])
        self.assertIn("미리보기 1/9", preview["user_response"])
        self.assertIn("다음 단계 미리보기", preview["next_action"])

        next_preview = invoke_turn(
            agent,
            "1단 · 매직링에 6코 다음 단계 미리보기",
            thread_id,
            learning_program=preview["learning_program"],
        )
        self.assertEqual(1, next_preview["learning_program"]["current_step"])
        self.assertEqual([], next_preview["learning_program"]["completed_steps"])
        self.assertIn("미리보기 2/9", next_preview["user_response"])

        ready = invoke_turn(
            agent,
            "준비됐어요. 1단부터 시작할게요",
            thread_id,
            learning_program=next_preview["learning_program"],
        )
        self.assertEqual("active", ready["learning_program"]["status"])
        self.assertEqual(0, ready["learning_program"]["current_step"])
        self.assertEqual([], ready["learning_program"]["completed_steps"])

    def test_coaster_shows_the_whole_pattern_then_advances_one_round(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-coaster-rounds"
        invoke_turn(agent, "코바늘 원형 티코스터을 선택할게요", thread_id)
        ready = invoke_turn(agent, "중간 굵기 면사와 4mm 코바늘이 준비됐어요", thread_id)

        self.assertEqual(0, ready["learning_program"]["current_step"])
        self.assertEqual([], ready["learning_program"]["completed_steps"])
        self.assertIn("작품 진도 0/9 · 1단", ready["user_response"])
        self.assertIn("아래 작업대 한 곳", ready["user_response"])
        self.assertNotIn("매직링에 짧은뜨기 6코를 뜨고", ready["user_response"])
        self.assertNotIn("전체 기본 도안 · 기호와 영문 약어", ready["user_response"])
        self.assertNotIn("초보자용 한글 설명", ready["user_response"])
        self.assertNotIn("0.5배속", ready["user_response"])

        next_round = invoke_turn(agent, "매직링 6코 하고, 연습 완료", thread_id)
        self.assertEqual(1, next_round["learning_program"]["current_step"])
        self.assertEqual(["round-1"], next_round["learning_program"]["completed_steps"])
        self.assertIn("작품 진도 1/9 · 2단", next_round["user_response"])

    def test_ready_phrase_with_round_number_does_not_become_pattern_conversion(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-pouch-ready-round"
        invoke_turn(agent, "코바늘 조임끈 납작 파우치을 선택할게요", thread_id)
        ready = invoke_turn(agent, "준비됐어요. 1단부터 시작할게요", thread_id)

        self.assertEqual("active", ready["learning_program"]["status"])
        self.assertEqual("text", ready["input_type"])
        self.assertEqual("learn_technique", ready["intent"])
        self.assertIn("아래 작업대 한 곳", ready["user_response"])
        self.assertNotIn("전체 기본 도안 · 기호와 영문 약어", ready["user_response"])
        self.assertNotIn("초보자용 한글 설명", ready["user_response"])
        self.assertNotIn("도안 초안", ready["user_response"])

    def test_bare_continue_after_materials_opens_the_project_preview(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-mini-hat-continue"
        selected = invoke_turn(agent, "코바늘 미니 모자 키링을 선택할게요", thread_id)
        self.assertEqual("awaiting_tools", selected["learning_program"]["status"])

        continued = invoke_turn(
            agent,
            "계속해줘",
            thread_id,
            learning_program=selected["learning_program"],
        )
        self.assertFalse(continued["out_of_scope"])
        self.assertEqual("preview", continued["learning_program"]["status"])
        self.assertIn("미리보기 1/5", continued["user_response"])
        self.assertNotIn("뜨개 범위", continued["user_response"])

        next_step = invoke_turn(
            agent,
            "계속해줘",
            thread_id,
            learning_program=continued["learning_program"],
        )
        self.assertTrue(next_step["program_turn"])
        self.assertEqual(1, next_step["learning_program"]["current_step"])
        self.assertIn("미리보기 2/5", next_step["user_response"])
        self.assertIn("3–4단", next_step["user_response"])

    def test_unrelated_knitting_question_keeps_project_progress_without_showing_the_step(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-side-technique-question"
        selected = invoke_turn(agent, "코바늘 미니 모자 키링을 선택할게요", thread_id)
        active = invoke_turn(
            agent,
            "3번 DK 면사와 3.5mm 코바늘이 준비됐어요",
            thread_id,
            learning_program=selected["learning_program"],
        )
        result = invoke_turn(
            agent,
            "한길긴뜨기는 어떻게 하는 거야?",
            thread_id,
            learning_program=active["learning_program"],
        )
        self.assertFalse(result["program_turn"])
        self.assertEqual(active["learning_program"], result["learning_program"])
        self.assertIn("한길긴뜨기", result["user_response"])
        self.assertNotIn("작품 진도", result["user_response"])
        self.assertNotIn("지금 뜰 차례", result["user_response"])
        self.assertNotIn("1–2단 · 꼭대기", result["user_response"])

    def test_off_topic_question_is_blocked_without_replaying_saved_pattern(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-scope-guardrail"
        selected = invoke_turn(agent, "코바늘 붕어빵 키링을 선택할게요", thread_id)
        blocked = invoke_turn(agent, "김치찌개는 어떻게 해요?", thread_id)

        self.assertTrue(blocked["out_of_scope"])
        self.assertEqual("scope_guardrail_agent", blocked["active_agent"])
        self.assertEqual(selected["learning_program"], blocked["learning_program"])
        self.assertIn("뜨개 질문과 작품 제작", blocked["user_response"])
        self.assertIn("진도는 그대로 보관", blocked["user_response"])
        self.assertNotIn("전체 기본 도안 · 기호와 영문 약어", blocked["user_response"])
        self.assertNotIn("매직링 안에 짧은뜨기 6코", blocked["user_response"])

    def test_scope_guardrail_allows_knitting_and_known_progress_controls(self) -> None:
        self.assertFalse(is_knitting_scope("김치찌개는 어떻게 해요?"))
        self.assertTrue(is_knitting_scope("짧은뜨기 6코는 어떻게 떠요?"))
        self.assertTrue(is_knitting_scope("다음 단계로 갈게요", existing_program={"curriculum_id": "crochet-fishbread-keyring"}))
        self.assertTrue(is_knitting_scope("계속해줘", existing_program={"curriculum_id": "crochet-mini-hat-keyring"}))
        self.assertTrue(is_knitting_scope("처음부터 설명해줘", existing_program={"curriculum_id": "crochet-mini-hat-keyring"}))

    def test_pattern_literacy_shortcuts_answer_the_selected_topic(self) -> None:
        cases = [
            ("ch, sc, dc, sl st가 들어간 영문 코바늘 도안을 처음 읽는 법을 예시로 알려줘", "영문 코바늘 약어 읽기", "`sc` = 짧은뜨기"),
            ("코바늘 기호 도안의 중심, 단 시작, 반복 구간을 찾는 법을 예시로 알려줘", "코바늘 기호 도안 읽기", "같은 밑점"),
            ("K, P, yo, k2tog가 들어간 영문 대바늘 도안을 처음 읽는 법을 예시로 알려줘", "영문 대바늘 약어 읽기", "`K` = 겉뜨기"),
            ("뜨개 도안에서 괄호, 별표, repeat 반복 구간을 찾는 법을 예시로 알려줘", "반복 구간 찾기", "rep from"),
        ]
        for index, (prompt, heading, detail) in enumerate(cases):
            with self.subTest(prompt=prompt):
                result = invoke_turn(create_knitcoach(), prompt, f"journey-pattern-literacy-{index}")
                self.assertEqual(JourneyType.EXPLAIN_PATTERN, result["journey"])
                self.assertEqual("미확정 프로젝트", result["detected_project_type"])
                self.assertIn(heading, result["user_response"])
                self.assertIn(detail, result["user_response"])
                self.assertNotIn("첫 작품 목표", result["user_response"])
                self.assertEqual("", result["practice_plan"])

    def test_restart_explanation_returns_to_first_project_step(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-restart-from-first-step"
        selected = invoke_turn(agent, "코바늘 원형 티코스터를 선택할게요", thread_id)
        active = invoke_turn(
            agent,
            "4번 면사와 4mm 코바늘이 준비됐어요",
            thread_id,
            learning_program=selected["learning_program"],
        )
        second = invoke_turn(agent, "계속해줘", thread_id, learning_program=active["learning_program"])
        self.assertEqual(1, second["learning_program"]["current_step"])

        restarted = invoke_turn(
            agent,
            "처음부터 설명해줘",
            thread_id,
            learning_program=second["learning_program"],
        )
        self.assertFalse(restarted["out_of_scope"])
        self.assertTrue(restarted["program_turn"])
        self.assertEqual(0, restarted["learning_program"]["current_step"])
        self.assertEqual([], restarted["learning_program"]["completed_steps"])
        self.assertIn("작품 진도 0/9 · 1단", restarted["user_response"])

    def test_learning_program_can_resume_after_agent_restart(self) -> None:
        first_agent = create_knitcoach()
        thread_id = "journey-coaster-resume"
        invoke_turn(first_agent, "코바늘 원형 티코스터을 선택할게요", thread_id)
        ready = invoke_turn(first_agent, "중간 굵기 면사와 4mm 코바늘이 준비됐어요", thread_id)

        restarted_agent = create_knitcoach()
        resumed = invoke_turn(
            restarted_agent,
            "1단 단계 완료",
            thread_id,
            learning_program=ready["learning_program"],
        )
        self.assertEqual(1, resumed["learning_program"]["current_step"])
        self.assertIn("2단 · 12코", resumed["user_response"])

    def test_coaster_problem_reaches_crochet_diagnosis(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "이 작품에서 막힌 부분을 진단해줘. 코스터 가장자리가 자꾸 휘어요. 왜 그런가요?",
            "journey-diagnosis",
        )
        self.assertEqual("analyze_artifact", result["intent"])
        self.assertEqual(JourneyType.DIAGNOSE_PROJECT, result["journey"])
        self.assertEqual("crochet", result["tool_type"])
        self.assertEqual("컵받침/coaster", result["detected_project_type"])
        self.assertTrue(result["recommended_fixes"])
        self.assertNotIn("사진에서 확인", result["user_response"])
        self.assertIn("텍스트 설명에서 추정", result["user_response"])

    def test_image_diagnosis_uses_observed_facts_and_only_needed_extra_views(self) -> None:
        observation = ImageObservation(
            summary="사진의 정면에서 코바늘 가방과 손잡이를 확인했습니다.",
            tool_type="crochet",
            project_type="가방",
            confidence="medium",
            visible_facts=["정면의 망사 무늬와 손잡이 연결부가 보입니다."],
            likely_techniques=["사슬뜨기", "한길긴뜨기"],
            construction=["몸판에서 손잡이가 이어집니다."],
            diagnoses=["왼쪽 손잡이 연결부의 장력이 더 촘촘해 보입니다."],
            suggested_actions=["양쪽 손잡이 시작 코 수를 비교해 보세요."],
            uncertainties=["가방 바닥의 시작 방식은 정면에서 보이지 않습니다."],
            additional_photos=["가방 바닥"],
        )
        sample = Path(__file__).resolve().parent.parent / "samples" / "crochet-mesh-shoulder-bag.png"
        with patch("knitcoach.structured_model_available", return_value=True), patch(
            "knitcoach.analyze_image_with_model", return_value=observation
        ):
            result = invoke_turn(
                create_knitcoach(),
                "이 가방 사진에서 보이는 부분과 문제를 진단해줘",
                "journey-vision-observation",
                image_path=str(sample),
                original_image_name=sample.name,
            )

        self.assertIn("정면의 망사 무늬", result["user_response"])
        self.assertIn("가방 바닥", result["user_response"])
        self.assertNotIn("정면 사진을", result["user_response"])
        self.assertEqual(observation.model_dump(), result["image_observation"])

    def test_rules_mode_never_pretends_to_have_seen_uploaded_pixels(self) -> None:
        sample = Path(__file__).resolve().parent.parent / "samples" / "crochet-mesh-shoulder-bag.png"
        with patch("knitcoach.structured_model_available", return_value=False):
            result = invoke_turn(
                create_knitcoach(),
                "이 가방 사진을 진단해줘",
                "journey-rules-image-honesty",
                image_path=str(sample),
                original_image_name=sample.name,
            )

        self.assertIn("이미지 내용을 실제로 읽지 못했습니다", result["user_response"])
        self.assertNotIn("첨부한 사진에서 보이는", result["user_response"])

    def test_pattern_explanation_does_not_invent_rows(self) -> None:
        result = invoke_turn(create_knitcoach(), "ch 12, sc in each ch", "journey-pattern")
        self.assertIn("반복할 단 수는 입력에 없으므로", result["user_response"])
        self.assertNotIn("총 5단", result["user_response"])

    def test_round_increase_diagnosis_checks_round_start(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "원형뜨기 단 시작 위치에서 자꾸 코가 늘어나요",
            "journey-round-start",
        )
        self.assertEqual(JourneyType.DIAGNOSE_PROJECT, result["journey"])
        self.assertIn("단 시작 위치", result["user_response"])
        self.assertIn("표시 고리", result["user_response"])

    def test_explicit_pattern_request_builds_rows(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "사슬 12코로 시작해서 짧은뜨기 5단을 도안으로 바꿔줘",
            "journey-pattern-build",
        )
        self.assertEqual("explanation_to_pattern", result["conversion_mode"])
        self.assertIn("1–5단", result["generated_pattern"])
        self.assertIn("입력에 없으므로", result["generated_pattern"])

    def test_material_question_returns_tools_and_project(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "울 실 두 타래와 5mm 대바늘로 뭘 만들 수 있을까요?",
            "journey-materials",
        )
        self.assertEqual(JourneyType.START_FROM_MATERIALS, result["journey"])
        self.assertIn("짧은 목도리", result["user_response"])
        self.assertIn("4.0-5.5mm", result["user_response"])

    def test_named_tool_definition_answers_the_question_without_starting_material_flow(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "표시링이 뭐야?",
            "journey-marker-definition",
        )
        self.assertEqual("tool_question", result["input_type"])
        self.assertEqual("advise_tools", result["intent"])
        self.assertIn("표시링·마커", result["user_response"])
        self.assertIn("단 시작", result["user_response"])
        self.assertNotIn("가진 재료로 시작하기", result["user_response"])
        self.assertNotIn("초보 용어 메모", result["user_response"])
        self.assertEqual("", result["practice_plan"])
        self.assertEqual("", result["next_action"])

    def test_tool_definition_does_not_replace_an_active_project_step(self) -> None:
        agent = create_knitcoach()
        thread_id = "journey-marker-during-project"
        selected = invoke_turn(agent, "코바늘 원형 티코스터를 선택할게요", thread_id)
        active = invoke_turn(
            agent,
            "4번 면사와 4mm 코바늘, 표시링이 준비됐어요",
            thread_id,
            learning_program=selected["learning_program"],
        )
        result = invoke_turn(
            agent,
            "표시링이 뭐야?",
            thread_id,
            learning_program=active["learning_program"],
        )
        self.assertEqual("active", result["learning_program"]["status"])
        self.assertEqual(0, result["learning_program"]["current_step"])
        self.assertEqual([], result["detected_techniques"])
        self.assertIn("표시링·마커", result["user_response"])
        self.assertNotIn("작품 진도", result["user_response"])

    def test_tool_purchase_question_does_not_attach_unrelated_practice(self) -> None:
        result = invoke_turn(
            create_knitcoach(),
            "아후강 코바늘을 처음 사는데 가성비 제품으로 가방을 만들고 싶어. 무엇을 사야 해?",
            "journey-tunisian-tools",
        )
        self.assertEqual("advise_tools", result["intent"])
        self.assertEqual([], result["detected_techniques"])
        self.assertEqual("", result["practice_plan"])
        self.assertIn("아후강·튀니지안 코바늘", result["user_response"])
        self.assertNotIn("기본 코바늘:", result["user_response"])
        self.assertNotIn("사슬뜨기", result["user_response"])
        self.assertNotIn("짧게 연습해 보기", result["user_response"])

    def test_provider_neutral_contracts_validate(self) -> None:
        request = TutorRequest(journey=JourneyType.START_FROM_ZERO, message="뜨개를 처음 시작해요")
        response = TutorResponse(summary="첫 목표를 정해볼게요", next_action="만들고 싶은 작품을 고르세요")
        self.assertEqual(JourneyType.START_FROM_ZERO, request.journey)
        self.assertEqual("unknown", response.confidence)


if __name__ == "__main__":
    unittest.main()
