"""Canonical tool, notion, brand, and gauge guidance for KnitCoach."""

from typing import Literal

from pydantic import BaseModel, Field

Craft = Literal["crochet", "needle_knitting", "both"]
ToolCategory = Literal["needle", "essential", "notion", "finishing", "measurement"]
Experience = Literal["first_project", "beginner", "upgrading"]


class ToolGuide(BaseModel):
    slug: str
    name: str
    craft: Craft
    category: ToolCategory
    icon: str
    summary: str
    best_for: list[str]
    not_for: list[str] = Field(default_factory=list)
    size_guide: list[str] = Field(default_factory=list)
    buying_tips: list[str]
    budget_choice: str
    upgrade_choice: str
    related_projects: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)


class BrandGuide(BaseModel):
    name: str
    crafts: list[Craft]
    tier: Literal["budget", "mid", "premium"]
    known_for: str
    good_time_to_buy: str
    caution: str
    official_url: str | None = None


TOOL_GUIDES = [
    ToolGuide(slug="single-crochet-hook", name="기본 코바늘", craft="crochet", category="needle", icon="⌝",
        summary="한쪽 끝에 갈고리가 있는 가장 보편적인 코바늘입니다. 손잡이 없는 일자형과 쿠션 그립형이 있습니다.",
        best_for=["사슬·짧은뜨기·한길긴뜨기", "코스터·가방·인형"], not_for=["한 번에 많은 코를 바늘에 걸어 두는 아후강 뜨기"],
        size_guide=["호수 이름보다 몸통에 적힌 mm를 확인하세요.", "실 라벨의 권장 mm에서 시작하고, 한두 단을 떠 코가 너무 빡빡하거나 흐물거리는지 보고 손땀과 원하는 조직에 맞춰 조정합니다."],
        buying_tips=["첫 구매는 세트보다 프로젝트에 필요한 한 규격만", "코를 잡는 머리 모양과 손잡이의 피로감 확인", "금속은 잘 미끄러지고, 대나무·목재는 제동감이 큼"],
        budget_choice="다이소·무명 알루미늄/그립 코바늘 한 개로 손에 맞는지 시험하세요. 매장별 규격과 재고는 달라질 수 있습니다.",
        upgrade_choice="오래 뜬다면 튤립 ETIMO, Clover Amour, KnitPro 같은 그립형 단품을 비교해 보세요.",
        related_projects=["코스터", "키링", "가방", "아미구루미"], aliases=["코바늘", "그립 코바늘", "일자 코바늘"]),
    ToolGuide(slug="steel-crochet-hook", name="레이스·스틸 코바늘", craft="crochet", category="needle", icon="⌟",
        summary="아주 가는 레이스실과 뜨개실을 위한 가는 금속 코바늘입니다. 일반 코바늘의 번호 체계와 반대로 보일 수 있어 mm 확인이 중요합니다.",
        best_for=["레이스", "도일리", "비즈·뜨개 액세서리"], not_for=["중간 굵기 실로 하는 첫 연습"],
        size_guide=["2mm 안팎 이하의 가는 규격이 많습니다.", "제품 번호보다 mm 표기를 우선하세요."],
        buying_tips=["실과 도안이 요구하는 정확한 mm만 구매", "작은 머리가 실 가닥을 쪼개지 않는지 확인"],
        budget_choice="첫 작품 도안이 요구할 때만 단품으로 구입하세요.", upgrade_choice="정교한 레이스를 반복한다면 손잡이형 스틸 훅을 고려하세요.", aliases=["레이스 코바늘", "스틸 훅"]),
    ToolGuide(slug="tunisian-hook", name="아후강·튀니지안 코바늘", craft="crochet", category="needle", icon="⟶",
        summary="코를 하나씩 완성하지 않고 여러 코를 긴 몸통이나 케이블에 걸어 왕복하는 아후강(튀니지안) 뜨개용 바늘입니다.",
        best_for=["두툼하고 직조 같은 조직", "넓은 패널·담요·가방"], not_for=["일반 코바늘 기초만 연습하는 첫날"],
        size_guide=["mm는 바늘 몸통의 굵기이고, cm는 일자 바늘 또는 케이블의 길이입니다.", "짧은 샘플은 일자형, 코가 많은 넓은 작품은 케이블 연결형이 편합니다."],
        buying_tips=["작품 폭보다 충분한 코 수용 길이", "케이블 연결부에 코가 걸리지 않는지 확인"],
        budget_choice="먼저 짧은 일자형 한 규격으로 조직이 취향인지 시험하세요.", upgrade_choice="큰 작품을 계속한다면 교체식 케이블형 세트를 고려하세요.", aliases=["아후강", "아프간", "튀니지안", "tunisian", "afghan"]),
    ToolGuide(slug="straight-needles", name="직선 대바늘", craft="needle_knitting", category="needle", icon="╱╱",
        summary="양끝이 분리된 곧은 바늘 한 쌍입니다. 구조가 단순해 평면뜨기를 이해하기 쉽습니다.",
        best_for=["작은 평면 샘플", "목도리·패널"], not_for=["넓고 무거운 편물", "원통형 작품"],
        size_guide=["mm는 바늘 지름, cm는 바늘 전체 길이입니다.", "코 수가 많다면 줄바늘이 손목 부담과 코 수용에 유리합니다."],
        buying_tips=["실 라벨 권장 mm 우선", "짧은 바늘은 휴대가 쉽지만 수용 코 수가 적음"],
        budget_choice="입문용 대나무·알루미늄 한 쌍으로 겉뜨기 샘플부터 시험하세요.", upgrade_choice="같은 평면 작업을 오래 한다면 손에 맞는 재질의 줄바늘도 비교하세요.", related_projects=["목도리", "스와치"]),
    ToolGuide(slug="fixed-circular", name="고정형 줄바늘", craft="needle_knitting", category="needle", icon="∪",
        summary="두 바늘 끝이 케이블로 영구 연결된 대바늘입니다. 평면과 원형 모두 가능하고 무게를 케이블에 분산합니다.",
        best_for=["목도리·숄 같은 넓은 평면", "모자·몸통 원형뜨기"],
        size_guide=["mm는 바늘 팁의 굵기이고, cm는 두 팁과 케이블을 합친 완성 길이로 표기하는 제품이 많습니다.", "같은 4mm 바늘도 40cm·60cm·80cm처럼 서로 다른 완성 길이를 고를 수 있습니다."],
        buying_tips=["바늘 mm와 전체 길이를 함께 확인", "케이블의 말림과 연결부 걸림 확인"],
        budget_choice="완성할 작품 규격이 정해졌다면 저가 고정형 한 개가 세트보다 경제적입니다.", upgrade_choice="자주 쓰는 규격은 ChiaoGoo, addi, KnitPro 등 케이블 특성이 다른 제품을 비교하세요.", related_projects=["모자", "스웨터", "숄", "목도리"], aliases=["줄바늘", "원형 바늘", "circular"]),
    ToolGuide(slug="interchangeable-needles", name="교체식 줄바늘 세트", craft="needle_knitting", category="needle", icon="⇄",
        summary="바늘 팁과 여러 길이의 케이블을 나사·결합 방식으로 바꿔 쓰는 시스템입니다.",
        best_for=["여러 굵기와 크기의 작품을 꾸준히 만드는 사람", "케이블 길이를 자주 바꾸는 의류"], not_for=["취향과 주력 규격을 아직 모르는 첫 구매"],
        size_guide=["브랜드·라인마다 팁과 케이블 호환 범위가 다릅니다.", "세트의 케이블 표기 길이가 완성 전체 길이인지 케이블 단독 길이인지 확인하세요."],
        buying_tips=["연결부가 풀리지 않는지", "팁 재질·날카로움·길이", "추가 케이블과 스토퍼의 국내 구입 용이성"],
        budget_choice="처음부터 큰 세트를 사기보다 같은 시스템의 팁 한 쌍과 케이블 하나를 시험하세요.", upgrade_choice="취향이 정해지면 KnitPro, ChiaoGoo, addi 등 한 시스템으로 확장하세요.", aliases=["교체형 줄바늘", "조립식 줄바늘", "인터체인저블"]),
    ToolGuide(slug="dpn", name="장갑바늘(DPN)", craft="needle_knitting", category="needle", icon="✣",
        summary="양쪽 끝이 모두 뾰족한 짧은 바늘 4–5개로 작은 원통을 나누어 뜹니다.",
        best_for=["양말", "장갑 손가락", "소매 끝", "모자 꼭대기"], not_for=["코가 바늘 사이에서 빠지는 것이 아직 부담스러운 첫 연습"],
        size_guide=["mm는 각 바늘의 굵기, cm는 각 바늘 한 개의 전체 길이입니다.", "굵기는 실·게이지에 맞추고 길이는 한 바늘이 맡을 코 수와 작품 크기에 맞춥니다."],
        buying_tips=["미끄러운 실은 대나무·목재가 안정적", "빠른 작업은 금속이 유리"],
        budget_choice="양말·장갑 도안을 실제 시작할 때 필요한 한 규격만 구입하세요.", upgrade_choice="작은 원통을 자주 뜨면 매직루프나 짧은 줄바늘과도 비교하세요.", aliases=["장갑 바늘", "양말 바늘", "double pointed"]),
    ToolGuide(slug="short-long-tips", name="숏팁·롱팁", craft="needle_knitting", category="needle", icon="↔",
        summary="교체식 또는 줄바늘의 바늘 팁 길이 차이입니다. 숏팁은 작은 둘레, 롱팁은 손 전체로 잡는 일반 작업에 맞습니다.",
        best_for=["숏팁: 40cm 안팎 모자·넥라인·소매", "롱팁: 60cm 이상 평면·몸통·숄"],
        size_guide=["mm는 팁의 굵기, cm·inch는 팁 자체의 길이입니다.", "긴 팁 두 개는 짧은 케이블과 결합해도 작은 완성 둘레를 만들기 어렵습니다."],
        buying_tips=["손이 큰 사람은 숏팁 피로감 시험", "사용하려는 케이블의 최소 완성 길이 확인"],
        budget_choice="처음에는 도안에 적힌 전체 길이의 고정형 줄바늘이 단순합니다.", upgrade_choice="모자·소매가 많으면 숏팁, 성인 의류·숄이 많으면 롱팁 비중이 큰 세트를 고르세요.", aliases=["숏 팁", "롱 팁", "short tip", "long tip"]),
    ToolGuide(slug="stitch-markers", name="표시링·마커", craft="both", category="essential", icon="○",
        summary="단 시작, 무늬 반복, 늘림·줄임 위치를 표시합니다. 잠금형은 편물에도 걸 수 있고 링형은 바늘 사이를 이동합니다.",
        best_for=["원형 단 시작", "무늬 반복", "실수 위치 표시"], buying_tips=["대바늘은 바늘보다 큰 내경", "코바늘은 빠지지 않는 잠금형", "실과 대비되는 색"],
        budget_choice="안전핀형 플라스틱 마커나 대비색 폐실로 충분합니다.", upgrade_choice="뜨는 방식에 맞춰 얇은 링형과 잠금형을 나누어 준비하세요.", aliases=["표시링", "단수링", "마커", "표시 고리"]),
    ToolGuide(slug="tapestry-needle", name="돗바늘·마무리 바늘", craft="both", category="finishing", icon="—",
        summary="큰 귀와 뭉툭한 끝으로 실 끝을 숨기고 편물을 잇습니다.", best_for=["실 정리", "매트리스 스티치", "조립"],
        size_guide=["굵은 실은 큰 귀, 가는 실은 작은 바늘", "끝이 뭉툭하면 실 가닥을 덜 쪼갭니다."], buying_tips=["굵기별 2–3개", "휘어진 팁은 입체 조립에 편리"],
        budget_choice="플라스틱 또는 금속 혼합 세트면 대부분의 첫 작품에 충분합니다.", upgrade_choice="자주 쓰는 실 굵기에 맞는 튤립·Clover 등의 케이스형 세트를 고려하세요.", aliases=["돗바늘", "태피스트리 바늘", "실정리 바늘"]),
    ToolGuide(slug="scissors", name="쪽가위·수예 가위", craft="both", category="essential", icon="✂",
        summary="실을 깨끗하게 자르는 작은 가위입니다.", best_for=["실 교체", "마무리"], not_for=["철사·굵은 부자재 절단"], buying_tips=["끝이 너무 길지 않고 케이스가 있는 제품", "아이와 함께 쓰면 안전 캡 필수"],
        budget_choice="잘 드는 작은 문구·다이소 가위로 시작해도 됩니다.", upgrade_choice="휴대가 잦으면 캡이나 접이식이 있는 수예용을 고르세요.", aliases=["가위", "실가위", "쪽가위"]),
    ToolGuide(slug="measure-gauge", name="줄자·바늘 게이지자", craft="both", category="measurement", icon="▤",
        summary="작품과 스와치 크기를 재고, 표기가 지워진 바늘의 mm를 구멍으로 확인합니다.", best_for=["게이지 측정", "완성 치수 확인", "바늘 규격 확인"],
        buying_tips=["늘어나지 않는 줄자", "게이지자는 사용하는 mm 범위를 포함", "10cm 눈금이 명확한 자"],
        budget_choice="집의 자와 줄자로 시작할 수 있습니다.", upgrade_choice="바늘 규격을 많이 보유하면 mm 구멍과 10cm 창이 함께 있는 게이지자가 편합니다.", aliases=["줄자", "게이지자", "바늘 호수 자"]),
    ToolGuide(slug="counter-holder", name="단수 카운터·코막음 도구", craft="needle_knitting", category="notion", icon="#",
        summary="뜬 단 수를 기록하고 쉬는 동안 살아 있는 코를 안전하게 보관합니다.", best_for=["반복 무늬", "소매 두 짝", "목둘레·어깨 대기 코"],
        buying_tips=["카운터는 손으로 즉시 누르기 쉬운지", "코홀더 대신 폐실도 가능"],
        budget_choice="메모 앱·종이와 대비색 폐실이면 충분합니다.", upgrade_choice="긴 프로젝트에는 클릭형 카운터와 케이블 스토퍼가 편합니다.", aliases=["단수계", "카운터", "코홀더", "코막음 핀"]),
    ToolGuide(slug="blocking", name="블로킹 도구", craft="both", category="finishing", icon="◇",
        summary="완성 편물을 세탁 후 치수와 형태에 맞춰 말리는 매트·녹슬지 않는 핀·와이어입니다.", best_for=["레이스", "모티브 연결", "의류 치수 정리"],
        buying_tips=["핀은 녹 방지 여부", "매트는 작품 크기만큼 연결 가능한지", "실 라벨 세탁법 우선"],
        budget_choice="수건과 평평한 매트, 녹슬지 않는 핀으로 시작하세요.", upgrade_choice="레이스·숄을 자주 만들면 블로킹 와이어와 눈금 매트가 편합니다.", aliases=["블로킹 매트", "T핀", "블로킹 와이어"]),
    ToolGuide(slug="project-notions", name="작품 부자재", craft="both", category="notion", icon="＋",
        summary="가방 손잡이·D링·지퍼·단추·스냅·안전눈·솜처럼 작품의 기능과 형태를 완성하는 재료입니다.", best_for=["가방", "파우치", "인형", "의류 여밈"],
        buying_tips=["도안 치수와 색상·도금 확인", "세탁 가능 여부", "어린이용 안전눈은 연령·고정 상태 확인"],
        budget_choice="샘플을 뜬 뒤 실제 완성 치수를 재고 필요한 수량만 구입하세요.", upgrade_choice="무거운 가방은 하중을 견디는 손잡이와 보강재를 선택하세요.", aliases=["부자재", "D링", "지퍼", "단추", "안전눈", "솜"]),
]

