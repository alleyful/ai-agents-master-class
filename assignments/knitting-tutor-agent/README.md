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

## Education Agent: Advanced Features + Streamlit

2일 챌린지의 고급 패턴은 **Option B: 워크플로우 아키텍처**를 선택했습니다.
분류 agent가 작업을 전문 worker에게 전달하는 Orchestrator-Workers 구조와,
기법별 `technique_scout`를 동시에 실행하는 `Send` 기반 병렬 처리를 사용합니다.

- `knitcoach.py`: Streamlit과 검증 코드가 공유하는 LangGraph core입니다.
- `main.py`: 단일 에이전트 작업대를 여는 얇은 Streamlit 엔트리입니다.
- `views/home.py`: 통합 컴포즈, 대화, 작업 카드와 상세 패널을 묶은 메인 작업대입니다.
- `views/techniques.py`: 설명·기호·영상 프롬프트를 탐색하고 대화로 이어가는 기법 라이브러리입니다.
- `views/tools.py`: 코바늘·대바늘·부자재 비교, 입문/업그레이드 구매 기준과 게이지 계산기를 제공하는 도구 보관함입니다.
- `views/pattern_studio.py`, `views/tutor.py`: 이전 페이지형 UI를 학습 참고용으로 보존합니다.
- `content/techniques.py`: 코바늘 20개·대바늘 20개 기법의 설명·단계·실수 교정·연습·영상 프롬프트를 가진 단일 원천입니다.
- `content/tools.py`: 도구 종류·호수 선택·브랜드 참고·실 굵기 범위·게이지 계산과 코칭 추천의 단일 원천입니다.
- `assets/tools/`: 표준 기호 대신 각 도구의 실제 형태를 알아볼 수 있도록 만든 학습용 일러스트 자산입니다.
- `content/symbols.py`: 표준 도안 기호, 도안 보조 표시, 학습 아이콘을 구분해 코드 기반 SVG로 렌더링합니다.
- `common.py`: 페이지 공용 헬퍼(`get_agent`, 세션 초기화, 임시 이미지, debug metadata).
- `nav.py`: 작업 중심 LNB의 공방 도구 구성을 정의합니다.
- `ui.py`: 따뜻한 뜨개 공방 스타일과 `eyebrow`/`tag` 렌더 헬퍼를 제공합니다.
- `content/presets.py`: 도안 만들기 시작 프리셋(`PROJECT_PRESETS`) — 크기·실·바늘 기본값.
- `.streamlit/config.toml`: 위젯 기반 테마(공방 작업대 팔레트). 비밀 값이 아니므로 커밋 대상입니다.
- `knitting_tutor_agent.ipynb`: 초기 설계와 예제를 보존한 학습용 notebook입니다.
- `DISCORD_POST.md`: 디스코드 `🔥|부스트업` 포럼 게시용 소개 초안입니다.

### 디자인 / 구조 노트 (로컬 스터디 변경)

- **정체성**: 실용적인 뜨개 작업대 — 아이보리 작업 화면(`#F6F4EE`)과 짙은 파인 LNB(`#26342D`),
  테라코타 실색(`#C96F4E`)으로 내비게이션과 작업 영역을 분리합니다. 큰 마케팅 hero, AI풍
  그라데이션, 세리프 제목과 과도한 둥근 카드를 사용하지 않습니다.
- **수단**: 전부 Streamlit 네이티브 — `config.toml [theme]` + `st.markdown` CSS 주입만 사용하며
  외부 폰트나 이미지 장식에 의존하지 않습니다.
- **에이전트 작업대**: 새 대화는 첫 화면 중앙의 통합 컴포즈가 먼저 보이고 최근 작업과 퀵 도구는
  바로 아래 작은 버튼 선반으로 표시됩니다. 대화가 시작되면 컴포즈는 화면 하단에 고정되고,
  도안·기법·연습·문제 진단 카드를 클릭하면 오른쪽 상세 패널이 열립니다. LNB는 새 대화, 현재
  세션의 최근 작업과 공방 도구를 왼쪽 정렬로 보여주며 기본 접기/펼치기를 지원합니다. `기법 찾아보기`는
  기호와 설명 세트를 탐색하는 전용 라이브러리를 열고, 새로고침·재배포 후의 영구 보존은 지원하지 않습니다.
