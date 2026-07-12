# KnitCoach

KnitCoach는 뜨개질 초보 학습자를 위한 LangGraph 기반 교육 agent입니다.
완성품 사진, 도안 사진, 도안 텍스트, 설명글을 입력하면 코바늘(crochet)과
대바늘(needle knitting) 중 어떤 작업인지 판단하고, 포함된 기법, 난이도,
필요한 도구/부자재, 다음 연습 방법을 제안합니다.

## 과제 맥락

- Course: AI Agents Masterclass, Demo Day project start
- Theme: 교육과 학습
- Goal: learning agent의 첫 LangGraph structure를 설계하고 구현합니다.
- Related local lessons: `01-your-first-ai-agent`, `02-chatgpt-clone`

## 주요 기능

- 완성품 사진 경로, 도안 사진 경로, 도안 텍스트, 설명글, 제품/도구 질문을
  구분합니다.
- 코바늘(crochet), 대바늘(needle knitting), 또는 아직 정하지 않은 tool path 중
  어디에 해당하는지 감지합니다.
- 사슬뜨기, 짧은뜨기, 긴뜨기, 빼뜨기, 매직링, 원형뜨기, 코 잡기, 겉뜨기,
  안뜨기, 고무뜨기 같은 기초 기법을 추론합니다.
- 작품 유형, 입력 유형, 감지된 기법, 난이도, 막힌 지점, practice plan을
  LangGraph state에 저장합니다.
- 분류 agent, artifact 분석 agent, pattern 변환 agent, 도구 advisor agent,
  기법 resource agent, teacher agent가 conditional edge 기반으로 분기/합류합니다.
- 도안 텍스트를 초보자 설명글로 바꾸고, 설명글을 row-by-row 도안과
  simplified chart spec으로 바꿉니다.
- 코바늘/대바늘 호수, 실 굵기, 실 라벨 확인법, 돗바늘/단수링/마커 같은
  부자재를 안내합니다.
- 기법별 설명, 자주 하는 실수, 미리 생성해 둔 기초 영상 asset 경로,
  작품별 맞춤 영상 생성 요청 metadata를 제공합니다.
- 단계별 lesson, 짧은 practice assignment, 다음 촬영/연습 가이드를 생성합니다.

## 주말 미션: 핵심 기능 (Tool + 병렬 + 메모리)

이 버전은 주말 미션 요구사항에 맞춰 다음을 추가했습니다.

- **노드 ≥ 3개**: `classifier_agent` ~ `check_understanding_agent` 등 12개 노드.
- **Conditional Edge ≥ 1개** (실제 2개):
  - `route_by_intent` — intent에 따라 분석/변환/기법 branch로 분기.
  - `tools_condition` — `resource_agent`가 tool을 호출하면 `resource_tools`(ToolNode)로,
    아니면 `teacher_agent`로 분기하는 ReAct tool 루프.
- **Tool 연동 ≥ 1개** (실제 3개, LangChain `@tool`):
  - `search_technique_tutorials` — **웹 검색**. `ddgs`(API 키 불필요)로 기법 튜토리얼을 찾고,
    네트워크/라이브러리가 없으면 유튜브 검색 링크 + 카탈로그 기반 fallback을 반환합니다.
  - `search_local_pattern_samples` — **파일 검색**. `samples/` 폴더와 기법 카탈로그에서 매칭 자료 경로를 찾습니다.
  - `recommend_tools_for_yarn` — **커스텀 도메인**. 실 굵기 → 권장 코바늘/대바늘 호수(mm)와 부자재를 추천합니다.
- **병렬 실행 (Send API)**: `fan_out_techniques`가 감지된 기법마다 `Send`로 `technique_scout`를
  동시에 실행하고, `operator.add` reducer로 `technique_resources`에 합칩니다(map-reduce).
- **메모리**: `MemorySaver` checkpointer로 `thread_id`별 대화/상태를 유지합니다.
  `run_conversation` 헬퍼로 같은 thread에서 여러 턴을 이어 실행하는 예시를 제공합니다.

`resource_agent`의 실제 tool 호출은 `OPENAI_API_KEY`가 있을 때만 LLM(bind_tools)으로 수행되고,
키가 없으면 tool 없이 카탈로그 리소스만 사용해 그래프가 그대로 완주합니다(offline-first 유지).

## 샘플 Reference

- `samples/crochet-mesh-shoulder-bag.png`: 코바늘 네트/레이스 숄더백 완성품 예시입니다.
- `samples/crochet-mesh-shoulder-bag-pattern.png`: 같은 유형의 가방 도안 reference입니다.
- 이 샘플은 "완성품은 이런 모습이고, 도안 구조는 바닥, 몸통, 손잡이,
  크로스끈으로 나뉜다"는 설명을 테스트하기 위한 자료입니다.
- 도안 reference는 가방바닥 3단 기준으로 보이지만, 샘플 완성품 크기는
  바닥을 6-7단 정도까지 확장한 응용으로 추정하는 메모를 포함합니다.