# Illustrations are generated project assets, not standard knitting symbols.
TOOL_IMAGE_PATHS = {
    "single-crochet-hook": "assets/tools/basic-crochet-hook.png",
    "steel-crochet-hook": "assets/tools/steel-crochet-hook.png",
    "tunisian-hook": "assets/tools/tunisian-hook-v2.png",
    "straight-needles": "assets/tools/straight-needles.png",
    "fixed-circular": "assets/tools/fixed-circular.png",
    "interchangeable-needles": "assets/tools/interchangeable-needles.png",
    "dpn": "assets/tools/dpn.png",
    "short-long-tips": "assets/tools/short-long-tips.png",
    "stitch-markers": "assets/tools/stitch-markers.png",
    "tapestry-needle": "assets/tools/tapestry-needle.png",
    "scissors": "assets/tools/scissors.png",
    "measure-gauge": "assets/tools/measure-gauge.png",
    "counter-holder": "assets/tools/counter-holder.png",
    "blocking": "assets/tools/blocking.png",
    "project-notions": "assets/tools/project-notions.png",
}

# Diameter and length are intentionally separate. A millimetre value describes
# shaft/tip diameter; a centimetre value describes needle, tip, cable, or the
# completed circular needle length stated in ``measured_as``.
KNITTING_NEEDLE_DIAMETER_ROWS = [
    {"marking": "0–2호", "mm": "2.1 · 2.4 · 2.7mm", "yarn_start": "레이스·핑거링"},
    {"marking": "3–5호", "mm": "3.0 · 3.3 · 3.6mm", "yarn_start": "핑거링·스포츠"},
    {"marking": "6–8호", "mm": "3.9 · 4.2 · 4.5mm", "yarn_start": "스포츠·DK"},
    {"marking": "9–11호", "mm": "4.8 · 5.1 · 5.4mm", "yarn_start": "DK·워스티드"},
    {"marking": "12–15호", "mm": "5.7 · 6.0 · 6.3 · 6.6mm", "yarn_start": "워스티드·아란"},
    {"marking": "점보", "mm": "7mm 이상은 실제 지름 표기 우선", "yarn_start": "벌키 이상"},
]