- **도안 만들기 플로우**: 대화 안의 `도안 만들기` 커맨드가 dialog에서 크기·실·바늘 프리셋을 열고, 값을
  수정해 구조화된 도안 카드를 만듭니다. 단, 에이전트(`generate_pattern`)는
  이미지와 크기/실/바늘 값을 반드시 요구합니다(→ `PatternRequest` 검증). 규칙 모드에서는 번들 샘플만
  결정적으로 처리하고, 로컬 개발에서는 저장된 ChatGPT/Codex 인증, 최종 검증에서는 OpenAI API를
  같은 구조화 출력 계약으로 사용합니다.
- **구조**: 콘텐츠(데이터)와 표현(UI)을 분리했습니다. 기법·프리셋 텍스트는 UI에 하드코딩하지 않고
  `content/`에서 가져옵니다. 에이전트의 기법 설명과 연습 계획도 같은 카탈로그를 사용합니다.
- **스터디 결론**: framer-motion·21st.dev 같은 React 디자인 도구의 *산출 코드*는 Streamlit에
  직접 적용되지 않습니다(JS 제거, React/Tailwind 아님; 커스텀 컴포넌트 iframe에서만 동작).
  디자인 *원칙*만 전이 가능하므로 재디자인은 React 도구 없이 진행했습니다.

Streamlit의 각 browser session은 고유한 `thread_id`를 사용합니다. 대화 메시지는
유지하되 분석 결과와 기법 리소스 같은 파생 state는 매 turn 초기화하므로, 이전 질문의
결과가 다음 질문에 섞이지 않습니다.

## 주요 기능

### 사용자 여정 중심 첫 화면

첫 화면은 내부 기능 이름 대신 학습자가 지금 하려는 일을 기준으로 여섯 흐름을 제공합니다.

- 처음부터 배우기 (`start_from_zero`)
- 배운 내용 이어가기 (`continue_learning`)
- 작품 문제 해결하기 (`diagnose_project`)
- 사진 속 작품 만들기 (`recreate_from_photo`)
- 도안 풀어 읽기 (`explain_pattern`)
- 가진 재료로 시작하기 (`start_from_materials`)

`domain/models.py`의 `TutorRequest`와 `TutorResponse`는 fixture·헤드리스 평가·최종 OpenAI API가
공유할 provider-neutral 계약입니다. `domain/journeys.py`는 모델 호출 없이 각 입력을 여정으로
분류하고, 같은 카탈로그를 첫 화면 문구와 테스트가 함께 사용합니다.

- 작품 이미지와 완성 크기·실·바늘 조건으로 구조화된 텍스트 도안 초안을 생성합니다.
- 대화 결과를 도안·기법·연습·문제 진단 카드로 정리하고 오른쪽 작업대에서 자세히 봅니다.
- 도구 보관함에서 기본/레이스/아후강 코바늘, 직선·고정형·교체식 줄바늘, 장갑바늘, 숏팁·롱팁과 공통 부자재를 독립적으로 비교합니다.
- 대바늘 스와치를 세탁·건조한 뒤 중앙 측정값을 10cm 게이지로 환산하고, 목표보다 촘촘하거나 느슨할 때의 바늘 조정 방향을 안내합니다.
- 첫 프로젝트에는 필요한 규격의 가성비 단품, 취향이 정해진 뒤에는 브랜드·재질·케이블 시스템을 비교하도록 단계별 추천합니다.
- 통합 컴포즈에서 질문과 이미지를 함께 첨부하며 새 대화와 최근 작업을 세션 안에서 오갑니다.

- 완성품 사진 경로, 도안 사진 경로, 도안 텍스트, 설명글, 제품/도구 질문을
  구분합니다.
- 코바늘(crochet), 대바늘(needle knitting), 또는 아직 정하지 않은 tool path 중
  어디에 해당하는지 감지합니다.
- 사슬뜨기, 짧은뜨기, 긴뜨기, 빼뜨기, 매직링, 매직링으로 원형 시작하기, 코 잡기, 겉뜨기,
  안뜨기, 1×1 고무뜨기 같은 기초 기법을 추론합니다.
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

로컬 설정이 필요하면 `.env` file을 만듭니다.

```bash
cp .env.example .env
```

로컬의 `KNITCOACH_MODEL_PROVIDER=rules`는 모델 호출 없이 deterministic fallback으로
graph 실행과 회귀 테스트가 가능합니다. 공개 배포에서는 대화 의도와 문맥 판단을
`openai_api` provider가 담당하고, 검수된 작품 도안과 진도 변경은 애플리케이션이 결정론적으로 관리합니다.

```bash
codex login status
OPENAI_API_KEY= KNITCOACH_MODEL_PROVIDER=codex_exec uv run streamlit run main.py
```

