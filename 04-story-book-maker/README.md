# 📖 Story Book Maker (Google ADK)

테마를 입력하면 5페이지 어린이 동화를 만들고, 각 페이지의 삽화를 생성하는 Google ADK 파이프라인입니다.

## 에이전트 구성

| 에이전트 | 역할 |
| --- | --- |
| **Story Writer Agent** | 테마 → 5페이지 구조화 동화(페이지별 `text` + `visual_description`)를 작성해 State(`story_book`)에 저장 |
| **Illustrator Agent** | State의 `story_book`을 읽어 페이지별 이미지를 생성하고 Artifact로 저장 |

- 두 에이전트는 `SequentialAgent`로 묶여 **Story Writer → Illustrator** 순서로 실행됩니다.
- 데이터 공유는 **ADK State**(`output_key="story_book"`)로 이루어집니다.
- 텍스트 생성: OpenAI `gpt-4o` (LiteLlm), 이미지 생성: OpenAI `gpt-image-1`.
- 생성된 이미지는 `page_1.jpeg` ~ `page_5.jpeg` 형태의 **Artifact**로 저장되어 ADK Web UI에서 확인할 수 있습니다.

## 실행 방법

1. `story_book_maker/.env` 파일에 OpenAI API 키를 설정합니다.

   ```
   OPENAI_API_KEY=sk-...
   ```

2. 이 디렉터리(`04-story-book-maker/`)에서 ADK Web UI를 실행합니다.

   ```bash
   uv run adk web
   ```

3. 브라우저에서 `story_book_maker` 앱을 선택하고, 채팅창에 동화 테마를 입력합니다.

   - 예: `보라색 하늘을 탐험하는 작은 토끼`

4. 결과 확인:
   - **State 탭**: `story_book`에 5페이지 구조화 데이터가 저장됨
   - **Artifacts 탭**: `page_1.jpeg` ~ `page_5.jpeg` 삽화 5장이 표시됨

## 예시 출력

```
Page 1:
  Text:   "옛날 옛적에, 베니라는 작은 토끼가 살았습니다."
  Visual: "버섯 집 앞에 서 있는 작은 흰 토끼"
  Image:  page_1.jpeg (Artifact)

Page 2:
  Text:   "베니는 탐험을 좋아했는데, 오늘은 하늘이 보라색이었어요!"
  Visual: "보라색 하늘을 올려다보는 토끼"
  Image:  page_2.jpeg (Artifact)
...
```