TOOL_DIAMETER_TABLES: dict[str, list[dict[str, str]]] = {
    "single-crochet-hook": [
        {"marking": "1/0", "mm": "1.80mm", "yarn_start": "아주 가는 레이스실"},
        {"marking": "2/0", "mm": "2.00mm", "yarn_start": "레이스·아주 가는 실"},
        {"marking": "3/0", "mm": "2.20mm", "yarn_start": "레이스·핑거링"},
        {"marking": "4/0", "mm": "2.50mm", "yarn_start": "핑거링·가는 면사"},
        {"marking": "5/0", "mm": "3.00mm", "yarn_start": "가는 면사·스포츠"},
        {"marking": "6/0", "mm": "3.50mm", "yarn_start": "스포츠·DK"},
        {"marking": "7/0", "mm": "4.00mm", "yarn_start": "DK·라이트 워스티드"},
        {"marking": "7.5/0", "mm": "4.50mm", "yarn_start": "라이트 워스티드"},
        {"marking": "8/0", "mm": "5.00mm", "yarn_start": "워스티드·중간 굵기"},
        {"marking": "9/0", "mm": "5.50mm", "yarn_start": "워스티드·아란"},
        {"marking": "10/0", "mm": "6.00mm", "yarn_start": "아란·벌키"},
        {"marking": "10.5/0", "mm": "6.50mm", "yarn_start": "벌키"},
    ],
    "steel-crochet-hook": [
        {"marking": "No. 0", "mm": "약 1.75mm", "yarn_start": "굵은 레이스실"},
        {"marking": "No. 2–6", "mm": "약 1.50–1.00mm", "yarn_start": "가는 레이스실"},
        {"marking": "No. 8–14", "mm": "약 0.90–0.50mm", "yarn_start": "아주 가는 실·비즈"},
    ],
    "tunisian-hook": [
        {"marking": "제품의 mm", "mm": "3.0–4.5mm", "yarn_start": "가는 실·얇은 조직"},
        {"marking": "제품의 mm", "mm": "5.0–6.5mm", "yarn_start": "중간 굵기 실"},
        {"marking": "제품의 mm", "mm": "7.0–12.0mm", "yarn_start": "굵은 실·성긴 조직"},
    ],
}