이 모드는 자식 프로세스에 `OPENAI_API_KEY`와 `CODEX_API_KEY`를 전달하지 않으며, `codex exec`가
저장한 로그인만 재사용합니다. 동일한 입력·이미지는 로컬 캐시에 저장되어 반복 새로고침 때 모델을
다시 호출하지 않습니다. 다만 ChatGPT/Codex 구독 사용량 제한에는 포함되며, 신뢰할 수 있는 로컬 개발
환경 전용이므로 공개 서버에는 사용하지 않습니다.

API 검증 또는 배포에서는 `OPENAI_API_KEY`와 `KNITCOACH_MODEL_PROVIDER=openai_api`를 설정합니다.
키가 있고 provider를 따로 지정하지 않아도 API 모드가 선택되지만, 배포 설정에는 명시하는 편이 좋습니다.

### Streamlit Community Cloud 배포

앱 entrypoint는 `assignments/knitting-tutor-agent/main.py`입니다. Streamlit Cloud의
**App settings → Secrets**에 `.streamlit/secrets.toml.example`과 같은 항목을 등록하세요.

```toml
OPENAI_API_KEY = "sk-..."
KNITCOACH_MODEL_PROVIDER = "openai_api"
KNITTING_AGENT_MODEL = "gpt-4.1-mini"
KNITCOACH_ROUTER_MODEL = "gpt-4.1-mini"
```

실제 키가 들어간 `secrets.toml`은 저장소에 커밋하지 않습니다. 모델은 일반 뜨개 질문에 직접 답하고,
작품 선택·현재 단계 설명·다음 단계 이동을 구조화된 action으로 반환합니다. 코 수와 단 수, 완료 상태는
모델 답변이 아니라 저장소의 검수된 curriculum 데이터로 처리합니다.

key가 없어도 notebook은 deterministic fallback response를 사용하므로 graph 실행과 리뷰가 가능합니다.
키가 있으면 `resource_agent`가 `@tool`(웹검색/파일검색/커스텀)을 실제로 호출합니다.
웹 검색 tool은 `ddgs`(설치 시, API 키 불필요)와 네트워크가 있을 때만 실제 검색하고,
없으면 유튜브 검색 링크 + 카탈로그 fallback을 반환하므로 오프라인에서도 안전합니다.
규칙 모드에서 임의 이미지를 받으면 이미지를 추측하지 않으며, 저장소의 샘플 가방만 curated demo로
실행합니다. `codex_exec` 또는 `openai_api` provider에서는 실제 이미지 관찰 결과를 구조화해 사용합니다.
도안은 사진 한 장을 기반으로 한 테스트용 초안이므로
게이지 샘플을 먼저 만들고 코 수를 조정해야 합니다.

agent routing과 raw state는 기본 화면에 나타나지 않습니다. 개발 중 확인하려면
다음 값을 사용합니다.

```bash
KNITCOACH_DEBUG=1
```

## Streamlit 실행

```bash
uv run streamlit run main.py
```

왼쪽 LNB에서 새 뜨개 대화, 최근 작업과 공방 도구를 선택할 수 있습니다. 중앙 통합 컴포즈는
PNG/JPG/JPEG/WebP 이미지와 질문을 함께 받고, 도안 만들기 커맨드는 이미지와 제작 조건을
받습니다. 새 대화는 새로운 LangGraph thread를 만들되 같은 접속 세션의 이전 대화는 유지합니다.

API key 없이도 규칙 및 catalog 기반 fallback으로 채팅이 끝까지 실행됩니다. API 요금 없이 실제 이미지
개발 플로우까지 확인하려면 다음처럼 구독 모델 provider를 명시합니다.

```bash
OPENAI_API_KEY= KNITCOACH_MODEL_PROVIDER=codex_exec uv run streamlit run main.py
```

## Notebook 실행

```bash
uv run jupyter lab
```

`knitting_tutor_agent.ipynb`를 열고 모든 cell을 실행합니다.

## 검증

먼저 API 호출 없이 core와 다중 turn 상태를 확인합니다.

```bash
uv run python -m compileall knitcoach.py main.py nav.py common.py ui.py content domain evals views
uv run python -c "from knitcoach import knitcoach, invoke_turn; r = invoke_turn(knitcoach, '코바늘 짧은뜨기를 배우고 싶어', 'smoke-test'); print(r['intent'], r['learning_path'])"
```

API 키가 들어 있는 로컬 `.env`와 무관하게 완전 오프라인으로 회귀 테스트를 실행하려면 빈 값을
명시합니다.

