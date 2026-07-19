"""Project-based beginner curricula that end in a finished knitting project."""

from copy import deepcopy

from pydantic import BaseModel


class CurriculumStep(BaseModel):
    id: str
    title: str
    technique: str
    why: str
    practice: str
    success_check: str
    project_use: str


class ProjectCurriculum(BaseModel):
    id: str
    title: str
    tool_type: str
    difficulty: str
    outcome: str
    estimated_time: str
    cover_image: str = ""
    reference_video_url: str = ""
    reference_video_title: str = ""
    badge: str = "입문 작품"
    recommended_for: str = ""
    yarn_requirement: str = ""
    needle_size: str = ""
    gauge: str = ""
    finished_size: str = ""
    construction: str = ""
    pattern_format: str = "기호·영문 약어 기본 도안 + 초보자 한글 설명"
    beginner_pattern: list[str] = []
    written_pattern: list[str] = []
    symbol_legend: list[str] = []
    pattern_techniques: list[str] = []
    starter_kit: list[str]
    steps: list[CurriculumStep]
    project_guide: list[str]
    assumptions: list[str]


CURRICULA: dict[str, ProjectCurriculum] = {
    "crochet-flat-mini-bag": ProjectCurriculum(
        id="crochet-flat-mini-bag",
        title="코바늘 납작 미니 토트백",
        tool_type="crochet",
        difficulty="첫 작품 추천",
        outcome="휴대폰보다 작은 납작한 손잡이 가방",
        estimated_time="기법 연습 후 3–5시간",
        cover_image="assets/projects/crochet-flat-mini-bag.png",
        badge="첫 가방 추천",
        recommended_for="짧은뜨기를 반복해 형태가 또렷한 첫 가방을 만들고 싶은 사람",
        starter_kit=[
            "중간 굵기 면사 또는 아크릴실 1볼(밝은 단색이면 코가 잘 보입니다)",
            "실 라벨 권장 범위의 코바늘 1개(보통 4–5mm에서 많이 시작)",
            "잠금형 표시링 1개, 돗바늘, 작은 가위, 줄자",
        ],
        steps=[
            CurriculumStep(
                id="chain",
                title="사슬뜨기로 가방 너비 만들기",
                technique="사슬뜨기(chain stitch)",
                why="가방 바닥의 시작 너비를 정하는 첫 줄입니다.",
                practice="사슬 15코를 두 번 만들어 코 크기와 전체 길이가 비슷한지 비교하세요.",
                success_check="15코를 세었을 때 빠진 코 없이 한 줄의 굵기가 일정하면 완료입니다.",
                project_use="완성 가방에서는 사슬 21코로 시작합니다.",
            ),
            CurriculumStep(
                id="single-crochet",
                title="짧은뜨기로 가방 몸판 만들기",
                technique="짧은뜨기(single crochet)",
                why="촘촘하고 형태가 잘 잡혀 첫 가방 몸판에 적합합니다.",
                practice="사슬 12코 위에 짧은뜨기를 뜨고 5단짜리 작은 사각형을 만드세요.",
                success_check="시작과 마지막 단의 코 수가 같고 양쪽 가장자리가 곧으면 완료입니다.",
                project_use="같은 코 수를 유지하며 앞·뒤 몸판 높이를 만듭니다.",
            ),
            CurriculumStep(
                id="slip-stitch",
                title="빼뜨기로 단 끝과 가장자리 정리하기",
                technique="빼뜨기(slip stitch)",
                why="코 높이를 늘리지 않고 몸판 가장자리와 손잡이 연결부를 정리합니다.",
                practice="짧은뜨기 샘플 한쪽 가장자리에 빼뜨기 8코를 연속으로 떠 보세요.",
                success_check="새 단이 솟아오르지 않고 가장자리가 납작하게 정리되면 완료입니다.",
                project_use="가방 입구와 손잡이 연결부를 깔끔하게 마감합니다.",
            ),
            CurriculumStep(
                id="handle",
                title="사슬 손잡이 연결하고 마무리하기",
                technique="사슬뜨기(chain stitch)",
                why="배운 사슬뜨기와 빼뜨기를 조합해 손잡이를 만듭니다.",
                practice="사슬 20코를 만든 뒤 시작점 가까이에 빼뜨기로 연결해 고리 하나를 만드세요.",
                success_check="고리를 가볍게 당겼을 때 연결부가 풀리지 않고 좌우 길이가 비슷하면 완료입니다.",
                project_use="가방 양쪽에 같은 길이의 손잡이를 연결합니다.",
            ),
        ],
        project_guide=[
            "준비: 중간 굵기 면사와 실 라벨 권장 코바늘을 사용하고, 사슬 21코가 약 12cm인지 확인합니다.",
            "몸판 1: 사슬 21코를 만들고 두 번째 사슬부터 짧은뜨기 20코를 뜹니다.",
            "몸판 2–24단: 매 단 짧은뜨기 20코를 유지해 약 24cm 길이의 직사각형을 만듭니다.",
            "접기: 직사각형을 반으로 접어 양옆을 돗바늘로 잇거나 빼뜨기로 연결합니다.",
            "손잡이: 가방 입구 양쪽에서 사슬 20코 고리를 만들고 빼뜨기로 단단히 연결합니다.",
            "마무리: 입구를 빼뜨기로 한 바퀴 정리하고 실 끝을 돗바늘로 숨깁니다.",
        ],
        assumptions=["완성 크기 약 가로 12cm × 세로 12cm", "중간 굵기 면사", "개인 장력에 따라 시작 사슬과 단 수 조정 필요"],
    ),
    "crochet-mesh-mini-bag": ProjectCurriculum(
        id="crochet-mesh-mini-bag",
        title="코바늘 네트 미니백",
        tool_type="crochet",
        difficulty="기초 다음 단계",
        outcome="구멍무늬가 있는 가벼운 미니백",
        estimated_time="기법 연습 후 4–6시간",
        cover_image="assets/projects/crochet-mesh-mini-bag.png",
        badge="기초 다음",
        recommended_for="사슬뜨기와 한길긴뜨기를 익힌 뒤 가벼운 가방에 도전하고 싶은 사람",
        starter_kit=[
            "중간 굵기 면사 1–2볼(늘어짐이 적은 실이 편합니다)",
            "실 라벨 권장 범위보다 같거나 0.5mm 큰 코바늘 1개",
            "잠금형 표시링 2개, 돗바늘, 작은 가위, 줄자",
        ],
        steps=[
            CurriculumStep(id="chain", title="사슬뜨기", technique="사슬뜨기(chain stitch)", why="바닥과 구멍무늬의 간격을 만듭니다.", practice="사슬 20코를 일정한 크기로 만드세요.", success_check="20코의 크기가 일정하면 완료입니다.", project_use="바닥과 네트 반복에 사용합니다."),
            CurriculumStep(id="double-crochet", title="한길긴뜨기", technique="한길긴뜨기(double crochet)", why="네트 무늬의 높이를 만듭니다.", practice="사슬 위에 한길긴뜨기 10코를 떠 보세요.", success_check="10코 높이가 비슷하고 두 고리씩 두 번 뺐다면 완료입니다.", project_use="가방 몸통 구멍무늬에 사용합니다."),
            CurriculumStep(id="round", title="매직링으로 원형 시작하기", technique="매직링으로 원형 시작하기(crocheting in the round)", why="바닥에서 몸통을 끊지 않고 올리는 원형 작업 방식을 익힙니다.", practice="매직링 첫 코에 표시 고리를 걸고 짧은뜨기 두 단을 이어 뜨세요.", success_check="단 시작 위치와 전체 코 수를 확인할 수 있으면 완료입니다.", project_use="가방 몸통을 한 바퀴씩 올립니다."),
            CurriculumStep(id="slip", title="빼뜨기 마감", technique="빼뜨기(slip stitch)", why="단 끝과 손잡이를 연결합니다.", practice="샘플 가장자리에 빼뜨기 10코를 뜨세요.", success_check="가장자리가 솟지 않고 납작하면 완료입니다.", project_use="입구와 손잡이를 마감합니다."),
        ],
        project_guide=[
            "준비: 중간 굵기 면사와 권장 코바늘로 10cm 네트 샘플을 먼저 만듭니다.",
            "바닥: 사슬 21코 양쪽을 짧은뜨기로 돌아 타원형 바닥을 만듭니다.",
            "몸통: 사슬 2코와 한길긴뜨기 1코를 반복해 원하는 높이까지 원형으로 뜹니다.",
            "입구: 짧은뜨기 한 단과 빼뜨기 한 단으로 늘어짐을 줄입니다.",
            "손잡이: 마주 보는 두 위치에 같은 수의 사슬을 만들고 빼뜨기로 연결합니다.",
        ],
        assumptions=["완성 크기 약 가로 14cm × 세로 16cm", "네트 무늬 전용 안감 없음", "게이지에 따라 반복 수 조정 필요"],
    ),
    "needle-flat-pouch": ProjectCurriculum(
        id="needle-flat-pouch",
        title="대바늘 납작 미니 파우치",
        tool_type="needle_knitting",
        difficulty="첫 작품 추천",
        outcome="직사각형을 접어 만드는 단추형 미니 파우치",
        estimated_time="기법 연습 후 4–6시간",
        cover_image="assets/projects/needle-flat-pouch.png",
        badge="첫 대바늘 소품",
        recommended_for="겉뜨기를 반복해 작고 실용적인 대바늘 작품을 만들고 싶은 사람",
        starter_kit=[
            "중간 굵기 실 1볼(밝은 단색이면 코가 잘 보입니다)",
            "실 라벨 권장 범위의 4.5–5mm 안팎 대바늘 한 쌍 또는 줄바늘",
            "돗바늘, 작은 가위, 줄자, 여밈용 단추 1개(선택)",
        ],
        steps=[
            CurriculumStep(id="cast-on", title="롱테일 코잡기", technique="롱테일 코잡기(long-tail cast on)", why="파우치 너비만큼 첫 코를 만듭니다.", practice="20코를 일정한 간격으로 잡아 보세요.", success_check="20코가 바늘 위에서 너무 조이지 않고 일정하면 완료입니다.", project_use="완성 파우치는 24코로 시작합니다."),
            CurriculumStep(id="knit", title="겉뜨기", technique="겉뜨기(knit stitch)", why="앞뒤 모두 겉뜨기해 말림이 적은 몸판을 만듭니다.", practice="20코로 겉뜨기 8단을 떠 보세요.", success_check="매 단 20코를 유지하고 가장자리가 크게 줄지 않으면 완료입니다.", project_use="파우치 몸판 전체를 만듭니다."),
            CurriculumStep(id="bind-off", title="덮어씌워 코막음", technique="덮어씌워 코막음(basic bind off)", why="마지막 단이 풀리지 않게 닫습니다.", practice="겉뜨기 샘플 10코를 너무 조이지 않게 막아 보세요.", success_check="마지막 가장자리가 몸판 너비와 비슷하면 완료입니다.", project_use="파우치 덮개 끝을 마감합니다."),
        ],
        project_guide=[
            "준비: 중간 굵기 실과 5mm 안팎 대바늘로 10cm 겉뜨기 샘플을 만듭니다.",
            "시작: 24코를 잡습니다.",
            "몸판: 모든 단을 겉뜨기로 약 30cm 길이까지 뜹니다.",
            "마감: 코를 느슨하게 막고 아래쪽 12cm를 접어 양옆을 돗바늘로 잇습니다.",
            "덮개: 남은 부분을 앞으로 접고 단추와 고리를 달아 닫습니다.",
        ],
        assumptions=["완성 크기 약 가로 13cm × 세로 12cm", "중간 굵기 실과 5mm 안팎 대바늘", "개인 게이지에 따라 코 수 조정 필요"],
    ),
    "crochet-round-coaster": ProjectCurriculum(
        id="crochet-round-coaster", title="코바늘 원형 티코스터", tool_type="crochet",
        difficulty="가장 쉬움", outcome="지름 약 10cm의 도톰한 원형 컵받침", estimated_time="1–2시간",
        cover_image="assets/projects/crochet-round-coaster.png", badge="첫 완성 추천",
        recommended_for="사슬뜨기와 짧은뜨기를 막 배웠고 짧은 시간 안에 첫 작품을 완성하고 싶은 사람",
        yarn_requirement="4번 중간 굵기 면사 약 20g", needle_size="4.0mm 코바늘",
        gauge="짧은뜨기 16코 × 18단 = 10cm (참고용 · 원판이 평평한지가 더 중요)",
        finished_size="지름 약 10cm", construction="매직링에서 시작해 빼뜨기로 잇지 않는 나선형 원형뜨기",
        beginner_pattern=[
            "1단 · 매직링 안에 짧은뜨기 6코를 뜨세요. 모두 6코입니다.",
            "2단 · 앞 단의 6코 각각에 짧은뜨기 2코씩 넣으세요. 모두 12코입니다.",
            "3단 · 짧은뜨기 1코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 18코입니다.",
            "4단 · 짧은뜨기 2코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 24코입니다.",
            "5단 · 짧은뜨기 3코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 30코입니다.",
            "6단 · 짧은뜨기 4코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 36코입니다.",
            "7단 · 짧은뜨기 5코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 42코입니다.",
            "8단 · 짧은뜨기 6코와 늘려뜨기 1회를 여섯 번 반복하세요. 모두 48코입니다.",
            "마무리 · 다음 코에 빼뜨기 1코를 하고 실을 10cm 남겨 자른 뒤 뒤쪽 코 사이에 숨기세요.",
        ],
        written_pattern=[
            "1단 · MR 안에 X 6코 (총 6코)", "2단 · V × 6회 (총 12코)",
            "3단 · (X, V) × 6회 (총 18코)", "4단 · (2X, V) × 6회 (총 24코)",
            "5단 · (3X, V) × 6회 (총 30코)", "6단 · (4X, V) × 6회 (총 36코)",
            "7단 · (5X, V) × 6회 (총 42코)", "8단 · (6X, V) × 6회 (총 48코)",
            "마무리 · 다음 코에 빼뜨기 1코, 실을 10cm 남겨 자르고 뒤쪽에 숨기기",
        ],
        symbol_legend=["MR = 매직링", "X = 짧은뜨기 1코", "V = 한 코에 짧은뜨기 2코", "× 6 = 괄호 안을 여섯 번 반복"],
        pattern_techniques=["매직링", "짧은뜨기", "짧은뜨기 늘려뜨기", "빼뜨기"],
        starter_kit=["4번 중간 굵기 밝은 면사 약 20g", "4.0mm 기본 코바늘", "잠금형 표시링 1개, 돗바늘, 작은 가위, 줄자"],
        steps=[
            CurriculumStep(id="round-1", title="1단 · 중심 6코", technique="매직링(magic ring)", why="원판 중심을 빈틈없이 시작합니다.", practice="매직링에 짧은뜨기 6코를 뜨고 첫 코에 표시링을 거세요.", success_check="중심이 닫히고 표시링 앞까지 정확히 6코입니다.", project_use="MR 안에 X 6"),
            CurriculumStep(id="round-2", title="2단 · 12코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="모든 코를 두 배로 늘립니다.", practice="각 코에 짧은뜨기 2코씩 뜨세요.", success_check="총 12코이며 작은 원판이 펼쳐집니다.", project_use="V × 6"),
            CurriculumStep(id="round-3", title="3단 · 18코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="늘림 사이에 짧은뜨기 한 코를 둡니다.", practice="(짧은뜨기 1코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 18코이고 늘림 여섯 곳이 고르게 놓였습니다.", project_use="(X,V) × 6"),
            CurriculumStep(id="round-4", title="4단 · 24코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="늘림 간격을 두 코로 넓혀 원판을 평평하게 키웁니다.", practice="(짧은뜨기 2코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 24코이고 원판이 평평하게 펼쳐집니다.", project_use="(2X,V) × 6"),
            CurriculumStep(id="round-5", title="5단 · 30코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="같은 규칙으로 지름을 더 키웁니다.", practice="(짧은뜨기 3코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 30코이며 가장자리가 물결치지 않습니다.", project_use="(3X,V) × 6"),
            CurriculumStep(id="round-6", title="6단 · 36코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="늘림 간격을 네 코로 넓힙니다.", practice="(짧은뜨기 4코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 36코이며 중심부터 고르게 펼쳐집니다.", project_use="(4X,V) × 6"),
            CurriculumStep(id="round-7", title="7단 · 42코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="컵을 안정적으로 올릴 지름에 가까워집니다.", practice="(짧은뜨기 5코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 42코이고 원판이 오목하지 않습니다.", project_use="(5X,V) × 6"),
            CurriculumStep(id="round-8", title="8단 · 48코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="티코스터의 최종 지름을 만듭니다.", practice="(짧은뜨기 6코, 늘려뜨기 1회)를 여섯 번 반복하세요.", success_check="총 48코, 지름 9.5–10.5cm이며 평평합니다.", project_use="(6X,V) × 6"),
            CurriculumStep(id="finish", title="마무리", technique="빼뜨기(slip stitch)", why="마지막 나선의 높이 차를 낮춥니다.", practice="다음 코에 빼뜨기하고 실 끝을 뒤쪽 세 코 이상 통과해 숨기세요.", success_check="마지막 코가 솟지 않고 실 끝이 잡아당겨도 빠지지 않습니다.", project_use="마무리"),
        ],
        project_guide=["표시링을 첫 코에 옮기며 나선형으로 뜹니다.", "매 단 6코씩 늘려 6→12→18→24코를 만듭니다.", "같은 규칙으로 30→36→42→48코까지 진행합니다.", "지름과 평평함을 확인하고 빼뜨기로 마감합니다."],
        assumptions=["4번 면사와 4.0mm 바늘 기준", "손땀이 달라 물결치면 마지막 단을 생략", "오목하면 바늘을 0.5mm 키우거나 늘림 장력을 느슨하게 조정"],
    ),
    "crochet-mini-hat-keyring": ProjectCurriculum(
        id="crochet-mini-hat-keyring", title="코바늘 미니 모자 키링", tool_type="crochet",
        difficulty="기초 2단계", outcome="챙 폭 약 5.5cm의 버킷햇 키링", estimated_time="2–3시간",
        cover_image="assets/projects/crochet-mini-hat-keyring.png", badge="두 번째 작품 추천",
        recommended_for="티코스터로 원형 늘림을 익힌 뒤 입체 형태를 처음 만들 사람",
        yarn_requirement="3번 DK 면사 약 15g", needle_size="3.5mm 코바늘",
        gauge="짧은뜨기 22코 × 24단 = 10cm", finished_size="높이 약 3.5cm · 챙 폭 약 5.5cm",
        construction="꼭대기부터 나선형으로 뜨고, BLO 한 단으로 옆면을 꺾은 뒤 챙을 늘림",
        beginner_pattern=[
            "1단 · 매직링 안에 짧은뜨기 6코를 뜨세요.",
            "2단 · 6코 각각에 짧은뜨기 2코씩 넣어 12코로 늘리세요.",
            "3단 · 짧은뜨기 1코와 늘려뜨기 1회를 여섯 번 반복해 18코를 만드세요.",
            "4단 · 짧은뜨기 2코와 늘려뜨기 1회를 여섯 번 반복해 24코를 만드세요.",
            "5단 · 24코의 뒤쪽 고리 한 가닥에만 짧은뜨기를 1코씩 떠서 옆면이 꺾일 자리를 만드세요.",
            "6–8단 · 양쪽 고리에 짧은뜨기 24코를 떠서 세 단 동안 같은 코 수를 유지하세요.",
            "9단 · 짧은뜨기 3코와 늘려뜨기 1회를 여섯 번 반복해 30코를 만드세요.",
            "10단 · 짧은뜨기 4코와 늘려뜨기 1회를 여섯 번 반복해 36코를 만드세요.",
            "11단 · 짧은뜨기 36코를 뜬 뒤 다음 코에 빼뜨기하세요.",
            "고리 · 꼭대기에 실을 연결해 사슬뜨기 8코로 고리를 만들고 같은 자리를 두 번 꿰매 키링을 고정하세요.",
        ],
        written_pattern=[
            "1단 · MR 안에 X 6 (6코)", "2단 · V × 6 (12코)", "3단 · (X,V) × 6 (18코)",
            "4단 · (2X,V) × 6 (24코)", "5단 · BLO X 24 (24코)", "6–8단 · X 24 (각 24코)",
            "9단 · (3X,V) × 6 (30코)", "10단 · (4X,V) × 6 (36코)", "11단 · X 36, 다음 코에 빼뜨기 (36코)",
            "고리 · 꼭대기 가장자리에 실을 연결해 사슬 8코 고리를 만들고 같은 자리를 두 번 꿰매 키링 부착",
        ],
        symbol_legend=["MR = 매직링", "X = 짧은뜨기", "V = 짧은뜨기 늘려뜨기", "BLO = 코의 뒤 고리에만 뜨기"],
        pattern_techniques=["매직링", "짧은뜨기", "짧은뜨기 늘려뜨기", "빼뜨기", "사슬뜨기"],
        starter_kit=["3번 DK 밝은 면사 약 15g", "3.5mm 기본 코바늘", "키링 고리 1개, 표시링, 돗바늘, 가위"],
        steps=[
            CurriculumStep(id="top-1-2", title="1–2단 · 꼭대기 12코", technique="매직링(magic ring)", why="모자 중심을 만들고 첫 늘림을 합니다.", practice="MR 6코 뒤 모든 코를 늘려 12코를 만드세요.", success_check="2단 끝 12코이며 중심 구멍이 닫혔습니다.", project_use="1–2단"),
            CurriculumStep(id="top-3-4", title="3–4단 · 꼭대기 24코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="평평한 모자 윗면을 만듭니다.", practice="18코, 24코 순서로 늘리세요.", success_check="4단 끝 24코이고 원판 지름이 약 3.5cm입니다.", project_use="3–4단"),
            CurriculumStep(id="side-5-8", title="5–8단 · 옆면 세우기", technique="짧은뜨기(single crochet)", why="BLO가 모서리를 만들고 같은 코 수가 높이를 만듭니다.", practice="5단은 뒤 고리에만 24코, 6–8단은 양 고리에 24코씩 뜨세요.", success_check="매 단 24코이며 작은 컵처럼 옆면이 섭니다.", project_use="5–8단"),
            CurriculumStep(id="brim-9-10", title="9–10단 · 챙 36코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="옆면 아래에서 챙을 펼칩니다.", practice="30코, 36코 순서로 늘리세요.", success_check="10단 끝 36코이며 챙이 고르게 펼쳐집니다.", project_use="9–10단"),
            CurriculumStep(id="finish-11", title="11단 · 챙 정리와 키링", technique="빼뜨기(slip stitch)", why="챙 끝을 정리하고 키링 연결부를 보강합니다.", practice="짧은뜨기 36코 뒤 빼뜨기하고, 꼭대기에 사슬 8코 고리를 만드세요.", success_check="챙이 평평하고 키링 고리를 당겨도 연결점이 벌어지지 않습니다.", project_use="11단·고리"),
        ],
        project_guide=["꼭대기를 6→12→18→24코로 늘립니다.", "BLO 1단 뒤 24코를 세 단 떠 옆면을 세웁니다.", "챙을 30→36코로 늘리고 한 단 고르게 뜹니다.", "빼뜨기로 마감한 뒤 사슬 고리를 두 번 보강해 키링을 답니다."],
        assumptions=["3번 DK 면사와 3.5mm 기준", "BLO는 코 위의 두 가닥 중 뒤쪽 한 가닥", "키링은 사슬 고리보다 돗바늘 보강이 안전"],
    ),
    "crochet-fishbread-keyring": ProjectCurriculum(
        id="crochet-fishbread-keyring", title="코바늘 붕어빵 키링", tool_type="crochet",
        difficulty="기초 2단계 · 매직링 다음 작품", outcome="한입 크기의 통통한 미니 붕어빵 키링", estimated_time="약 1–2시간",
        cover_image="assets/projects/crochet-fishbread-keyring-GNK16UCra7Q.jpg", badge="기초를 익힌 뒤",
        reference_video_url="https://www.youtube.com/watch?v=GNK16UCra7Q",
        reference_video_title="#붕어빵만들기 · 심쿵 미니 붕어빵 키링",
        recommended_for="매직링·짧은뜨기·늘림·줄임을 한 작은 작품 안에서 연습하고 싶은 사람",
        yarn_requirement="3번 DK 면사 또는 소품용 면혼방실 약 10–15g + 비늘·눈용 자투리실", needle_size="3.0–3.5mm 코바늘",
        gauge="고정 게이지 없음 · 솜을 넣었을 때 코 사이가 벌어지지 않는 촘촘한 장력",
        finished_size="실 굵기와 손땀에 따라 길이 약 5–8cm", construction="기둥코와 빼뜨기로 매 단을 닫는 원통형 몸통 1–10단 · 11단 늘림 · 12단 부채꼴 꼬리 4개 · 솜과 자수 마무리",
        beginner_pattern=[
            "1단 · 매직링 안에 짧은뜨기 6코를 뜨고 첫 짧은뜨기에 빼뜨기하세요. 단을 마치면 6코입니다.",
            "2단 · 기둥 사슬 1코를 뜬 뒤, 짧은뜨기 1코와 한 코에 짧은뜨기 2코를 넣는 늘려뜨기 1회를 세 번 반복하세요. 첫 짧은뜨기에 빼뜨기하면 9코입니다.",
            "3단 · 기둥 사슬 1코를 뜬 뒤, 짧은뜨기 2코와 늘려뜨기 1회를 세 번 반복하세요. 빼뜨기로 닫으면 12코입니다.",
            "4단 · 기둥 사슬 1코를 뜬 뒤, 짧은뜨기 3코와 늘려뜨기 1회를 세 번 반복하세요. 빼뜨기로 닫으면 15코입니다.",
            "5–8단 · 각 단마다 기둥 사슬 1코를 뜨고 짧은뜨기 15코를 뜬 뒤 빼뜨기로 닫으세요. 네 단 모두 15코를 유지합니다.",
            "9단 · 기둥 사슬 1코를 뜬 뒤, 짧은뜨기 3코와 짧은뜨기 2코 모아뜨기 1회를 세 번 반복하세요. 빼뜨기로 닫으면 12코입니다.",
            "10단 · 기둥 사슬 1코를 뜬 뒤 짧은뜨기 2코 모아뜨기를 6회 반복하세요. 구멍이 완전히 좁아지기 전에 솜을 넣고 빼뜨기로 닫으면 6코입니다.",
            "11단 · 기둥 사슬 1코를 뜬 뒤 6코 각각에 짧은뜨기 2코씩 넣으세요. 빼뜨기로 닫으면 꼬리 바탕 12코가 됩니다.",
            "12단 · 한 코를 건너뛰고 다음 코에 긴뜨기 3코를 넣은 뒤, 그다음 코에 빼뜨기하세요. 이 순서를 네 번 반복해 부채꼴 꼬리 4개를 만드세요.",
            "마무리 · 실 끝을 안쪽에 숨기고, 완성 영상을 보며 눈과 세로 지그재그 비늘을 수놓은 뒤 키링 고리를 두 번 이상 보강해 고정하세요.",
        ],
        written_pattern=[
            "1단 · MR 안에 X 6, 첫 코에 SLST (6코) · 6SC in MR, SLST [6]",
            "2단 · CH1, (X 1, V 1) × 3, SLST (9코) · CH1, (1SC, 1INC) × 3, SLST [9]",
            "3단 · CH1, (X 2, V 1) × 3, SLST (12코) · CH1, (2SC, 1INC) × 3, SLST [12]",
            "4단 · CH1, (X 3, V 1) × 3, SLST (15코) · CH1, (3SC, 1INC) × 3, SLST [15]",
            "5–8단 · 매 단 CH1, X 15, SLST (각 15코) · CH1, 15SC, SLST [15]",
            "9단 · CH1, (X 3, A 1) × 3, SLST (12코) · CH1, (3SC, 1DEC) × 3, SLST [12]",
            "10단 · CH1, A × 6, SLST (6코) · CH1, 6DEC, SLST [6] · 닫기 전 솜 넣기",
            "11단 · CH1, V × 6, SLST (12코) · CH1, 6INC, SLST [12]",
            "12단 · (한 코 건너뛰고 다음 코에 긴뜨기 3코, 다음 코에 SLST) × 4 · (skip 1, 3HDC in next stitch, SLST in next stitch) × 4",
            "마무리 · 실을 정리하고 영상 완성품을 참고해 눈과 세로 지그재그 비늘을 수놓은 뒤 키링 고리를 단단히 고정",
        ],
        symbol_legend=["MR = 매직링", "CH1 = 기둥 사슬 1코(코 수에 포함하지 않음)", "X/SC = 짧은뜨기", "V/INC = 한 코에 짧은뜨기 2코", "A/DEC = 짧은뜨기 2코 모아뜨기", "HDC = 긴뜨기", "SLST = 빼뜨기"],
        pattern_techniques=["매직링", "사슬뜨기", "짧은뜨기", "짧은뜨기 늘려뜨기", "짧은뜨기 2코 모아뜨기", "긴뜨기", "빼뜨기", "돗바늘 마무리"],
        starter_kit=["3번 DK 면사 또는 소품용 면혼방실 약 10–15g과 자수용 자투리실", "3.0–3.5mm 기본 코바늘", "충전솜 소량, 키링 고리, 돗바늘, 표시링, 가위"],
        steps=[
            CurriculumStep(id="round-1", title="1단 · 매직링 6코", technique="매직링(magic ring)", why="붕어빵 앞쪽 중심을 만듭니다.", practice="매직링 안에 짧은뜨기 6코를 뜨고 첫 짧은뜨기에 빼뜨기하세요.", success_check="중심이 닫히고 6코이며 빼뜨기 위치를 찾을 수 있습니다.", project_use="1단"),
            CurriculumStep(id="round-2", title="2단 · 9코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="세 곳에서 늘려 몸통을 넓힙니다.", practice="기둥 사슬 1코를 뜬 뒤, 짧은뜨기 1코와 늘려뜨기 1회를 세 번 반복하고 빼뜨기하세요.", success_check="기둥코를 제외하고 9코입니다.", project_use="2단"),
            CurriculumStep(id="round-3", title="3단 · 12코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="늘림 간격을 두 코로 넓힙니다.", practice="기둥 사슬 1코를 뜬 뒤, 짧은뜨기 2코와 늘려뜨기 1회를 세 번 반복하고 빼뜨기하세요.", success_check="단 끝 12코입니다.", project_use="3단"),
            CurriculumStep(id="round-4", title="4단 · 15코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="몸통의 최대 둘레를 만듭니다.", practice="기둥 사슬 1코를 뜬 뒤, 짧은뜨기 3코와 늘려뜨기 1회를 세 번 반복하고 빼뜨기하세요.", success_check="단 끝 15코입니다.", project_use="4단"),
            CurriculumStep(id="round-5", title="5단 · 15코 유지", technique="짧은뜨기(single crochet)", why="늘림을 멈추고 몸통 높이를 만들기 시작합니다.", practice="기둥 사슬 1코와 짧은뜨기 15코를 뜬 뒤 빼뜨기로 한 단을 닫으세요.", success_check="단 끝 15코이며 옆면이 서기 시작합니다.", project_use="5단"),
            CurriculumStep(id="round-6", title="6단 · 15코 유지", technique="짧은뜨기(single crochet)", why="같은 둘레로 몸통을 이어 갑니다.", practice="기둥 사슬 1코와 짧은뜨기 15코를 뜬 뒤 빼뜨기하세요.", success_check="단 끝 15코입니다.", project_use="6단"),
            CurriculumStep(id="round-7", title="7단 · 15코 유지", technique="짧은뜨기(single crochet)", why="몸통 길이를 더합니다.", practice="기둥 사슬 1코와 짧은뜨기 15코를 뜬 뒤 빼뜨기하세요.", success_check="단 끝 15코이며 단 연결선이 한쪽에 모입니다.", project_use="7단"),
            CurriculumStep(id="round-8", title="8단 · 15코 유지", technique="짧은뜨기(single crochet)", why="줄임 전 마지막 몸통 단입니다.", practice="기둥 사슬 1코와 짧은뜨기 15코를 뜬 뒤 빼뜨기하세요.", success_check="단 끝 15코입니다.", project_use="8단"),
            CurriculumStep(id="round-9", title="9단 · 12코로 줄이기", technique="짧은뜨기 2코 모아뜨기(single crochet 2 together)", why="몸통을 꼬리 쪽으로 좁힙니다.", practice="기둥 사슬 1코를 뜬 뒤, 짧은뜨기 3코와 짧은뜨기 2코 모아뜨기 1회를 세 번 반복하고 빼뜨기하세요.", success_check="단 끝 12코이며 줄임 세 곳이 고르게 놓였습니다.", project_use="9단"),
            CurriculumStep(id="round-10", title="10단 · 6코와 솜 넣기", technique="짧은뜨기 2코 모아뜨기(single crochet 2 together)", why="몸통 끝을 좁히고 꼬리 전에 형태를 채웁니다.", practice="기둥 사슬 1코를 뜬 뒤 짧은뜨기 2코 모아뜨기를 6회 반복하세요. 구멍이 닫히기 전에 솜을 넣고 빼뜨기하세요.", success_check="단 끝 6코이며 솜이 코 사이로 비치지 않습니다.", project_use="10단"),
            CurriculumStep(id="round-11", title="11단 · 꼬리 바탕 12코", technique="짧은뜨기 늘려뜨기(single crochet increase)", why="좁힌 끝에서 꼬리가 펼쳐질 바탕을 만듭니다.", practice="기둥 사슬 1코를 뜬 뒤 6코 각각에 짧은뜨기 2코씩 넣고 빼뜨기하세요.", success_check="단 끝 12코이며 몸통 끝보다 넓어졌습니다.", project_use="11단"),
            CurriculumStep(id="round-12", title="12단 · 부채꼴 꼬리 4개", technique="긴뜨기(half double crochet)", why="긴뜨기 세 코 묶음 네 개로 꼬리 윤곽을 만듭니다.", practice="(한 코 건너뛰기, 다음 코에 긴뜨기 3코, 다음 코에 빼뜨기)를 4회 반복하세요.", success_check="크기가 비슷한 부채꼴 네 개가 꼬리 둘레에 생겼습니다.", project_use="12단"),
            CurriculumStep(id="finish", title="자수·키링 마무리", technique="빼뜨기(slip stitch)", why="마지막 고리를 닫은 뒤 눈과 비늘을 더하고 키링을 안전하게 고정합니다.", practice="빼뜨기로 꼬리 끝을 닫고, 영상 완성품을 보며 눈과 세로 지그재그 비늘을 수놓은 뒤 키링 연결부를 두 번 보강하세요.", success_check="실 끝이 안쪽에 숨고 키링을 가볍게 당겨도 풀리지 않습니다.", project_use="마무리"),
        ],
        project_guide=["1–4단은 6→9→12→15코로 늘리며 매 단 빼뜨기로 닫습니다.", "5–8단은 15코를 유지해 몸통 길이를 만듭니다.", "9–10단은 12→6코로 줄이고 닫기 전에 솜을 넣습니다.", "11단은 6코를 모두 늘려 12코 꼬리 바탕을 만듭니다.", "12단은 긴뜨기 3코 부채를 네 번 만들고 자수와 키링으로 마무리합니다."],
        assumptions=["출처 영상: https://www.youtube.com/watch?v=GNK16UCra7Q", "기둥 사슬 1코는 단의 코 수에 포함하지 않음", "나선형이 아니라 매 단 첫 코에 빼뜨기로 닫는 방식", "11단 영문 표기의 마지막 코 수는 증가 결과에 맞춰 [12]로 교정", "한국어 긴뜨기는 HDC이므로 첨부 영문 3DC를 3HDC로 교정", "어린이용이면 눈은 플라스틱 부품 대신 실로 수놓기"],
    ),
    "crochet-flat-pouch": ProjectCurriculum(
        id="crochet-flat-pouch", title="코바늘 조임끈 납작 파우치", tool_type="crochet",
        difficulty="첫 실용 작품", outcome="약 11×12cm의 조임끈 파우치", estimated_time="4–6시간",
        cover_image="assets/projects/crochet-flat-pouch.png", badge="반복 연습 추천",
        recommended_for="짧은뜨기를 일정한 코 수로 유지해 실제 쓰는 소품을 만들고 싶은 사람",
        yarn_requirement="4번 중간 굵기 면사 80–100g", needle_size="4.0mm 코바늘",
        gauge="짧은뜨기 18코 × 20단 = 10cm", finished_size="가로 약 11cm × 세로 약 12cm",
        construction="사슬 양쪽 면을 떠 좁은 타원형 바닥을 만든 뒤, 편물을 뒤집지 않고 매 단 빼뜨기로 닫아 원통형으로 올리는 조임끈 파우치",
        beginner_pattern=[
            "시작 · 사슬뜨기 20코를 만드세요.",
            "1단 · 바늘에서 두 번째 사슬부터 짧은뜨기 18코를 뜨고, 마지막 사슬에 짧은뜨기 3코를 넣으세요. 편물을 뒤집지 말고 사슬의 반대쪽 고리를 따라 짧은뜨기 17코를 뜬 뒤, 시작 사슬에 짧은뜨기 2코를 더 넣으세요. 첫 짧은뜨기에 빼뜨기하면 모두 40코입니다.",
            "2–24단 · 빼뜨기 다음에 기둥 사슬 1코를 올리고 짧은뜨기 40코를 뜬 뒤 첫 짧은뜨기에 빼뜨기하세요. 기둥 사슬은 코 수에 넣지 않고, 편물을 뒤집지 않은 채 같은 방향으로 반복합니다.",
            "25단 · 기둥 사슬 3코와 사슬 1코를 뜨고 다음 코를 건너뛰세요. 그다음 코에 한길긴뜨기 1코를 뜬 뒤, ‘사슬 1코, 한 코 건너뛰기, 다음 코에 한길긴뜨기 1코’를 단 끝까지 반복해 끈 구멍 20개를 만드세요. 기둥 사슬의 세 번째 코에 빼뜨기합니다.",
            "26단 · 기둥 사슬 1코를 올리고 한길긴뜨기마다 짧은뜨기 1코, 사슬 공간마다 짧은뜨기 1코를 떠서 모두 40코를 만드세요. 첫 짧은뜨기에 빼뜨기합니다.",
            "조임끈 · 사슬뜨기 75코를 만들어 25단의 구멍에 번갈아 통과시키고 앞 중앙에서 묶으세요.",
        ],
        written_pattern=[
            "시작 · CH 20",
            "R1 · 2nd CH부터 SC 18, last CH에 3SC, foundation CH 반대쪽에 SC 17, first CH에 2SC, SLST [40]",
            "R2–24 · CH1, SC 40, SLST [40] · do not turn",
            "R25 · CH4(첫 DC+CH1), SK1, DC, [CH1, SK1, DC] × 18, CH1, SK1, SLST to 3rd CH [20 DC + 20 CH-sp]",
            "R26 · CH1, 각 DC와 CH-sp에 SC 1, SLST [40]",
            "조임끈 · CH 75, R25의 CH-sp에 번갈아 통과시켜 묶기",
        ],
        symbol_legend=["CH = 사슬뜨기", "SC/X = 짧은뜨기", "DC/T = 한길긴뜨기", "SLST = 빼뜨기", "SK1 = 한 코 건너뛰기", "CH-sp = 사슬 공간", "CH1 기둥코는 코 수에 포함하지 않음", "[ ] × 숫자 = 대괄호 안 반복"],
        pattern_techniques=["사슬뜨기", "짧은뜨기", "빼뜨기", "한길긴뜨기"],
        starter_kit=["4번 중간 굵기 밝은 면사 80–100g", "4.0mm 기본 코바늘", "표시링 2개, 돗바늘, 가위, 줄자"],
        steps=[
            CurriculumStep(id="base-round-1", title="1단 · 사슬 양쪽을 떠 40코 바닥", technique="사슬뜨기(chain stitch)", why="옆선을 잇지 않아도 되는 좁은 타원형 바닥을 만듭니다.", practice="사슬 20코의 양쪽 면을 따라 18코+3코+17코+2코를 뜨고 첫 코에 빼뜨기하세요.", success_check="1단 끝 정확히 40코이고 사슬을 중심으로 코가 타원형으로 둘러져 있습니다.", project_use="1단"),
            CurriculumStep(id="body-rounds-2-24", title="2–24단 · 원통 몸판 40코", technique="짧은뜨기(single crochet)", why="접거나 잇지 않고 파우치 몸통을 둥글게 올립니다.", practice="매 단 CH1, SC40, SLST를 반복하고 편물을 뒤집지 마세요.", success_check="매 단 40코이며 높이가 약 11.5–12cm, 연결선은 한쪽에 곧게 놓입니다.", project_use="2–24단"),
            CurriculumStep(id="eyelets-round-25", title="25단 · 조임끈 구멍 20개", technique="한길긴뜨기(double crochet)", why="한길긴뜨기 사이 사슬 공간으로 끈이 지나갑니다.", practice="DC와 CH1 공간을 번갈아 총 20개씩 만들고 빼뜨기로 닫으세요.", success_check="한길긴뜨기 20개와 사슬 공간 20개가 번갈아 놓입니다.", project_use="25단"),
            CurriculumStep(id="edge-round-26", title="26단 · 입구 짧은뜨기 40코", technique="짧은뜨기(single crochet)", why="끈 구멍 위를 정돈해 입구가 늘어지는 것을 줄입니다.", practice="각 DC와 CH-sp에 짧은뜨기 1코씩 떠 40코를 만들고 빼뜨기하세요.", success_check="입구가 고르고 마지막 단은 정확히 40코입니다.", project_use="26단"),
            CurriculumStep(id="cord", title="사슬 75코 조임끈", technique="사슬뜨기(chain stitch)", why="입구를 실제로 여닫게 합니다.", practice="사슬 75코를 구멍에 번갈아 통과시키고 앞에서 묶으세요.", success_check="양끝 길이가 비슷하고 당기면 입구가 닫힙니다.", project_use="조임끈"),
        ],
        project_guide=["사슬 20코를 만들고 사슬 양쪽을 떠 1단 40코의 좁은 타원형 바닥을 만듭니다.", "매 단 빼뜨기로 닫고 기둥 사슬 1코를 올린 뒤, 편물을 뒤집지 않고 짧은뜨기 40코를 24단까지 반복합니다.", "25단에 한길긴뜨기 20개와 사슬 공간 20개를 번갈아 만들어 끈 통로를 냅니다.", "26단은 짧은뜨기 40코로 입구를 정리합니다.", "사슬 75코 끈을 통과시켜 완성합니다."],
        assumptions=["게이지가 다르면 단수보다 완성 높이 약 12cm를 우선", "매 단 첫 짧은뜨기에 빼뜨기로 닫는 연결 원형뜨기이며 편물을 뒤집지 않음", "단 시작의 기둥 사슬 1코는 코 수에 포함하지 않음", "옆선 잇기 없이 사슬 양쪽에서 바로 원통 몸판을 올림", "조임끈 길이는 묶어 본 뒤 5–10코 조정 가능"],
    ),
    "needle-garter-scarf": ProjectCurriculum(
        id="needle-garter-scarf", title="대바늘 가터뜨기 미니 목도리", tool_type="needle_knitting",
        difficulty="대바늘 첫 작품", outcome="겉뜨기만 반복하는 약 14×90cm 목도리", estimated_time="여러 날에 나누어 8–12시간",
        cover_image="assets/projects/needle-garter-scarf.png", badge="대바늘 첫 추천",
        recommended_for="코잡기·겉뜨기·코막음 세 기법으로 첫 대바늘 작품을 완성하고 싶은 사람",
        yarn_requirement="5번 굵은 실 두 색 합계 220m 이상", needle_size="6.5mm 대바늘 또는 60cm 줄바늘",
        gauge="18코로 시작해 몇 단 뜬 뒤 폭이 약 13–15cm인지 확인", finished_size="폭 약 14cm × 길이 약 90cm",
        construction="18코 직사각형 · A색 18단/B색 18단 줄무늬를 6회 반복",
        beginner_pattern=[
            "시작 · A색 실로 롱테일 방식의 코잡기 18코를 만드세요.",
            "1–18단 · A색으로 모든 코를 겉뜨기하세요. 매 단 18코를 유지합니다.",
            "19–36단 · B색으로 바꾸고 모든 코를 겉뜨기하세요. 매 단 18코를 유지합니다.",
            "줄무늬 · A색 18단과 B색 18단을 한 묶음으로 보고 총 여섯 번 반복하세요. 길이 약 90cm를 우선 확인합니다.",
            "마무리 · 마지막 단 다음에 겉뜨기 방식으로 18코를 느슨하게 코막음하세요.",
            "실 정리 · 색을 바꿀 때 남긴 실 끝을 같은 색의 가로 골을 따라 돗바늘로 5cm 이상 숨기세요.",
        ],
        written_pattern=[
            "시작 · A색으로 롱테일 코잡기 18코", "1–18단 · A색으로 모든 코 겉뜨기 (매 단 18코)",
            "19–36단 · B색으로 모든 코 겉뜨기 (매 단 18코)",
            "줄무늬 · 1–36단의 A색 18단 + B색 18단을 총 6회 반복 (216단, 약 90cm)",
            "마무리 · B색 마지막 단 다음에 겉뜨기 방식으로 18코를 느슨하게 코막음",
            "실 정리 · 색을 바꿀 때 남긴 12cm 실 끝을 같은 색 골을 따라 돗바늘로 5cm 이상 숨기기",
        ],
        symbol_legend=["CO = 코잡기", "K = 겉뜨기", "BO = 코막음", "가터뜨기 = 앞뒤 모든 단을 겉뜨기"],
        pattern_techniques=["롱테일 코잡기", "겉뜨기", "가터뜨기", "덮어씌워 코막음"],
        starter_kit=["5번 굵은 밝은 실 A·B색 합계 220m 이상", "6.5mm 대바늘 한 쌍 또는 60cm 줄바늘", "돗바늘, 가위, 줄자, 단수 표시 도구"],
        steps=[
            CurriculumStep(id="cast-on", title="코잡기 18코", technique="롱테일 코잡기(long-tail cast on)", why="목도리를 시작할 18코를 너무 조이지 않게 만듭니다.", practice="A색 실로 롱테일 코잡기 18코를 만드세요.", success_check="18코가 바늘 위에서 움직일 여유가 있고, 몇 단 떠 본 폭이 13–15cm 정도입니다.", project_use="시작"),
            CurriculumStep(id="stripe-1", title="A색 1–18단", technique="겉뜨기(knit stitch)", why="첫 가터 줄무늬와 곧은 가장자리를 만듭니다.", practice="모든 단 18코를 겉뜨기하세요.", success_check="18단 뒤에도 18코이고 가로 골이 9개 보입니다.", project_use="1–18단"),
            CurriculumStep(id="stripe-2", title="B색 19–36단", technique="가터뜨기(garter stitch)", why="색 바꾸기와 같은 장력 유지를 익힙니다.", practice="B색을 연결해 18단을 더 뜨세요.", success_check="36단 뒤 18코이고 두 색 줄무늬 폭이 비슷합니다.", project_use="19–36단"),
            CurriculumStep(id="repeat", title="줄무늬 6회 · 총 216단", technique="가터뜨기(garter stitch)", why="같은 36단 묶음을 반복해 90cm 길이를 만듭니다.", practice="A 18단+B 18단 묶음이 총 여섯 번 되도록 반복하세요.", success_check="총 216단 안팎, 길이 88–92cm, 폭 13–15cm입니다.", project_use="줄무늬 반복"),
            CurriculumStep(id="bind-off", title="18코 느슨하게 코막음", technique="덮어씌워 코막음(basic bind off)", why="끝 폭을 유지하며 풀리지 않게 닫습니다.", practice="겉뜨기 방식으로 18코를 느슨하게 막고 실 끝을 숨기세요.", success_check="시작과 끝 폭이 비슷하고 당겼을 때 코막음이 조이지 않습니다.", project_use="마무리"),
        ],
        project_guide=["A색으로 18코를 잡고 몇 단 뜬 뒤 폭이 약 13–15cm인지 확인합니다.", "A색으로 겉뜨기 18단을 뜹니다.", "B색으로 바꿔 겉뜨기 18단을 뜹니다.", "두 줄무늬를 총 여섯 번 반복해 약 90cm로 만듭니다.", "18코를 느슨하게 코막음하고 모든 실 끝을 숨깁니다."],
        assumptions=["5번 굵은 실과 6.5mm 바늘 기준", "몇 단 뜬 뒤 실제 폭이 13–15cm인지 확인", "단수보다 완성 길이 90cm를 우선하되 색은 18단 단위로 변경", "긴 성인 머플러가 아니라 첫 완성을 위한 짧은 목도리"],
    ),
    "needle-ribbed-muffler": ProjectCurriculum(
        id="needle-ribbed-muffler", title="대바늘 1×1 골지 머플러", tool_type="needle_knitting",
        difficulty="기초 2단계", outcome="약 14×120cm의 신축성 있는 골지 머플러", estimated_time="여러 날에 나누어 12–18시간",
        cover_image="assets/projects/needle-ribbed-muffler.png", badge="겉·안뜨기 다음",
        recommended_for="가터 목도리 뒤 안뜨기와 실 앞뒤 이동을 익히려는 사람",
        yarn_requirement="4번 중간 굵기 울 혼방 실 350–400m", needle_size="5.0mm 대바늘 또는 60cm 줄바늘",
        gauge="1×1 고무뜨기에서 편 상태 20코 × 24단 = 10cm · 세탁 전 샘플 기준", finished_size="편하게 놓아 폭 약 14cm × 길이 약 120cm",
        construction="짝수 28코로 시작해 모든 단 K1,P1 반복 · 약 288단",
        beginner_pattern=[
            "시작 · 롱테일 방식으로 28코를 잡으세요.",
            "1단 · 겉뜨기 1코와 안뜨기 1코를 번갈아 모두 14회 반복하세요. 단을 마치면 28코입니다.",
            "2–12단 · 아래에서 겉뜨기로 보이는 코는 겉뜨기하고, 안뜨기로 보이는 코는 안뜨기하며 세로 골을 이어 가세요.",
            "13단 이후 · 겉뜨기 1코와 안뜨기 1코를 번갈아 뜨는 순서를 길이 120cm까지 반복하세요.",
            "마무리 · 겉코는 겉뜨기하고 안코는 안뜨기하면서 현재 무늬대로 28코를 느슨하게 코막음하세요.",
            "실 정리 · 실 끝을 편물 뒤쪽의 안뜨기 골을 따라 돗바늘로 5cm 이상 숨기세요.",
        ],
        written_pattern=[
            "시작 · 롱테일 코잡기 28코", "1단 · [K1, P1] × 14 (28코)",
            "2–12단 · 보이는 겉코는 K, 안코는 P로 떠 세로 골 확인 (각 28코)",
            "13단 이후 · [K1,P1] × 14를 길이 120cm까지 반복 (게이지 기준 약 288단)",
            "마무리 · 겉코는 겉뜨기, 안코는 안뜨기로 뜨면서 무늬대로 느슨하게 28코 코막음",
            "실 정리 · 앞면의 V 기둥이 아닌 뒤쪽 안뜨기 골을 따라 실 끝을 5cm 이상 숨기기",
        ],
        symbol_legend=["CO = 코잡기", "K1 = 겉뜨기 1코", "P1 = 안뜨기 1코", "[K1,P1] × 14 = 두 코 한 묶음을 14회 반복", "BO = 코막음"],
        pattern_techniques=["롱테일 코잡기", "겉뜨기", "안뜨기", "1×1 고무뜨기", "덮어씌워 코막음"],
        starter_kit=["4번 중간 굵기 밝은 울 혼방 실 350–400m", "5.0mm 대바늘 한 쌍 또는 60cm 줄바늘", "표시링 2개, 돗바늘, 가위, 줄자, 단수 표시 도구"],
        steps=[
            CurriculumStep(id="swatch", title="게이지 샘플과 28코 시작", technique="롱테일 코잡기(long-tail cast on)", why="골지는 당기면 폭이 크게 달라져 샘플 확인이 필요합니다.", practice="1×1 골지 샘플을 편하게 놓아 게이지를 재고 28코를 잡으세요.", success_check="28코이며 샘플을 잡아 늘리지 않은 폭으로 계산했습니다.", project_use="시작"),
            CurriculumStep(id="row-1", title="1단 · K1, P1 반복", technique="안뜨기(purl stitch)", why="실을 코 사이로 앞뒤 이동하며 첫 골을 만듭니다.", practice="[겉1, 안1]을 14회 반복하세요.", success_check="1단 끝 28코이며 코 사이에 불필요한 가로 실걸림이 없습니다.", project_use="1단"),
            CurriculumStep(id="rows-2-12", title="2–12단 · 세로 골 확인", technique="1×1 고무뜨기(1x1 ribbing)", why="보이는 코대로 떠야 골이 세로로 이어집니다.", practice="겉코는 겉뜨기, 안코는 안뜨기로 12단까지 뜨세요.", success_check="28코이고 V 기둥과 안뜨기 골이 어긋나지 않습니다.", project_use="2–12단"),
            CurriculumStep(id="repeat", title="길이 120cm까지 반복", technique="1×1 고무뜨기(1x1 ribbing)", why="같은 무늬를 유지해 머플러 길이를 완성합니다.", practice="28코를 유지하며 120cm 또는 약 288단까지 반복하세요.", success_check="폭 13–15cm, 길이 약 120cm이며 빠진 골이 없습니다.", project_use="13단 이후"),
            CurriculumStep(id="bind-off", title="무늬대로 느슨한 코막음", technique="덮어씌워 코막음(basic bind off)", why="골지 신축성을 보존하며 끝을 닫습니다.", practice="겉코는 겉뜨기, 안코는 안뜨기로 떠 가며 28코를 느슨히 막으세요.", success_check="끝단 폭이 몸판보다 눈에 띄게 좁지 않습니다.", project_use="마무리"),
        ],
        project_guide=["1×1 골지 게이지를 재고 28코를 잡습니다.", "첫 단부터 겉1·안1을 14회 반복합니다.", "보이는 겉코는 겉뜨기, 안코는 안뜨기로 12단까지 확인합니다.", "같은 무늬로 길이 120cm까지 진행합니다.", "무늬대로 느슨하게 코막음하고 뒤쪽 골에 실 끝을 숨깁니다."],
        assumptions=["4번 실과 5.0mm 바늘 기준", "골지는 잡아 늘리지 않고 편하게 놓아 폭 측정", "가터 목도리보다 안뜨기와 실 위치 전환이 있어 두 번째 대바늘 작품으로 권장"],
    ),
}

CURATED_BEGINNER_PROJECT_IDS = [
    "crochet-round-coaster",
    "crochet-mini-hat-keyring",
    "crochet-fishbread-keyring",
    "crochet-flat-pouch",
    "needle-garter-scarf",
    "needle-ribbed-muffler",
]


def detect_curriculum(text: str) -> str | None:
    lowered = text.casefold()
    curated_aliases = {
        "crochet-round-coaster": ("원형 티코스터", "티코스터", "컵받침"),
        "crochet-mini-hat-keyring": ("미니 모자 키링", "모자 키링"),
        "crochet-fishbread-keyring": ("붕어빵 키링", "붕어빵"),
        "crochet-flat-pouch": ("조임끈 납작 파우치", "코바늘 파우치", "조임끈 파우치"),
        "needle-garter-scarf": ("가터뜨기 미니 목도리", "가터 목도리", "미니 목도리"),
        "needle-ribbed-muffler": ("1×1 골지 머플러", "골지 머플러", "고무뜨기 머플러"),
    }
    for curriculum_id, aliases in curated_aliases.items():
        if any(alias in lowered for alias in aliases):
            return curriculum_id
    if any(word in lowered for word in ("네트 미니", "네트 가방", "메쉬 미니", "메쉬 가방")):
        return "crochet-mesh-mini-bag"
    if any(word in lowered for word in ("대바늘 파우치", "납작 미니 파우치", "대바늘 미니")):
        return "needle-flat-pouch"
    if any(word in lowered for word in ("미니 토트", "납작 미니 토트", "코바늘 토트")):
        return "crochet-flat-mini-bag"
    return None


def beginner_project_ids(project_type: str = "", tool_type: str = "unknown") -> list[str]:
    if project_type == "키링/keyring":
        return ["crochet-mini-hat-keyring", "crochet-fishbread-keyring"]
    if project_type == "컵받침/coaster":
        return ["crochet-round-coaster"]
    if project_type == "목도리/scarf":
        return ["needle-garter-scarf", "needle-ribbed-muffler"]
    if project_type == "가방/bag":
        return ["crochet-flat-pouch", "crochet-flat-mini-bag", "needle-flat-pouch"]
    if tool_type == "crochet":
        return CURATED_BEGINNER_PROJECT_IDS[:4]
    if tool_type == "needle_knitting":
        return CURATED_BEGINNER_PROJECT_IDS[4:]
    return CURATED_BEGINNER_PROJECT_IDS.copy()


def new_learning_program(curriculum_id: str) -> dict:
    return {
        "curriculum_id": curriculum_id,
        "current_step": 0,
        "completed_steps": [],
        "status": "awaiting_tools",
    }


def activate_learning_program(program: dict) -> dict:
    """Unlock technique practice only after the learner confirms materials."""
    updated = deepcopy(program)
    if updated.get("status") in {"preview", "preview_complete"}:
        updated["current_step"] = 0
        updated["completed_steps"] = []
    updated["status"] = "active"
    return updated


def mark_learning_program_shopping(program: dict) -> dict:
    """Remember that the learner has no materials and needs purchase guidance."""
    updated = deepcopy(program)
    updated["status"] = "shopping"
    return updated


def preview_learning_program(program: dict) -> dict:
    """Open the curriculum step-by-step without claiming the learner has materials."""
    updated = deepcopy(program)
    updated["status"] = "preview"
    updated["current_step"] = 0
    updated["completed_steps"] = []
    return updated


def restart_learning_program(program: dict) -> dict:
    """Return to the first authored step when the learner explicitly asks to restart."""
    updated = deepcopy(program)
    updated["current_step"] = 0
    updated["completed_steps"] = []
    if updated.get("status") not in {"active", "preview"}:
        updated["status"] = "preview"
    return updated


def advance_learning_program(program: dict) -> dict:
    updated = deepcopy(program)
    curriculum = CURRICULA[updated["curriculum_id"]]
    index = updated["current_step"]
    step_id = curriculum.steps[index].id
    is_preview = updated.get("status") == "preview"
    if not is_preview and step_id not in updated["completed_steps"]:
        updated["completed_steps"].append(step_id)
    if index + 1 < len(curriculum.steps):
        updated["current_step"] = index + 1
    else:
        updated["status"] = "preview_complete" if is_preview else "project_ready"
    return updated


def current_curriculum_step(program: dict) -> CurriculumStep | None:
    if not program or program.get("status") not in {"active", "preview"}:
        return None
    return CURRICULA[program["curriculum_id"]].steps[program["current_step"]]


def curriculum_choices_markdown() -> str:
    return (
        "### 처음 만들기 좋은 작은 가방 3가지\n\n"
        "**가장 추천하는 작품은 코바늘 납작 미니 토트백**이에요. 작은 크기이고 같은 동작을 반복해 첫 완성 경험을 만들기 좋습니다.\n\n"
        "1. **코바늘 납작 미니 토트백 · 첫 작품 추천**  \n"
        "   사슬뜨기 → 짧은뜨기 → 빼뜨기 → 손잡이 연결\n\n"
        "2. **코바늘 네트 미니백 · 기초 다음 단계**  \n"
        "   사슬뜨기 → 한길긴뜨기 → 매직링으로 원형 시작하기 → 빼뜨기\n\n"
        "3. **대바늘 납작 미니 파우치 · 첫 작품 추천**  \n"
        "   코 잡기 → 겉뜨기 → 코 막음 → 옆선 잇기\n\n"
        "원하는 이름을 그대로 말해 주세요. 작품을 고르면 먼저 가지고 있는 실과 바늘을 확인하고, 준비가 끝난 뒤에만 필요한 기법 연습을 시작합니다."
    )
