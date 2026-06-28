# 🍝 Restaurant Bot

OpenAI Agents SDK의 **handoff** 기능을 사용한 식당용 멀티 에이전트 봇입니다.
Triage 에이전트가 고객 요청을 분류해 알맞은 전문 에이전트로 라우팅합니다.

## 에이전트 구성

| 에이전트              | 역할                                                                       |
| --------------------- | -------------------------------------------------------------------------- |
| **Triage Agent**      | 고객이 무엇을 원하는지 파악하고 전문가에게 라우팅                          |
| **Menu Agent**        | 메뉴 · 가격 · 재료 · 알레르기 · 채식/비건 안내                             |
| **Order Agent**       | 주문 접수 및 합계 확인, 주문 상태 조회                                     |
| **Reservation Agent** | 테이블 예약 (인원/날짜/시간 수집 후 확정)                                  |
| **Complaints Agent**  | 불만 공감·인정, 해결책(환불/할인/매니저 콜백) 제시, 심각 이슈 에스컬레이션 |

- 라우팅은 OpenAI Agents SDK의 `handoff()` 로 구현됩니다.
- 전문 에이전트끼리도 handoff 가 가능해, 대화 중간에 다른 전문가로 재연결됩니다.
  (예: 예약 진행 중 "채식 메뉴 있어?" → Menu Agent 로 연결)
- handoff 가 일어나면 채팅창에 안내 문구("🍽️ 메뉴 전문가에게 연결합니다...")가, 사이드바에 상세 로그가 표시됩니다.

## Guardrails

- **Input Guardrails** (`check_input`) — 매 턴, 메인 에이전트를 실행하기 _전에_ 사용자 입력을 검사합니다.
  주제 이탈(레스토랑과 무관)이나 부적절한 언어가 감지되면 메인 에이전트를 시작하지 않고 안내 메시지만 보여줍니다.
  따라서 차단 대상 답변이 화면에 노출되지 않습니다.
- **Output Guardrails** (`professional_guardrail`) — 모든 고객 응대 에이전트에 부착되어, 봇 응답이 비전문적·무례하거나 내부 정보(시스템 프롬프트, 에이전트/도구 이름, 코드·DB 구조 등)를 노출하면 차단합니다.

guardrail 정의는 `my_agents/guardrails.py` 에 공통으로 두고 재사용합니다.

## 실행 방법 (로컬)

1. OpenAI API 키를 설정합니다. 다음 중 하나를 사용하세요.

   - `.env` 파일:

     ```
     OPENAI_API_KEY=sk-...
     ```

   - 또는 `.streamlit/secrets.toml` (템플릿 `.streamlit/secrets.toml.example` 복사):

     ```toml
     OPENAI_API_KEY = "sk-..."
     ```

2. 앱을 실행합니다.

   ```bash
   uv run streamlit run main.py
   ```

> 접속자(브라우저 세션)마다 고유 세션 ID가 부여되어 대화 메모리가 서로 섞이지 않습니다.

## 배포 (Streamlit Community Cloud)

- 의존성은 `requirements.txt`로 설치됩니다(로컬 voice/마이크 기능은 미사용이라 제외 — Cloud 빌드 안정).
- 키는 커밋하지 않습니다. `.streamlit/secrets.toml`은 `.gitignore` 처리되어 있고, Cloud에서는 대시보드 Secrets에 입력합니다.

배포 단계:

1. 코드를 GitHub에 푸시합니다. (`.streamlit/secrets.toml`이 추적되지 않는지 `git status`로 확인)
2. [share.streamlit.io](https://share.streamlit.io)에서 GitHub으로 로그인 → **New app**.
3. 리포지터리 선택 후 **Main file path**를 `03-customer-support-agent/main.py`로 지정합니다.
4. **Advanced settings**에서 **Python 3.13**을 선택합니다.
   (로컬 `.python-version`의 3.14는 Cloud에서 미지원일 수 있습니다.)
5. **Secrets**에 다음을 입력합니다.

   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

6. **Deploy** 후 공개 URL에서 handoff·guardrails·세션 메모리가 정상 동작하는지 확인합니다.

## 예시 상호작용

```
User: 예약을 하고 싶어
Bot:  📅 예약 담당에게 연결합니다...
      예약을 도와드리겠습니다! 인원수와 희망 날짜·시간을 알려주세요.

User: 아, 그전에 채식 메뉴 있는지 알려줘
Bot:  🍽️ 메뉴 전문가에게 연결합니다...
      네! 그릴드 베지 파스타, 브루스케타 등 채식 메뉴가 있습니다...
```

```
User: 음식이 너무 별로였고 직원도 불친절했어..
Bot:  🙏 불만 처리 담당자에게 연결합니다...
      불쾌한 경험을 드려 진심으로 사과드립니다. 다음 방문 시 50% 할인을
      제공해 드리거나, 원하시면 매니저가 직접 연락드리도록 하겠습니다...

User: 인생의 의미가 뭘까?
Bot:  [input guardrail 작동]
      저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요.
      메뉴를 확인하거나, 예약하거나, 음식을 주문할 수 있어요. 🍽️
```