```bash
OPENAI_API_KEY= KNITCOACH_ENABLE_VISION=0 uv run python -m unittest discover -s tests -v
OPENAI_API_KEY= KNITCOACH_ENABLE_VISION=0 uv run python evals/run_offline.py
```

`evals/cases.jsonl`에는 기본 여정 사례와 키링 입문 회귀 사례를 포함한 총 19개 라우팅 사례가 있습니다.
사람이 화면에서 그대로 복사해 확인할 수 있는 절차는 `evals/MANUAL_SCENARIOS.md`에 정리했습니다.
여기에는 초보 사용자가 작은 가방 세 가지 중 하나를 고르고, 필요한 기법을 단계별로 연습해
진도를 저장한 뒤 실제 작품 제작 가이드를 여는 다중 턴 커리큘럼도 포함됩니다.
`evals/run_codex.py`는
이미 저장된 ChatGPT/Codex 인증으로 오프라인 응답을 교육 기준표에 따라 평가하는 개발용 실행기입니다.
API 키를 전달하지 않으며, 실제 이미지 fixture가 없는 사진 사례는 평가에서 제외합니다.

```bash
OPENAI_API_KEY= uv run python evals/run_codex.py
```

사진 진단과 사진 기반 도안 생성은 실제 샘플 이미지를 첨부하는 별도 회귀 실행기로 확인합니다.
두 시나리오 모두 저장된 구독 인증만 사용하고 결과를 캐시합니다.

```bash
OPENAI_API_KEY= KNITCOACH_MODEL_PROVIDER=codex_exec uv run python evals/run_codex_images.py
```

Streamlit UI는 다음 명령으로 실행한 뒤 통합 컴포즈, 퀵 커맨드, 샘플 도안 카드,
오른쪽 상세 패널, 이미지 첨부와 최근 대화 복원을 확인합니다. 개발자 정보는 debug mode에서만
보여야 합니다.

```bash
uv run streamlit run main.py
```

기존 notebook 전체 실행 검증도 유지합니다.

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

## 기법 설명·영상 전략

- 코바늘 20개와 대바늘 20개, 총 40개 기법에 설명·기호·단계·실수 교정·연습·성공 체크를 미리 작성했습니다.
- 기법 라이브러리는 도구·난이도·카테고리 필터와 기법명·영문명·약어 검색을 지원합니다.
- 에이전트도 같은 카탈로그의 별칭을 사용하므로 새 기법을 추가할 때 별도 감지 목록을 수정할 필요가 없습니다.
- 완전 초보용 핵심 기법은 바늘이야기처럼 국내에서 널리 알려진 뜨개 채널의 실제 손동작 영상을 먼저 보여줍니다.
  사슬뜨기는 `코바늘 마스터 #1`의 바늘·실 잡기와 `#2`의 사슬뜨기를 순서대로 연결했습니다.
- 사용자 제공 영상 중 `oPhgAX0AX9M`은 사슬뜨기가 아니라 새 실 연결 영상이므로, 해당 기법을 추가할 때 쓰도록 보류했습니다.
- 각 상세 화면은 8초·16:9 손동작 영상을 위한 복사 가능한 AI 생성 프롬프트도 제공합니다.
- 영상 AI가 손과 실의 관계, 기호나 자막을 부정확하게 만들 수 있으므로 실제 손동작의 주 교재로 사용하지 않습니다.
  표준 도안 기호·보조 표시·학습 아이콘을 구분해 SVG로 렌더링하고, 동작 복습은 실제 영상 프레임의 구조를 보존한 주석 카드로 제공합니다.
- 파일럿은 사슬뜨기·짧은뜨기·겉뜨기입니다. 생성한 파일을
  `assets/techniques/<slug>/video.mp4`에 넣으면 placeholder가 `st.video`로 자동 교체됩니다.
- 사슬뜨기는 바늘이야기 `코바늘 마스터 #2`에서 추출한 실제 장면에 학습 표시만 더한 카드 5장과
  12.9초 복습 MP4가 포함되어 있습니다. 손·바늘·실의 구조를 생성형 AI로 다시 그리지 않으며,
  앱 실행이나 agent turn에서 영상 API를 호출하지 않습니다.
- `scripts/build_chain_reference_cards.py`로 원본 프레임을 변경하지 않고 같은 카드 구성을 재생성할 수 있습니다.
- 코바늘 영문 표기는 `긴뜨기=half double crochet(hdc)`, `한길긴뜨기=double crochet(dc)`로 구분합니다.