for _slug in ("straight-needles", "fixed-circular", "interchangeable-needles", "dpn", "short-long-tips"):
    TOOL_DIAMETER_TABLES[_slug] = KNITTING_NEEDLE_DIAMETER_ROWS

TOOL_LENGTH_TABLES: dict[str, list[dict[str, str]]] = {
    "tunisian-hook": [
        {"length": "23cm", "measured_as": "일자 바늘 전체 길이", "use": "연습 스와치·좁은 패널"},
        {"length": "33cm", "measured_as": "일자 바늘 전체 길이", "use": "목도리·중간 폭 패널"},
        {"length": "60 · 80 · 100cm", "measured_as": "플렉시블 제품 전체 길이(제품 표기 확인)", "use": "가방·담요·넓은 패널"},
    ],
    "straight-needles": [
        {"length": "20–25cm", "measured_as": "바늘 한 개의 전체 길이", "use": "스와치·작은 패널"},
        {"length": "30–35cm", "measured_as": "바늘 한 개의 전체 길이", "use": "목도리·중간 폭 평면"},
        {"length": "40cm 안팎", "measured_as": "바늘 한 개의 전체 길이", "use": "넓은 평면—무거우면 줄바늘이 편함"},
    ],
    "fixed-circular": [
        {"length": "40cm", "measured_as": "팁 끝↔팁 끝 완성 길이", "use": "모자·넥라인·작은 둘레"},
        {"length": "60cm", "measured_as": "팁 끝↔팁 끝 완성 길이", "use": "요크·어린이 몸통"},
        {"length": "80cm", "measured_as": "팁 끝↔팁 끝 완성 길이", "use": "성인 몸통·넓은 평면"},
        {"length": "100cm 이상", "measured_as": "팁 끝↔팁 끝 완성 길이", "use": "매직루프·숄·담요"},
    ],
    "interchangeable-needles": [
        {"length": "실제 케이블 20cm", "measured_as": "숏팁 결합 후 약 40cm", "use": "모자·작은 둘레"},
        {"length": "실제 케이블 35cm", "measured_as": "팁 결합 후 약 60cm", "use": "요크·중간 둘레"},
        {"length": "실제 케이블 56cm", "measured_as": "팁 결합 후 약 80cm", "use": "성인 몸통"},
        {"length": "실제 케이블 76cm", "measured_as": "팁 결합 후 약 100cm", "use": "매직루프·큰 작품"},
    ],
    "dpn": [
        {"length": "10–15cm", "measured_as": "바늘 한 개의 전체 길이", "use": "장갑 손가락·인형"},
        {"length": "15–20cm", "measured_as": "바늘 한 개의 전체 길이", "use": "양말·소매·모자 꼭대기"},
    ],
    "short-long-tips": [
        {"length": "2–3in / 약 5–7.5cm", "measured_as": "팁 한 개의 길이", "use": "아주 작은 완성 길이용 숏팁"},
        {"length": "4in / 약 10cm", "measured_as": "팁 한 개의 길이", "use": "작은 둘레와 일반 작업 사이"},
        {"length": "5in / 약 13cm", "measured_as": "팁 한 개의 길이", "use": "일반 그립·60cm 이상 완성 길이"},
    ],
}