- notebook 예제 중 `crochet-coaster-tight-edge.png`, `needle-knit-scarf-dropped-stitch.jpg`는
  repo에 포함된 실제 파일이 아니라 image_path fallback 분석(막힌 지점 진단)을 시연하기 위한
  예시 경로입니다. vision 호출이 꺼져 있어 파일이 없어도 fallback으로 동작합니다.

## 설치

```bash
cd assignments/knitting-tutor-agent
uv sync
```

OpenAI model을 사용하려면 local `.env` file을 만듭니다.

```bash
cp .env.example .env
```

그다음 `.env`에 `OPENAI_API_KEY`를 설정합니다. key가 없어도 notebook은
deterministic fallback response를 사용하므로 graph 실행과 리뷰가 가능합니다.
키가 있으면 `resource_agent`가 `@tool`(웹검색/파일검색/커스텀)을 실제로 호출합니다.
웹 검색 tool은 `ddgs`(설치 시, API 키 불필요)와 네트워크가 있을 때만 실제 검색하고,
없으면 유튜브 검색 링크 + 카탈로그 fallback을 반환하므로 오프라인에서도 안전합니다.
실제 vision model 호출은 기본적으로 꺼져 있으며, 필요하면 다음 값을 추가합니다.

```bash
KNITCOACH_ENABLE_VISION=1
```

## 실행

```bash
uv run jupyter lab
```

`knitting_tutor_agent.ipynb`를 열고 모든 cell을 실행합니다.

## 검증

```bash
uv run jupyter nbconvert --to notebook --execute knitting_tutor_agent.ipynb --output executed.ipynb
```

확인할 내용:

- notebook이 API 키 없이도 error 없이 실행됩니다(offline-first).
- graph에는 12개 working node가 있습니다(요구사항 ≥3 충족).
- `add_conditional_edges`를 2번 사용합니다: (1) `route_by_intent`로 분석/변환/기법 branch 분기,
  (2) `tools_condition`으로 `resource_agent`의 tool 호출 루프 분기(요구사항 ≥1 충족).
- `Send` API로 감지된 기법마다 `technique_scout`를 병렬 실행하고 reducer로 합류합니다(병렬 보너스).
- `MemorySaver` checkpointer + `thread_id`로 대화를 기억합니다(`run_conversation` 데모, 메모리 보너스).
- LangChain `@tool` 3종(웹검색/파일검색/커스텀 도메인)을 `resource_agent`가 `bind_tools`로 사용합니다
  (다중 Tool 보너스). 키가 없으면 tool 없이 카탈로그 리소스로 우회합니다.
- `print(knitcoach.get_graph().draw_mermaid())`에 `technique_scout`, `resource_agent`,
  `resource_tools` 노드와 두 conditional edge가 나타납니다.
- 샘플 가방 prompt는 완성품 사진과 도안 reference를 함께 분석하고,
  가방바닥, 가방몸통, 손잡이, 크로스끈 구조를 설명합니다.
- 샘플 가방 prompt는 도안은 바닥 3단 기준이고 완성품은 6-7단 확장
  가능성이 있다는 reference note를 생성합니다.
- 사진 경로 prompt는 fallback 분석으로 작품 유형, 기법, 난이도, 도구/부자재,
  수정 방법을 생성합니다.
- 코바늘 prompt는 코바늘 학습 경로, 호수/실/부자재 안내, practice plan을
  생성합니다.
- 대바늘 prompt는 대바늘 학습 경로, 바늘/실/부자재 안내, practice plan을
  생성합니다.
- pattern text prompt는 약어 해설이 아니라 단계별 초보자 설명글과 row-by-row
  pattern을 생성합니다.
- explanation prompt는 row-by-row pattern과 chart spec을 생성합니다.
- quiz/feynman output은 생성하지 않습니다.

## 영상 전략

- 기초 기법 영상은 사슬뜨기, 짧은뜨기, 긴뜨기, 빼뜨기, 매직링, 겉뜨기,
  안뜨기처럼 반복적으로 쓰이는 기법별로 미리 AI 생성해 asset library에
  저장해 둡니다.
- agent는 사진/도안 분석에서 감지한 기법에 맞춰 prebuilt 영상 asset을
  추천합니다.
- 사용자 작품에서 특정 문제를 발견한 경우에는 작품 유형, 문제 부위,
  감지된 기법, 수정 방법을 바탕으로 맞춤형 짧은 영상 생성 요청 metadata를
  만듭니다.
- 샘플 가방에서는 바닥 3단에서 6-7단으로 확장하는 방법, 몸통 반복
  구멍무늬, 손잡이 사슬 40코, 크로스끈 연결부를 설명하는 맞춤 영상
  생성 prompt를 만듭니다.
- 현재 notebook은 실제 영상 파일 생성까지 실행하지 않고, prebuilt asset 경로와
  on-demand 생성 prompt를 출력해 다음 단계 구현 지점을 명확히 보여줍니다.

