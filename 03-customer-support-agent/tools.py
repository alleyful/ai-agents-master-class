import streamlit as st
from agents import AgentHooks, RunContextWrapper, function_tool

from models import CustomerContext


# ---------------------------------------------------------------------------
# Mock 데이터 (인메모리)
# ---------------------------------------------------------------------------

MENU = {
    "전채": {
        "브루스케타": {
            "price": 9000,
            "ingredients": ["바게트", "토마토", "바질", "마늘", "올리브오일"],
            "allergens": ["글루텐"],
            "vegetarian": True,
            "vegan": True,
        },
        "버섯 크림 수프": {
            "price": 11000,
            "ingredients": ["양송이버섯", "양파", "생크림", "버터"],
            "allergens": ["우유"],
            "vegetarian": True,
            "vegan": False,
        },
    },
    "메인": {
        "마르게리타 피자": {
            "price": 17000,
            "ingredients": ["도우", "토마토소스", "모짜렐라", "바질"],
            "allergens": ["글루텐", "우유"],
            "vegetarian": True,
            "vegan": False,
        },
        "그릴드 베지 파스타": {
            "price": 16000,
            "ingredients": ["파스타", "주키니", "파프리카", "올리브오일", "마늘"],
            "allergens": ["글루텐"],
            "vegetarian": True,
            "vegan": True,
        },
        "안심 스테이크": {
            "price": 34000,
            "ingredients": ["소고기 안심", "버터", "로즈마리", "감자"],
            "allergens": ["우유"],
            "vegetarian": False,
            "vegan": False,
        },
    },
    "디저트": {
        "티라미수": {
            "price": 8000,
            "ingredients": ["마스카포네", "에스프레소", "레이디핑거", "계란"],
            "allergens": ["우유", "글루텐", "계란"],
            "vegetarian": True,
            "vegan": False,
        },
    },
}


def _all_dishes():
    """{ dish_name: info } 형태로 전체 메뉴를 평탄화."""
    flat = {}
    for category in MENU.values():
        flat.update(category)
    return flat


# ---------------------------------------------------------------------------
# Menu 도구
# ---------------------------------------------------------------------------

@function_tool
def get_menu() -> dict:
    """카테고리별 전체 메뉴와 가격을 반환한다."""
    return {
        category: {name: info["price"] for name, info in dishes.items()}
        for category, dishes in MENU.items()
    }


@function_tool
def get_dish_details(dish: str) -> dict:
    """특정 메뉴의 재료, 알레르겐, 채식/비건 여부를 반환한다."""
    dishes = _all_dishes()
    if dish not in dishes:
        return {"error": f"'{dish}' 메뉴를 찾을 수 없습니다.", "available": list(dishes)}
    return {"dish": dish, **dishes[dish]}


@function_tool
def list_dietary_options(diet: str) -> dict:
    """식이 조건에 맞는 메뉴를 반환한다. diet: 'vegetarian' | 'vegan' | 'gluten-free'."""
    diet = diet.lower()
    matches = []
    for name, info in _all_dishes().items():
        if diet in ("vegetarian", "채식") and info["vegetarian"]:
            matches.append(name)
        elif diet in ("vegan", "비건") and info["vegan"]:
            matches.append(name)
        elif diet in ("gluten-free", "글루텐프리", "글루텐 프리") and "글루텐" not in info["allergens"]:
            matches.append(name)
    return {"diet": diet, "options": matches}


# ---------------------------------------------------------------------------
# Order 도구
# ---------------------------------------------------------------------------

_ORDERS: dict[str, dict] = {}


@function_tool
def place_order(items: list[str]) -> dict:
    """주문 항목 목록을 받아 주문을 생성하고, 합계와 함께 확인 정보를 반환한다."""
    dishes = _all_dishes()
    confirmed, unknown, total = [], [], 0
    for item in items:
        if item in dishes:
            price = dishes[item]["price"]
            confirmed.append({"name": item, "price": price})
            total += price
        else:
            unknown.append(item)

    order_id = f"ORD-{1000 + len(_ORDERS) + 1}"
    record = {
        "order_id": order_id,
        "items": confirmed,
        "total": total,
        "status": "접수됨",
    }
    _ORDERS[order_id] = record
    return {**record, "unknown_items": unknown}


@function_tool
def get_order_status(order_id: str) -> dict:
    """주문 번호로 현재 주문 상태를 조회한다."""
    if order_id not in _ORDERS:
        return {"error": f"주문 '{order_id}' 을(를) 찾을 수 없습니다."}
    return _ORDERS[order_id]


# ---------------------------------------------------------------------------
# Reservation 도구
# ---------------------------------------------------------------------------

_RESERVATIONS: dict[str, dict] = {}


@function_tool
def check_availability(date: str, time: str, party_size: int) -> dict:
    """요청한 날짜/시간/인원에 예약 가능한지 확인한다 (mock: 8명 이하 가능)."""
    available = party_size <= 8
    return {
        "date": date,
        "time": time,
        "party_size": party_size,
        "available": available,
        "note": "" if available else "9명 이상은 전화 예약이 필요합니다.",
    }


@function_tool
def book_reservation(party_size: int, date: str, time: str, name: str) -> dict:
    """테이블 예약을 확정하고 예약 번호를 발급한다."""
    reservation_id = f"RES-{2000 + len(_RESERVATIONS) + 1}"
    record = {
        "reservation_id": reservation_id,
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time,
        "status": "예약 확정",
    }
    _RESERVATIONS[reservation_id] = record
    return record


# ---------------------------------------------------------------------------
# 에이전트 활동 로깅 hooks (sidebar 표시)
# ---------------------------------------------------------------------------

class AgentToolUsageLoggingHooks(AgentHooks):
    """에이전트 활성화 / 도구 호출 / handoff 를 sidebar 에 기록한다."""

    async def on_start(self, context: RunContextWrapper[CustomerContext], agent):
        with st.sidebar:
            st.write(f"▶️ **{agent.name}** 활성화")

    async def on_tool_start(self, context, agent, tool):
        with st.sidebar:
            st.write(f"🔧 {agent.name} → `{tool.name}` 호출")

    async def on_tool_end(self, context, agent, tool, result):
        with st.sidebar:
            st.write(f"✅ `{tool.name}` 완료")

    async def on_handoff(self, context, agent, source):
        with st.sidebar:
            st.write(f"🔀 {source.name} → {agent.name} handoff")