YARN_LABEL_CHECKLIST = [
    "코바늘 그림인지 대바늘 그림인지 먼저 구분합니다.",
    "‘권장 4/0’처럼 호수만 보지 말고 옆의 ‘2.50mm’ 같은 지름 표기를 함께 확인합니다.",
    "권장 범위가 두 개라면 단단한 조직은 작은 쪽, 부드럽고 성긴 조직은 큰 쪽에서 샘플을 시작합니다.",
    "세탁법·소재·길이(m)도 확인합니다. 같은 무게(g)라도 실 길이가 길수록 대체로 더 가늘 수 있습니다.",
    "라벨 규격은 출발점입니다. 가방은 형태를 위해 한 단계 작게, 레이스·드레이프는 크게 쓰기도 하므로 도안을 우선합니다.",
]

BRAND_GUIDES = [
    BrandGuide(name="다이소·무명 입문 제품", crafts=["both"], tier="budget", known_for="낮은 진입비용과 단품 시험 구매", good_time_to_buy="첫 프로젝트에 필요한 규격 하나만 확인할 때", caution="매장·시점별 재고와 규격이 달라 mm·마감 상태를 직접 확인"),
    BrandGuide(name="Tulip", crafts=["both"], tier="premium", known_for="ETIMO 그립 코바늘과 수예 바늘", good_time_to_buy="손 피로를 줄일 그립형 단품을 찾을 때", caution="세트 전 주력 mm 단품을 먼저 시험", official_url="https://en.tulip-japan.co.jp/knitting_needle/"),
    BrandGuide(name="Clover", crafts=["both"], tier="mid", known_for="Amour 코바늘과 폭넓은 수예 부자재", good_time_to_buy="기본 도구를 안정적으로 업그레이드할 때", caution="라인별 손잡이와 재질 차이 확인", official_url="https://www.clover-mfg.com/"),
    BrandGuide(name="KnitPro", crafts=["both"], tier="mid", known_for="재질과 팁 길이가 다양한 교체식 줄바늘·튀니지안 훅", good_time_to_buy="선호 재질과 케이블 시스템이 정해졌을 때", caution="제품군별 팁·케이블 호환 범위 확인", official_url="https://www.knitpro.eu/"),
    BrandGuide(name="ChiaoGoo", crafts=["needle_knitting"], tier="premium", known_for="TWIST 금속 팁과 유연한 레드 케이블", good_time_to_buy="매직루프·의류를 자주 뜨며 케이블 성능을 중시할 때", caution="팁 크기군별 케이블 연결 규격 확인", official_url="https://www.chiaogoo.com/products/"),
    BrandGuide(name="addi", crafts=["both"], tier="premium", known_for="다양한 고정형·교체식 원형바늘", good_time_to_buy="주력 프로젝트와 바늘 촉감 취향이 분명할 때", caution="팁 모양과 케이블 길이를 라인별로 확인", official_url="https://addi.de/en/"),
]

YARN_WEIGHT_GUIDE = [
    {"weight": "0 Lace", "examples": "레이스", "needle_mm": "1.5–2.25", "hook_mm": "1.4–2.25", "knit_sts_10cm": "33–40"},
    {"weight": "1 Super Fine", "examples": "삭스·핑거링", "needle_mm": "2.25–3.25", "hook_mm": "2.25–3.5", "knit_sts_10cm": "27–32"},
    {"weight": "2 Fine", "examples": "스포츠·베이비", "needle_mm": "3.25–3.75", "hook_mm": "3.5–4.5", "knit_sts_10cm": "23–26"},
    {"weight": "3 Light", "examples": "DK·라이트 워스티드", "needle_mm": "3.75–4.5", "hook_mm": "4.5–5.5", "knit_sts_10cm": "21–24"},
    {"weight": "4 Medium", "examples": "워스티드·아란", "needle_mm": "4.5–5.5", "hook_mm": "5.5–6.5", "knit_sts_10cm": "16–20"},
    {"weight": "5 Bulky", "examples": "청키", "needle_mm": "5.5–8", "hook_mm": "6.5–9", "knit_sts_10cm": "12–15"},
    {"weight": "6 Super Bulky", "examples": "슈퍼 벌키·로빙", "needle_mm": "8–12.75", "hook_mm": "9–15", "knit_sts_10cm": "7–11"},
]

_BY_SLUG = {item.slug: item for item in TOOL_GUIDES}


def list_tools(craft: str | None = None, category: str | None = None, query: str = "") -> list[ToolGuide]:
    items = TOOL_GUIDES
    if craft:
        items = [item for item in items if item.craft in {craft, "both"}]
    if category:
        items = [item for item in items if item.category == category]
    if query.strip():
        needle = query.casefold().strip()
        items = [item for item in items if needle in " ".join([item.name, item.summary, *item.aliases, *item.related_projects]).casefold()]
    return items


def get_tool(slug: str) -> ToolGuide | None:
    return _BY_SLUG.get(slug)


def resolve_tools(text: str) -> list[ToolGuide]:
    lowered = text.casefold()
    generic_terms = {"코바늘", "대바늘", "바늘", "가위", "부자재"}
    scored: list[tuple[ToolGuide, int]] = []
    for item in TOOL_GUIDES:
        hits = [term for term in [item.name, *item.aliases] if term.casefold() in lowered]
        if hits:
            scored.append((item, max(len(term) for term in hits if term not in generic_terms) if any(term not in generic_terms for term in hits) else 1))
    if any(score > 1 for _, score in scored):
        scored = [(item, score) for item, score in scored if score > 1]
    return [item for item, _ in scored]


def recommend_tools(text: str, tool_type: str = "unknown", level: str = "beginner") -> list[str]:
    """Return deterministic, catalog-backed recommendations for coaching."""
    matches = resolve_tools(text)
    project_map = {
        "모자": "fixed-circular", "비니": "fixed-circular", "스웨터": "interchangeable-needles",
        "양말": "dpn", "장갑": "dpn", "목도리": "straight-needles", "아후강": "tunisian-hook",
        "튀니지안": "tunisian-hook", "인형": "single-crochet-hook", "가방": "single-crochet-hook",
    }
    if not matches:
        for keyword, slug in project_map.items():
            if keyword in text:
                matches.append(_BY_SLUG[slug])
                break
    if not matches:
        slug = "single-crochet-hook" if tool_type == "crochet" else "fixed-circular" if tool_type == "needle_knitting" else "measure-gauge"
        matches = [_BY_SLUG[slug]]
    result = []
    for item in matches[:3]:
        choice = item.budget_choice if level in {"beginner", "first_project", "unknown"} or any(word in text for word in ["입문", "초보", "가성비", "다이소", "처음"]) else item.upgrade_choice
        result.append(f"{item.name}: {choice}")
    return result


def calculate_gauge(stitches: float, rows: float, width_cm: float, height_cm: float, target_stitches: float | None = None) -> dict:
    if min(stitches, rows, width_cm, height_cm) <= 0:
        raise ValueError("모든 측정값은 0보다 커야 합니다.")
    stitches_10cm = stitches / width_cm * 10
    rows_10cm = rows / height_cm * 10
    advice = "목표 게이지가 있으면 비교해 바늘을 조정하세요."
    if target_stitches:
        delta = stitches_10cm - target_stitches
        if abs(delta) < 0.5:
            advice = "목표 코 게이지에 가깝습니다. 단 게이지와 세탁 후 치수도 확인하세요."
        elif delta > 0:
            advice = "10cm 안의 코가 목표보다 많아 조직이 촘촘합니다. 더 큰 바늘로 다시 스와치를 떠 보세요."
        else:
            advice = "10cm 안의 코가 목표보다 적어 조직이 느슨합니다. 더 작은 바늘로 다시 스와치를 떠 보세요."
    return {"stitches_10cm": stitches_10cm, "rows_10cm": rows_10cm, "advice": advice}
