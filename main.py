import math
import html
import streamlit as st
import requests
import re
import time


st.set_page_config(
    page_title="맛집 추천",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ======================================
# 💰 실제 가격대 표시
# ======================================


# ======================================
# Google Maps API 키
# ======================================

GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
KAKAO_REST_API_KEY = st.secrets.get("KAKAO_REST_API_KEY")



# ======================================
# 표시용 이모지
# ======================================

CATEGORY_EMOJIS = {
    "맛": "😋",
    "서비스": "🙂",
    "청결": "🧼",
    "가격/가성비": "💰",
    "웨이팅": "⏳",
    "분위기": "🌙",
    "전체 만족": "❤️"
}


# ======================================
# 음식 관련 단어
# ======================================

FOOD_RELATED_WORDS = [
    "음식",
    "메뉴",
    "맛",
    "먹",
    "고기",
    "치킨",
    "삼겹살",
    "목살",
    "갈비",
    "게장",
    "생선",
    "패티",
    "버거",
    "햄버거",
    "샌드위치",
    "딤섬",
    "샤오롱바오",
    "샤오마이",
    "만두",
    "반찬",
    "밑반찬",
    "밥",
    "정식",
    "냉면",
    "찌개",
    "국",
    "국물",
    "육수",
    "튀김",
    "볶음밥",
    "육즙",
    "소스",
    "재료",
    "요리",
    "식사",
    "파스타",
    "리조또",
    "삼계탕",
    "김치",
    "깍두기",
    "닭",
    "돼지고기",
    "소고기"
]


# ======================================
# 숙박 중심 표현
# ======================================

HOTEL_RELATED_WORDS = [
    "객실",
    "침구",
    "어메니티",
    "입욕제",
    "안마의자",
    "숙박",
    "호텔",
    "체크인",
    "체크아웃",
    "반캉스"
]


# ======================================
# 일반 분석 사전
# ======================================

REVIEW_RULES = {

    "맛": {

        "positive": {
            "맛있": 3,
            "맛잇": 3,
            "맛나": 3,
            "맛난": 3,
            "맛도리": 3,
            "개맛도리": 4,
            "존맛": 4,
            "존맛탱": 4,
            "대존맛": 4,

            "훌륭": 3,
            "끝내줘": 3,
            "끝내주": 3,
            "쵝오": 3,

            "신선": 2,
            "싱싱": 2,
            "질 좋은": 2,

            "부드럽": 2,
            "야들야들": 2,
            "바삭": 2,
            "겉바속촉": 3,
            "쫀득": 2,
            "쫄깃": 2,
            "담백": 2,
            "고소": 2,
            "구수": 2,

            "육즙": 2,
            "풍미": 2,
            "감칠맛": 2,

            "잘 어우러": 2,
            "조화가 좋": 2,
            "조화가 훌륭": 3,
            "완벽한 밸런스": 3,
            "완성도가 높": 3,

            "먹기 좋": 2,
            "먹을만": 1,
            "맛깔": 2,
            "진국": 2
        },

        "negative": {
            "맛없": 4,
            "맛이 없": 4,
            "맛이 별로": 4,
            "맛이 너무 별로": 5,
            "음식이 별로": 4,

            "냉동같": 2,
            "냉동 같": 2,

            "비리": 2,
            "비린": 2,
            "질기": 2,
            "잡내": 2,
            "냄새나": 2,
            "탄 맛": 2,

            "싱겁": 1,
            "짜다": 2,
            "짜요": 2,
            "짰": 2,
            "엄청 짜": 3,

            "느끼": 1,
            "너무 달": 1,
            "간이 안 맞": 3,

            "탄력없이": 2,
            "탄력 없이": 2,

            "식어 있": 1,
            "식어있": 1,

            "아쉬운 맛": 2
        }
    },


    "서비스": {

        "positive": {
            "직원분들이 친절": 4,
            "직원분이 친절": 4,
            "직원이 친절": 4,
            "친절": 3,

            "서비스 좋": 3,
            "응대가 좋": 3,
            "응대 좋": 3,

            "세심": 2,
            "잘 챙겨": 2,
            "챙겨주": 2,
            "센스 있": 2,

            "구워주": 1
        },

        "negative": {
            "서비스 최악": 6,
            "최악의 서비스": 6,

            "불친절": 5,
            "무례": 5,

            "친절도는 개선": 5,
            "친절도 개선": 5,
            "친절 개선": 5,

            "서비스 별로": 4,
            "서비스가 별로": 4,

            "응대 별로": 4,
            "응대가 별로": 4,
            "응대가 안 좋": 4,

            "대답도 안": 4,
            "제대로 대답도 안": 5,

            "주문 누락": 5,
            "누락되었다": 5,
            "누락됐": 5,

            "취소도 못": 4,

            "주문 실수": 3,

            "음식이 안 나": 4,
            "안나와": 4,
            "안 나와": 4
        }
    },


    "청결": {

        "positive": {
            "매장이 깔끔": 4,
            "매장 깔끔": 4,
            "매장이 깨끗": 4,
            "매장 깨끗": 4,

            "화장실이 깔끔": 4,
            "화장실도 깔끔": 4,

            "청소 상태 좋": 4,
            "청결": 3,
            "위생적": 3,

            "정리가 잘": 2,
            "정돈": 2
        },

        "negative": {
            "매장이 더럽": 5,
            "화장실이 더럽": 5,
            "더럽": 4,

            "비위생": 5,
            "지저분": 4,

            "청결하지 않": 4,
            "위생이 별로": 4,
            "위생 별로": 4,

            "벌레": 6,
            "곰팡이": 6
        }
    },


    "가격/가성비": {

        "positive": {
            "가성비 좋": 4,
            "가성비 좋은": 4,
            "가성비 최고": 5,
            "가성비 갑": 5,
            "가성비 있": 3,

            "합리적인 가격": 4,
            "합리적": 3,

            "가격 대비 좋": 4,
            "가격이면 괜찮": 3,

            "저렴": 3,
            "돈이 아깝지 않": 4,
            "값어치": 3
        },

        "negative": {
            "가격이 부담": 4,
            "가격대가 부담": 4,

            "가격이 비싸": 3,
            "가격은 비싸": 3,
            "가격이 꽤 비쌌": 4,
            "꽤 비쌌": 4,
            "꽤 비싸": 4,

            "가격이 좀 센": 3,
            "가격이 센 편": 3,
            "가격이 높": 3,

            "가격에 비해": 3,
            "가격 대비 별로": 5,
            "가격에 비해 맛이": 4,

            "가성비 별로": 5,
            "가성비 안 좋": 5,

            "돈 아깝": 5,

            "모든게 유료": 3,
            "모든 게 유료": 3
        }
    },


    "분위기": {

        "positive": {
            "분위기 좋": 4,
            "분위기가 좋": 4,
            "분위기 최고": 5,

            "아늑": 2,
            "감성": 2,
            "힙": 2,

            "조용": 2,
            "편안": 2,
            "개방감이 좋": 3,

            "데이트": 1,

            "인테리어 좋": 3,
            "인테리어 예쁘": 3,

            "낭만": 2
        },

        "negative": {
            "분위기 별로": 4,
            "분위기가 별로": 4,

            "시끄러": 3,
            "시끄럽": 3,
            "어수선": 2,

            "너무 어두": 2,
            "혼잡": 2,
            "복잡": 2
        }
    },


    # 웨이팅은 키워드 사전 대신 analyze_waiting()에서
    # 시간/대기 문맥을 별도로 분석한다.
    "웨이팅": {
        "positive": {},
        "negative": {}
    },


    "전체 만족": {

        "positive": {
            "만족": 3,
            "만족스럽": 4,

            "재방문": 5,
            "또 방문": 5,
            "다시 방문": 5,
            "다시 가고 싶": 5,
            "또 가고 싶": 5,

            "자주 옵": 4,
            "자주 가": 4,
            "종종 찾": 4,

            "추천하고 싶": 5,
            "추천합니다": 4,
            "강력 추천": 5,
            "추천 안할 수": 5,

            "잘 먹었습니다": 3,
            "잘 먹고": 3,

            "흠 잡을 곳 없": 4,

            "마음에 든": 2
        },

        "negative": {
            "최악": 6,
            "실망": 5,

            "다시는 안": 6,
            "다시 안 갈": 6,
            "재방문 안": 6,

            "다른 지점에 가세요": 6,
            "다른 가게": 3,

            "추천 못": 5,
            "추천하지 않": 5,

            "후회": 5,

            "별 한 개도 주고 싶지": 6,
            "별 1개도 주고 싶지": 6
        }
    }
}


# ======================================
# 긴 문맥을 우선 처리하는 규칙
# ======================================

CONTEXT_RULES = {

    "맛": {

        "positive": {
            "느끼하지 않": 4,
            "느끼하지않": 4,
            "느끼하지는 않": 4,
            "느끼함 없이": 4,
            "느끼함은 잡고": 4,
            "느끼함을 잡": 4,
            "비리지 않": 4,
            "비리지않": 4,
            "비리지 않는": 4,
            "비린 맛이 없": 4,
            "비린 맛은 전혀 없": 4,
            "비린 맛이 전혀 없": 4,
            "잡내가 없": 4,
            "잡내 없이": 4,
            "잡내하나없이": 4,

            "맛없는 게 없": 5,
            "맛없는게 없": 5,
            "맛 없는 게 없": 5,

            "맛 없음 반칙": 5,
            "맛없으면 반칙": 5,

            "짜지 않": 3,
            "짜지않": 3,

            "달지 않": 3,
            "달지않": 3,

            "싱겁지 않": 3,
            "싱겁지않": 3,

            "나쁘지 않": 2,
            "나쁘지않": 2,

            "맛은 나쁘지 않": 3,
            "맛은 나쁘지는 않": 3,

            "잡내하나없이": 4,
            "잡내 하나 없이": 4,

            "물리지 않는 맛": 3,

            "실패없는 맛": 4,
            "실패 없는 맛": 4
        },

        "negative": {
            "안 맛있": 5,
            "맛있지 않": 5,
            "맛있지는 않": 4,
            "맛있는 편은 아니": 4,

            "맛이 너무 별로": 6,

            "호불호 있을": 1,
            "호불호는 갈릴": 1
        }
    },


    "서비스": {

        "positive": {},

        "negative": {
            "친절하지 않": 5,
            "친절하지않": 5,
            "친절하지는 않": 5,

            "친절도는 개선이 필요": 6,
            "친절도 개선이 필요": 6,

            "서비스는 그냥 그렇": 2
        }
    },


    "청결": {

        "positive": {},

        "negative": {
            "깨끗하지 않": 5,
            "깨끗하지않": 5,

            "깔끔하지 않": 4,
            "깔끔하지않": 4
        }
    },


    "가격/가성비": {

        "positive": {
            "가격은 있지만 특별함으로 커버": 2,
            "가격대는 있으나 특별함으로 커버": 2
        },

        "negative": {
            "가격이 좀 센 편": 4,
            "가격이 센 편": 4,
            "가격이 많이 올랐": 3,
            "가격대가 부담": 4,
            "5만원 넘는": 2
        }
    }
}


# ======================================
# 텍스트 정리
# ======================================

def render_review_text(review_text):
    """
    Google 리뷰 원문을 Markdown으로 해석하지 않고 일반 본문으로 표시한다.

    리뷰가 '#', '##', '*', '_' 등으로 시작해도
    Streamlit 제목/강조 문법으로 변환되지 않도록 HTML escape 처리한다.
    """
    safe_text = html.escape(
        str(review_text or "")
    )

    st.markdown(
        (
            "<div style='"
            "font-size: 1rem;"
            "font-weight: 400;"
            "line-height: 1.65;"
            "white-space: pre-wrap;"
            "overflow-wrap: anywhere;"
            "margin: 0.25rem 0 0.65rem 0;"
            "'>"
            f"{safe_text}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ======================================
# 문장 나누기
# ======================================

def split_sentences(text):

    text = normalize_text(text)

    sentences = re.split(
        r"[.!?\n]+",
        text
    )

    cleaned = []


    for sentence in sentences:

        sentence = sentence.strip()

        if sentence:
            cleaned.append(
                sentence
            )


    return cleaned


# ======================================
# 음식 관련성 확인
# ======================================

def is_food_related(text):

    text = normalize_text(text)

    food_count = 0
    hotel_count = 0


    for word in FOOD_RELATED_WORDS:

        if word in text:
            food_count += 1


    for word in HOTEL_RELATED_WORDS:

        if word in text:
            hotel_count += 1


    if food_count > 0:
        return True


    if hotel_count > 0:
        return False


    return False


# ======================================
# 다른 음식점에 대한 문장인지 확인
#
# "다른 지점에 가세요"
# "다른 맛있고 서비스 좋은 가게..."
# 같은 문장을 현재 식당의 긍정으로
# 계산하지 않기 위한 간단 필터
# ======================================

def is_other_place_sentence(sentence):

    patterns = [
        "다른 지점",
        "다른 교촌",
        "다른 가게",
        "다른 식당",
        "다른 맛집",
        "다른 곳에 가",
        "다른 곳을 가",
        "다른 곳이 더",
        "다른 식당이 더"
    ]


    for pattern in patterns:

        if pattern in sentence:
            return True


    return False


# ======================================
# 청결 문맥 확인
#
# "깔끔한 맛"을 청결로 잘못 잡는 것을 방지
# ======================================

def is_cleanliness_sentence(sentence):

    cleanliness_context = [
        "매장",
        "가게",
        "식당",
        "내부",
        "인테리어",
        "화장실",
        "테이블",
        "좌석",
        "청소",
        "위생",
        "정리",
        "정돈"
    ]


    for word in cleanliness_context:

        if word in sentence:
            return True


    return False


# ======================================
# 웨이팅 자동 분석
# ======================================

def analyze_waiting(sentences):
    """
    웨이팅 문맥 분석.

    핵심 원칙:
    1) "웨이팅 없음"이라는 단어만으로 긍정 처리하지 않는다.
    2) "웨이팅 없이 바로 입장"처럼 실제 입장 경험이 좋았을 때만 긍정한다.
    3) "웨이팅 없는 다른 곳", "굳이 기다릴 필요 없다"처럼
       다른 가게와 비교하거나 기다릴 가치가 없다는 표현은 부정으로 본다.
    4) 숫자 시간은 웨이팅 문맥에 가까이 붙어 있을 때만 대기시간으로 본다.
       음식 조리/서빙 시간은 웨이팅 시간으로 오해하지 않는다.
    """

    positive_score = 0
    negative_score = 0
    positive_matches = []
    negative_matches = []

    # 현재 식당의 웨이팅을 부정적으로 평가하는 강한 문맥.
    negative_context_patterns = [
        (
            r"웨이팅\s*(?:이|은|도)?\s*없는?\s*다른\s*(?:곳|가게|데)",
            "웨이팅 없는 다른 곳과 비교",
        ),
        (
            r"대기\s*(?:가|는|도)?\s*없는?\s*다른\s*(?:곳|가게|데)",
            "대기 없는 다른 곳과 비교",
        ),
        (
            r"굳이[^.!?\n]{0,30}웨이팅[^.!?\n]{0,20}(?:안|하지)",
            "굳이 웨이팅할 필요가 없다는 표현",
        ),
        (
            r"굳이[^.!?\n]{0,30}대기[^.!?\n]{0,20}(?:안|하지)",
            "굳이 대기할 필요가 없다는 표현",
        ),
        (
            r"굳이[^.!?\n]{0,30}기다[^.!?\n]{0,20}(?:필요|이유|가치)",
            "굳이 기다릴 이유가 없다는 표현",
        ),
        (
            r"웨이팅[^.!?\n]{0,20}(?:할|해서|해가며)[^.!?\n]{0,20}(?:가치|정도는\s*아니|필요\s*없)",
            "웨이팅할 가치가 낮다는 표현",
        ),
        (
            r"대기[^.!?\n]{0,20}(?:할|해서|해가며)[^.!?\n]{0,20}(?:가치|정도는\s*아니|필요\s*없)",
            "대기할 가치가 낮다는 표현",
        ),
        (
            r"기다[^.!?\n]{0,20}(?:가치\s*없|필요가?\s*없|정도는\s*아니)",
            "기다릴 가치가 낮다는 표현",
        ),
        (
            r"줄\s*(?:서|서서|까지\s*서)[^.!?\n]{0,20}(?:먹을|갈)[^.!?\n]{0,15}(?:정도는\s*아니|가치\s*없)",
            "줄 서서 먹을 가치가 낮다는 표현",
        ),
        (
            r"웨이팅[^.!?\n]{0,25}더\s*좋은\s*(?:곳|가게|데)",
            "웨이팅보다 더 좋은 다른 곳이 있다는 표현",
        ),
        (
            r"대기[^.!?\n]{0,25}더\s*좋은\s*(?:곳|가게|데)",
            "대기보다 더 좋은 다른 곳이 있다는 표현",
        ),
    ]

    # 실제로 기다리지 않고 들어갔다는 경험이 확인되는 경우만 긍정.
    positive_patterns = [
        "바로 들어",
        "바로 입장",
        "웨이팅 없이 바로",
        "대기 없이 바로",
        "기다림 없이 바로",
        "웨이팅 없이 들어",
        "대기 없이 들어",
        "기다림 없이 들어",
        "웨이팅이 없었",
        "웨이팅은 없었",
        "대기가 없었",
        "대기는 없었",
        "기다리지 않고",
        "기다리지 않아서",
        "기다릴 필요 없이",
        "줄이 금방 줄",
        "순식간에 줄이 줄",
        "회전율은 빠",
        "회전율이 빠",
    ]

    negative_patterns = [
        "웨이팅 길",
        "대기 길",
        "오래 기다",
        "한참 기다",
        "웨이팅 대박",
        "극악의 웨이팅",
        "웨이팅이 불가",
        "웨이팅 해야",
        "웨이팅해야",
        "대기해야",
        "대기 해야",
        "기다렸",
        "줄을 서서",
        "줄을 서야",
        "줄서서",
        "줄서야",
        "줄이 길",
        "대기가 길",
        "대기줄이 길",
        "대기 줄이 길",
        "웨이팅이 길",
        "웨이팅을 오래",
        "기다려야",
        "기다려야 했",
        "기다리다",
        "기다리는 시간",
        "웨이팅이 있었",
        "웨이팅은 있었",
        "대기가 있었",
        "대기는 있었",
    ]

    # 숫자 주변에 이런 말이 있으면 조리/서빙 시간일 가능성이 높다.
    preparation_time_terms = [
        "요리",
        "음식",
        "메뉴",
        "조리",
        "주방",
        "서빙",
        "나오",
        "나오는",
        "나오기",
        "간격",
    ]

    short_wait_positive_terms = [
        "도 안",
        "안 걸",
        "이내",
        "미만",
        "금방",
        "잠깐",
        "바로",
    ]

    for sentence in sentences:
        waiting_word = (
            "웨이팅" in sentence
            or "대기" in sentence
            or "기다" in sentence
            or "줄" in sentence
        )

        if not waiting_word:
            continue

        # --------------------------------------
        # 1. 강한 부정 문맥을 먼저 처리한다.
        # --------------------------------------
        strong_negative = False

        matched_context_labels = []

        for pattern, label in negative_context_patterns:
            if re.search(pattern, sentence):
                matched_context_labels.append(label)

        if matched_context_labels:
            # 같은 문장이 여러 규칙에 동시에 걸려도
            # 문장 하나를 여러 번 감점하지 않는다.
            negative_score += 5
            negative_matches.append(
                matched_context_labels[0]
            )
            strong_negative = True

        # 강한 부정 문맥이 있는 문장에서는
        # "웨이팅 없" 같은 일부 문자열 때문에 긍정이 섞이지 않게 한다.
        if not strong_negative:
            for pattern in positive_patterns:
                if pattern in sentence:
                    positive_score += 3
                    positive_matches.append(pattern)

        # --------------------------------------
        # 2. 일반적인 부정 대기 표현
        # --------------------------------------
        for pattern in negative_patterns:
            if pattern in sentence:
                negative_score += 3
                negative_matches.append(pattern)

        # --------------------------------------
        # 3. 시간 자동 인식
        # --------------------------------------
        # 숫자 바로 주변 문맥만 보고 웨이팅 시간인지 판단한다.
        # 조리/서빙 문맥이 가까우면 대기시간에서 제외한다.
        time_patterns = [
            (r"(\d+(?:\.\d+)?)\s*시간", "hour"),
            (r"(\d+)\s*분", "minute"),
        ]

        for time_pattern, unit in time_patterns:
            for match in re.finditer(time_pattern, sentence):
                span_start, span_end = match.span()
                nearby = sentence[
                    max(0, span_start - 24):
                    min(len(sentence), span_end + 24)
                ]

                nearby_has_wait = any(
                    token in nearby
                    for token in ["웨이팅", "대기", "기다", "줄"]
                )

                if not nearby_has_wait:
                    continue

                nearby_has_preparation = any(
                    token in nearby
                    for token in preparation_time_terms
                )

                # "주문하고 30분 기다렸다"처럼 실제 기다림 표현이
                # 숫자 주변에 있으면 조리 단어가 있어도 웨이팅으로 본다.
                explicit_wait_action = (
                    "기다" in nearby
                    or re.search(
                        r"(?:웨이팅|대기|줄)\s*(?:약\s*)?\d",
                        nearby
                    )
                    is not None
                    or re.search(
                        r"\d+(?:\.\d+)?\s*(?:분|시간)[^.!?\n]{0,10}(?:웨이팅|대기|기다|줄)",
                        nearby
                    )
                    is not None
                )

                if nearby_has_preparation and not explicit_wait_action:
                    continue

                # "10분도 안 기다림", "5분 이내 입장" 같은 짧은 대기는
                # 부정이 아니라 긍정 신호로 처리한다.
                if any(
                    term in nearby
                    for term in short_wait_positive_terms
                ):
                    positive_score += 2
                    positive_matches.append(
                        f"짧은 대기: {match.group(0)}"
                    )
                    continue

                if unit == "hour":
                    hours = float(match.group(1))

                    if hours >= 1:
                        negative_score += 5
                        negative_matches.append(
                            f"{match.group(1)}시간 대기"
                        )
                    elif hours >= 0.5:
                        negative_score += 3
                        negative_matches.append(
                            f"{match.group(1)}시간 대기"
                        )

                else:
                    minutes = int(match.group(1))

                    if minutes >= 60:
                        negative_score += 5
                    elif minutes >= 30:
                        negative_score += 4
                    elif minutes >= 15:
                        negative_score += 2
                    elif minutes >= 10:
                        negative_score += 1

                    if minutes >= 10:
                        negative_matches.append(
                            f"{minutes}분 대기"
                        )

    return {
        "positive_score": positive_score,
        "negative_score": negative_score,
        "positive_matches": list(set(positive_matches)),
        "negative_matches": list(set(negative_matches)),
    }


# ======================================
# 점수 → 긍정/부정 판정
# ======================================

def decide_result(
    positive_score,
    negative_score
):

    if (
        positive_score == 0
        and negative_score == 0
    ):

        return "언급 없음"


    if (
        positive_score > 0
        and negative_score == 0
    ):

        return "긍정"


    if (
        negative_score > 0
        and positive_score == 0
    ):

        return "부정"


    if positive_score >= (
        negative_score * 2
    ):

        return "긍정"


    if negative_score >= (
        positive_score * 2
    ):

        return "부정"


    return "혼합"


# ======================================
# 리뷰 하나 분석
# ======================================

def analyze_review(
    review_text,
    review_rating=None
):

    text = normalize_text(
        review_text
    )

    sentences = split_sentences(
        text
    )

    food_related = is_food_related(
        text
    )

    analysis = {}


    # ======================================
    # 자연스러운 부정 표현
    # ======================================

    natural_negative_phrases = {

        "맛": [
            "맛이 별로",
            "맛도 별로",
            "맛은 별로",
            "음식이 별로",
            "음식도 별로",
            "맛이 왜",
            "맛도 왜",
            "평타도 못",
            "평타도 못하",
            "맛을 못",
            "맛도 못",
            "맛있게 못",
            "제대로 못",
            "맛이 아쉽",
            "맛은 아쉽",
            "맛이 부족",
            "맛이 떨어",
            "맛이 기대 이하",
            "맛은 기대 이하",
            "맛볼 가치가 없",
            "먹을 가치가 없",
            "먹을만하지 않",
            "먹을 만하지 않",
            "추천하기 어렵",
            "추천하기 힘들"
        ],

        "서비스": [
            "서비스가 별로",
            "서비스는 별로",
            "응대가 별로",
            "직원이 별로",
            "직원도 별로",
            "친절하지 않",
            "불친절",
            "무례",
            "무시",
            "응대가 아쉽",
            "서비스가 아쉽",
            "서비스가 부족",
            "직원 태도가 별로",
            "직원태도가 별로",
            "직원 태도도 별로"
        ],

        "가격/가성비": [
            "가격이 별로",
            "가격은 별로",
            "가격이 비싸",
            "가격은 비싸",
            "너무 비싸",
            "비싼 편",
            "가격 대비 별로",
            "가성비가 별로",
            "가성비는 별로",
            "돈이 아깝",
            "돈 아깝",
            "가격이 아쉽"
        ],

        "청결": [
            "더럽",
            "지저분",
            "청결하지 않",
            "위생이 별로",
            "위생이 좋지 않",
            "깨끗하지 않",
            "깔끔하지 않"
        ],

        "분위기": [
            "분위기가 별로",
            "분위기는 별로",
            "시끄럽",
            "너무 시끄럽",
            "정신없",
            "분위기가 아쉽",
            "분위기는 아쉽"
        ],

        "전체 만족": [
            "별로였다",
            "별로였",
            "별로예요",
            "별로에요",
            "실망",
            "기대 이하",
            "기대이하",
            "추천하기 어렵",
            "추천하기 힘들",
            "다시는 안",
            "다시 갈 생각 없",
            "돈이 아깝",
            "아쉬운 점",
            "아쉬웠"
        ]
    }


    # ======================================
    # 자연스러운 긍정 표현
    # ======================================

    natural_positive_phrases = {

        "맛": [
            "맛이 좋",
            "맛은 좋",
            "맛도 좋",
            "맛이 괜찮",
            "맛은 괜찮",
            "맛도 괜찮",
            "맛이 나쁘지 않",
            "맛은 나쁘지 않",
            "맛도 나쁘지 않",
            "먹을만",
            "먹을 만",
            "맛볼 만",
            "맛볼만",
            "추천할 만",
            "추천할만"
        ],

        "서비스": [
            "친절하",
            "친절했",
            "친절해서",
            "서비스가 좋",
            "서비스는 좋",
            "응대가 좋",
            "응대는 좋"
        ],

        "가격/가성비": [
            "가격이 괜찮",
            "가격은 괜찮",
            "가격도 괜찮",
            "가성비가 좋",
            "가성비는 좋",
            "가성비도 좋",
            "가격 대비 괜찮",
            "가격 대비 좋"
        ],

        "청결": [
            "깨끗하",
            "깔끔하",
            "청결하",
            "위생적"
        ],

        "분위기": [
            "분위기가 좋",
            "분위기는 좋",
            "분위기도 좋",
            "분위기가 괜찮",
            "분위기는 괜찮"
        ],

        "전체 만족": [
            "만족",
            "추천",
            "재방문",
            "다시 가",
            "또 가",
            "좋은 곳",
            "좋은집",
            "좋은 집"
        ]
    }


    # ======================================
    # 부정 표현이 실제 부정인지 확인
    # ======================================

    def is_negated_expression(
        sentence,
        expression
    ):

        index = sentence.find(
            expression
        )


        if index == -1:

            return False


        after_index = (
            index
            + len(expression)
        )


        after_text = sentence[
            after_index:
            after_index + 25
        ]


        # ----------------------------------
        # 이중 부정 / 긍정으로 뒤집히는 경우
        # ----------------------------------

        positive_turn_phrases = [

            "을 수가 없",
            "을수가 없",
            "을 수 없",
            "을수 없",

            "ㄹ 수가 없",
            "ㄹ수가 없",
            "ㄹ 수 없",
            "ㄹ수 없",

            "진 않",
            "지는 않",
            "지는않",
            "진않",

            "않다",
            "않아요",
            "않습니다",

            "아니",
            "없진",
            "없지는"
        ]


        for phrase in (
            positive_turn_phrases
        ):

            if phrase in after_text:

                return True


        return False


    # ======================================
    # 문장 전체가 중립화되는 경우
    # ======================================

    def is_neutral_sentence(
        sentence
    ):

        neutral_patterns = [

            "친절하지는 않으나 불친절한 것도 아니다",
            "친절하지는 않지만 불친절한 것도 아니다",
            "불친절한 것도 아니다",
            "불친절한 것은 아니다",

            "친절하지않으나 불친절한 것도 아니다",
            "친절하지않지만 불친절한 것도 아니다",

            "맛이 없진 않",
            "맛이없진 않",

            "나쁘지 않",
            "나쁘지않"
        ]


        for pattern in (
            neutral_patterns
        ):

            if pattern in sentence:

                return True


        return False


    # ======================================
    # 정보성 문장 확인
    # ======================================

    def is_information_only(
        sentence
    ):

        information_phrases = [

            "폐업",
            "폐업함",
            "지금은 폐업",
            "폐업했습니다",
            "폐업했",
            "영업 종료",
            "영업종료"
        ]


        for phrase in (
            information_phrases
        ):

            if phrase in sentence:

                return True


        return False


    # ======================================
    # 일반 카테고리 분석
    # ======================================

    for category, rules in REVIEW_RULES.items():

        positive_score = 0
        negative_score = 0

        positive_matches = []
        negative_matches = []


        # ======================================
        # 웨이팅은 기존 숫자 분석 사용
        # ======================================

        if category == "웨이팅":

            waiting_result = analyze_waiting(
                sentences
            )

            positive_score = (
                waiting_result[
                    "positive_score"
                ]
            )

            negative_score = (
                waiting_result[
                    "negative_score"
                ]
            )

            positive_matches = (
                waiting_result[
                    "positive_matches"
                ]
            )

            negative_matches = (
                waiting_result[
                    "negative_matches"
                ]
            )


        else:

            for sentence in sentences:

                working_sentence = sentence


                # ==================================
                # 정보성 리뷰는 감정 분석에서 제외
                # ==================================

                if is_information_only(
                    sentence
                ):

                    continue


                # ==================================
                # 이중 부정 / 중립 문장
                # ==================================

                neutral_sentence = (
                    is_neutral_sentence(
                        sentence
                    )
                )


                # ==================================
                # 다른 식당을 칭찬하는 문장 제외
                # ==================================

                other_place = (
                    is_other_place_sentence(
                        sentence
                    )
                )


                # ==================================
                # 기존 긴 문맥 규칙
                # ==================================

                if category in CONTEXT_RULES:

                    context_rules = (
                        CONTEXT_RULES[
                            category
                        ]
                    )


                    # ------------------------------
                    # 기존 긍정 문맥
                    # ------------------------------

                    for expression, weight in (
                        context_rules[
                            "positive"
                        ].items()
                    ):

                        if expression in working_sentence:

                            if (
                                not other_place
                                and not neutral_sentence
                                and not is_negated_expression(
                                    working_sentence,
                                    expression
                                )
                            ):

                                count = (
                                    working_sentence.count(
                                        expression
                                    )
                                )

                                positive_score += (
                                    count * weight
                                )

                                positive_matches.append(
                                    expression
                                )


                            working_sentence = (
                                working_sentence.replace(
                                    expression,
                                    " "
                                )
                            )


                    # ------------------------------
                    # 기존 부정 문맥
                    # ------------------------------

                    for expression, weight in (
                        context_rules[
                            "negative"
                        ].items()
                    ):

                        if expression in working_sentence:

                            if (
                                not neutral_sentence
                                and not is_negated_expression(
                                    working_sentence,
                                    expression
                                )
                            ):

                                count = (
                                    working_sentence.count(
                                        expression
                                    )
                                )

                                negative_score += (
                                    count * weight
                                )

                                negative_matches.append(
                                    expression
                                )


                            working_sentence = (
                                working_sentence.replace(
                                    expression,
                                    " "
                                )
                            )


                # ==================================
                # 청결은 청결 관련 문장만
                # ==================================

                if (
                    category == "청결"
                    and not is_cleanliness_sentence(
                        sentence
                    )
                ):

                    continue


                # ==================================
                # 새 자연어 긍정 표현
                # ==================================

                for expression in (
                    natural_positive_phrases.get(
                        category,
                        []
                    )
                ):

                    if expression in working_sentence:

                        if other_place:

                            continue


                        if neutral_sentence:

                            continue


                        if is_negated_expression(
                            working_sentence,
                            expression
                        ):

                            continue


                        positive_score += 2

                        positive_matches.append(
                            expression
                        )


                # ==================================
                # 기존 긍정 표현
                # ==================================

                for expression, weight in (
                    rules[
                        "positive"
                    ].items()
                ):

                    if expression in working_sentence:

                        if other_place:

                            continue


                        if neutral_sentence:

                            continue


                        if is_negated_expression(
                            working_sentence,
                            expression
                        ):

                            continue


                        count = (
                            working_sentence.count(
                                expression
                            )
                        )

                        positive_score += (
                            count * weight
                        )

                        positive_matches.append(
                            expression
                        )


                # ==================================
                # 새 자연어 부정 표현
                # ==================================

                for expression in (
                    natural_negative_phrases.get(
                        category,
                        []
                    )
                ):

                    if expression in working_sentence:

                        if neutral_sentence:

                            continue


                        if is_negated_expression(
                            working_sentence,
                            expression
                        ):

                            continue


                        negative_score += 3

                        negative_matches.append(
                            expression
                        )


                # ==================================
                # 기존 부정 표현
                # ==================================

                for expression, weight in (
                    rules[
                        "negative"
                    ].items()
                ):

                    if expression in working_sentence:

                        if neutral_sentence:

                            continue


                        if is_negated_expression(
                            working_sentence,
                            expression
                        ):

                            continue


                        count = (
                            working_sentence.count(
                                expression
                            )
                        )

                        negative_score += (
                            count * weight
                        )

                        negative_matches.append(
                            expression
                        )


        # ======================================
        # 맛은 음식 관련 리뷰에서만 사용
        # ======================================

        if (
            category == "맛"
            and not food_related
        ):

            positive_score = 0
            negative_score = 0

            positive_matches = []
            negative_matches = []


        # ======================================
        # 리뷰 별점은 텍스트 감정 점수에 다시 넣지 않는다.
        # Google 전체 평점이 최종 추천 점수에서 별도로 반영되므로
        # 여기서는 리뷰 문장 자체의 내용만 분석한다.
        # ======================================

        # ======================================
        # 최종 감정 결정
        # ======================================

        result = decide_result(
            positive_score,
            negative_score
        )


        analysis[category] = {

            "result":
                result,

            "positive_score":
                positive_score,

            "negative_score":
                negative_score,

            "positive_matches":
                list(
                    set(
                        positive_matches
                    )
                ),

            "negative_matches":
                list(
                    set(
                        negative_matches
                    )
                )
        }


    # ======================================
    # 음식 관련 여부
    # ======================================

    analysis[
        "음식 관련"
    ] = food_related


    return analysis

# ======================================
# 여러 리뷰 종합
# ======================================

def summarize_reviews(reviews):

    summary = {}


    for category in REVIEW_RULES.keys():

        summary[category] = {

            "positive_score": 0,

            "negative_score": 0,

            "positive_matches": [],

            "negative_matches": []
        }


    food_related_review_count = 0


    for review in reviews:

        review_text = (
            review.get(
                "text",
                {}
            ).get(
                "text",
                ""
            )
        )


        review_rating = review.get(
            "rating"
        )


        if not review_text:
            continue


        analysis = analyze_review(
            review_text,
            review_rating
        )


        if analysis[
            "음식 관련"
        ]:

            food_related_review_count += 1


        for category in REVIEW_RULES.keys():

            data = analysis[
                category
            ]


            summary[
                category
            ][
                "positive_score"
            ] += data[
                "positive_score"
            ]


            summary[
                category
            ][
                "negative_score"
            ] += data[
                "negative_score"
            ]


            summary[
                category
            ][
                "positive_matches"
            ].extend(
                data[
                    "positive_matches"
                ]
            )


            summary[
                category
            ][
                "negative_matches"
            ].extend(
                data[
                    "negative_matches"
                ]
            )


    # ======================================
    # 종합 결과
    # ======================================

    for category, data in summary.items():

        data["result"] = decide_result(
            data[
                "positive_score"
            ],
            data[
                "negative_score"
            ]
        )


        data[
            "positive_matches"
        ] = list(
            set(
                data[
                    "positive_matches"
                ]
            )
        )


        data[
            "negative_matches"
        ] = list(
            set(
                data[
                    "negative_matches"
                ]
            )
        )


    return (
        summary,
        food_related_review_count
    )


# ======================================
# V53: 리뷰 종합 분석 UI
# ======================================

REVIEW_SUMMARY_ORDER = [
    "맛",
    "가격/가성비",
    "서비스",
    "분위기",
    "웨이팅",
    "청결",
    "전체 만족",
]


REVIEW_RESULT_ICONS = {
    "긍정": "🟢",
    "혼합": "🟡",
    "부정": "🔴",
    "언급 없음": "⚪",
}


# Google Places가 제공하는 리뷰 원문 표본이 작기 때문에
# 몇 개의 강한 표현만으로 0/100에 가까워지는 것을 막는 중립 prior.
# 화면과 최종 추천점수 모두 동일한 보정 점수를 사용한다.
REVIEW_SENTIMENT_PRIOR = 20.0


def get_review_sentiment_score(data):
    """
    표시용 리뷰 감정 점수(0~100).

    50점이 중립이다.

    단순 긍정/부정 비율을 쓰지 않고,
    근거가 적을 때는 50점 쪽으로 강하게 보정한다.

    공식:
        50 + 50 * (긍정 - 부정)
                   / (긍정 + 부정 + PRIOR)

    예:
        긍정 5 / 부정 0  -> 60점
        긍정 10 / 부정 0 -> 약 66.7점
        긍정 20 / 부정 0 -> 75점
        긍정 5 / 부정 5  -> 50점
        긍정 0 / 부정 5  -> 40점

    즉 긍정 표현 하나만 잡혔다고 바로 100점이 되지 않는다.
    """
    positive = float(
        data.get(
            "positive_score",
            0
        ) or 0
    )

    negative = float(
        data.get(
            "negative_score",
            0
        ) or 0
    )

    signal_total = (
        positive
        + negative
    )

    if signal_total <= 0:
        return None

    score = (
        50.0
        + 50.0
        * (
            positive
            - negative
        )
        / (
            signal_total
            + REVIEW_SENTIMENT_PRIOR
        )
    )

    return round(
        max(
            0.0,
            min(
                100.0,
                score
            )
        ),
        1
    )


def get_review_sentiment_label(score):
    """
    0~100 리뷰 감정 점수를 사람이 읽기 쉬운 단계로 변환한다.
    """
    if score is None:
        return (
            "⚪",
            "정보 없음"
        )

    if score >= 80:
        return (
            "🟢",
            "매우 긍정"
        )

    if score >= 65:
        return (
            "🟢",
            "긍정"
        )

    if score >= 55:
        return (
            "🟡",
            "약간 긍정"
        )

    if score > 45:
        return (
            "⚪",
            "중립"
        )

    if score > 35:
        return (
            "🟡",
            "약간 부정"
        )

    if score > 20:
        return (
            "🔴",
            "부정"
        )

    return (
        "🔴",
        "매우 부정"
    )


def get_review_evidence_label(data):
    """
    감지된 긍정/부정 신호의 총량을 표시한다.
    점수가 같은 식당이라도 근거량 차이를 사용자가 볼 수 있게 한다.
    """
    positive = float(
        data.get(
            "positive_score",
            0
        ) or 0
    )

    negative = float(
        data.get(
            "negative_score",
            0
        ) or 0
    )

    signal_total = (
        positive
        + negative
    )

    if signal_total <= 0:
        return "없음"

    if signal_total < 8:
        return "적음"

    if signal_total < 20:
        return "보통"

    if signal_total < 40:
        return "많음"

    return "매우 많음"




def render_review_summary_dashboard(
    review_summary
):
    """
    리뷰 종합 분석을 점수형 카드 대시보드로 표시한다.

    50점 = 중립.
    신호가 적으면 점수가 50 근처에 머물고,
    근거가 누적될수록 긍정/부정 방향으로 더 크게 움직인다.
    """
    if not review_summary:
        st.info(
            "분석할 리뷰 요약 데이터가 없습니다."
        )
        return

    ordered_categories = [
        category
        for category in REVIEW_SUMMARY_ORDER
        if category in review_summary
    ]

    ordered_categories.extend(
        category
        for category in review_summary.keys()
        if category not in ordered_categories
    )

    positive_categories = []
    neutral_categories = []
    negative_categories = []

    category_display_data = {}

    for category in ordered_categories:
        data = review_summary[
            category
        ]

        score = get_review_sentiment_score(
            data
        )

        icon, label = get_review_sentiment_label(
            score
        )

        evidence_label = get_review_evidence_label(
            data
        )

        category_display_data[
            category
        ] = {
            "score": score,
            "icon": icon,
            "label": label,
            "evidence_label": evidence_label,
        }

        if score is None:
            neutral_categories.append(
                category
            )

        elif score >= 55:
            positive_categories.append(
                category
            )

        elif score <= 45:
            negative_categories.append(
                category
            )

        else:
            neutral_categories.append(
                category
            )

    if positive_categories:
        st.markdown(
            "🟢 **긍정 쪽** · "
            + " · ".join(
                positive_categories
            )
        )

    if neutral_categories:
        st.markdown(
            "⚪ **중립/근거 부족** · "
            + " · ".join(
                neutral_categories
            )
        )

    if negative_categories:
        st.markdown(
            "🔴 **부정 쪽** · "
            + " · ".join(
                negative_categories
            )
        )

    st.markdown("")

    # --------------------------------------
    # 2. 2열 점수 카드
    # --------------------------------------
    for start in range(
        0,
        len(ordered_categories),
        2
    ):
        columns = st.columns(
            2,
            gap="small"
        )

        pair = ordered_categories[
            start:start + 2
        ]

        for column, category in zip(
            columns,
            pair
        ):
            data = review_summary[
                category
            ]

            display = category_display_data[
                category
            ]

            emoji = CATEGORY_EMOJIS.get(
                category,
                "•"
            )

            score = display[
                "score"
            ]

            icon = display[
                "icon"
            ]

            label = display[
                "label"
            ]

            evidence_label = display[
                "evidence_label"
            ]

            positive_score = float(
                data.get(
                    "positive_score",
                    0
                ) or 0
            )

            negative_score = float(
                data.get(
                    "negative_score",
                    0
                ) or 0
            )

            with column:
                with st.container(
                    border=True
                ):
                    st.markdown(
                        (
                            '<div class="review-card-heading">'
                            '<span class="review-card-title">'
                            f'{emoji} {html.escape(str(category))}'
                            '</span>'
                            '<span class="review-card-status">'
                            f'{icon} {html.escape(str(label))}'
                            '</span>'
                            '</div>'
                        ),
                        unsafe_allow_html=True,
                    )

                    if score is None:
                        st.metric(
                            "리뷰 감정 점수",
                            "정보 없음"
                        )

                        st.caption(
                            "이 항목을 판단할 긍정·부정 표현이 "
                            "충분히 감지되지 않았습니다."
                        )

                    else:
                        st.metric(
                            "리뷰 감정 점수",
                            f"{score:.1f} / 100"
                        )

                        st.progress(
                            score / 100.0,
                            text=f"{label}"
                        )

                        st.caption(
                            f"리뷰 근거량: **{evidence_label}**"
                        )

    # --------------------------------------
    # 3. 부정 표현은 아래에 대표 표현만 정리
    # --------------------------------------
    negative_signal_rows = []

    for category in ordered_categories:
        data = review_summary[
            category
        ]

        matches = list(
            data.get(
                "negative_matches",
                []
            ) or []
        )

        if not matches:
            continue

        representative = matches[
            :4
        ]

        negative_signal_rows.append(
            (
                category,
                representative
            )
        )

    if negative_signal_rows:
        st.markdown(
            "##### ⚠️ 리뷰에서 감지된 아쉬운 표현"
        )

        st.caption(
            "같은 표현이 반복되더라도 대표 표현만 간단히 표시합니다."
        )

        for category, matches in negative_signal_rows:
            emoji = CATEGORY_EMOJIS.get(
                category,
                "•"
            )

            st.markdown(
                f"**{emoji} {category}**  ·  "
                + " · ".join(
                    matches
                )
            )



# ======================================
# 가격 수준
# ======================================

PRICE_LEVEL_LABELS = {
    "PRICE_LEVEL_FREE": "무료",
    "PRICE_LEVEL_INEXPENSIVE": "저렴",
    "PRICE_LEVEL_MODERATE": "보통",
    "PRICE_LEVEL_EXPENSIVE": "비싼 편",
    "PRICE_LEVEL_VERY_EXPENSIVE": "매우 비싼 편",
}


PRICE_FILTER_OPTIONS = {
    "전체": None,
    "저렴": {"PRICE_LEVEL_INEXPENSIVE"},
    "보통": {"PRICE_LEVEL_MODERATE"},
    "비싼 편": {"PRICE_LEVEL_EXPENSIVE"},
    "매우 비싼 편": {"PRICE_LEVEL_VERY_EXPENSIVE"},
}


# ======================================
# 💰 V25: 리뷰 속 실제 원화 가격 추출
# ======================================

KRW_PRICE_PATTERNS = [
    # 명확한 1인 가격: 1인 17,900원 / 1인당 2만원 / 인당 2.5만원
    re.compile(
        r'(?:1\s*인\s*당|1\s*인|인\s*당)\s*'
        r'([0-9]+(?:[,，][0-9]{3})*|[0-9]+(?:\.[0-9]+)?)\s*'
        r'(만원|만\s*원|원|won|krw)\b',
        re.I
    ),

    # 2인/3인/4인 가격: 2인 5만원, 3인 7만5천원
    re.compile(
        r'([2-9]|10)\s*인\s*'
        r'([0-9]+(?:[,，][0-9]{3})*|[0-9]+(?:\.[0-9]+)?)\s*'
        r'(만원|만\s*원|원|won|krw)\b',
        re.I
    ),

    # 2명/3명/4명 가격: 2명 6만원
    re.compile(
        r'([2-9]|10)\s*명\s*'
        r'([0-9]+(?:[,，][0-9]{3})*|[0-9]+(?:\.[0-9]+)?)\s*'
        r'(만원|만\s*원|원|won|krw)\b',
        re.I
    ),

    # 둘이서/셋이서/넷이서 가격
    re.compile(
        r'(?:둘이서|둘이|세명이서|셋이서|셋이|네명이서|넷이서|넷이)\s*'
        r'([0-9]+(?:[,，][0-9]{3})*|[0-9]+(?:\.[0-9]+)?)\s*'
        r'(만원|만\s*원|원|won|krw)\b',
        re.I
    ),

    # 인원수 없이 쓰인 일반 원화 가격
    re.compile(
        r'([0-9]{1,3}(?:[,，][0-9]{3})+|[0-9]{4,7})\s*'
        r'(원|won|krw|w)\b',
        re.I
    ),

    # 3만원 / 2.5만원 / 5만 원
    re.compile(
        r'([0-9]+(?:\.[0-9]+)?)\s*'
        r'(만\s*원|만원)\b',
        re.I
    ),

    # 2만5천원 / 1만8천원
    re.compile(
        r'([0-9]+)\s*만\s*([0-9]+)\s*천\s*원\b',
        re.I
    ),
]


def _parse_price_amount(number_text, unit_text):
    number = str(number_text).replace(",", "").replace("，", "").strip()
    unit = str(unit_text).replace(" ", "").lower()

    try:
        value = float(number)
    except ValueError:
        return None

    if "만" in unit:
        value *= 10000

    if value < 1000 or value > 2000000:
        return None

    return int(round(value))


def extract_prices_from_reviews(reviews):
    """
    리뷰에서 실제 가격 표현을 추출한다.

    우선순위:
    1) 1인/인당 가격
    2) 2인·3인 등 총액 → 인당 가격으로 환산
    3) 둘이서/셋이서 총액 → 인당 가격으로 환산
    4) 일반 가격 표현
    """
    per_person_prices = []
    total_group_prices = []
    general_prices = []

    for review in reviews or []:
        if isinstance(review, dict):
            raw = " ".join([
                str(review.get("text", "")),
                str(review.get("review_text", "")),
                str(review.get("translated_text", "")),
            ])
        else:
            raw = str(review)

        # 1인 / 인당
        for match in KRW_PRICE_PATTERNS[0].finditer(raw):
            value = _parse_price_amount(match.group(1), match.group(2))
            if value:
                per_person_prices.append(value)

        # N인 총액 → 인당 환산
        for match in KRW_PRICE_PATTERNS[1].finditer(raw):
            people = int(match.group(1))
            total = _parse_price_amount(match.group(2), match.group(3))
            if total:
                total_group_prices.append(total / people)

        # N명 총액 → 인당 환산
        for match in KRW_PRICE_PATTERNS[2].finditer(raw):
            people = int(match.group(1))
            total = _parse_price_amount(match.group(2), match.group(3))
            if total:
                total_group_prices.append(total / people)

        # 둘이서/셋이서/넷이서 총액 → 인당 환산
        for match in KRW_PRICE_PATTERNS[3].finditer(raw):
            word = match.group(0)
            people = 2 if ("둘" in word) else (3 if "셋" in word or "세명" in word else 4)
            total = _parse_price_amount(match.group(1), match.group(2))
            if total:
                total_group_prices.append(total / people)

        # 일반 가격
        for match in KRW_PRICE_PATTERNS[4].finditer(raw):
            value = _parse_price_amount(match.group(1), match.group(2))
            if value:
                general_prices.append(value)

        # 만원
        for match in KRW_PRICE_PATTERNS[5].finditer(raw):
            value = _parse_price_amount(match.group(1), match.group(2))
            if value:
                general_prices.append(value)

        # 2만5천원
        for match in KRW_PRICE_PATTERNS[6].finditer(raw):
            try:
                value = int(match.group(1)) * 10000 + int(match.group(2)) * 1000
                if 1000 <= value <= 2000000:
                    general_prices.append(value)
            except ValueError:
                pass

    # 사람 수가 명시된 가격을 가장 신뢰한다.
    if per_person_prices:
        return sorted(set(int(round(v)) for v in per_person_prices))

    if total_group_prices:
        return sorted(set(int(round(v)) for v in total_group_prices))

    return sorted(set(general_prices))



def get_review_price_value(reviews):
    prices = extract_prices_from_reviews(reviews)

    if not prices:
        return None

    # 여러 가격이 있으면 극단값의 영향을 줄이기 위해 중앙값 사용
    prices_sorted = sorted(prices)
    middle = len(prices_sorted) // 2

    if len(prices_sorted) % 2:
        return prices_sorted[middle]

    return int(round((prices_sorted[middle - 1] + prices_sorted[middle]) / 2))


def get_price_range_label_from_reviews(reviews):
    price = get_review_price_value(reviews)

    if price is None:
        return "가격 정보 없음"

    if price <= 10000:
        return "1만원 이하"
    elif price <= 20000:
        return "1만원 ~ 2만원"
    elif price <= 30000:
        return "2만원 ~ 3만원"
    elif price <= 50000:
        return "3만원 ~ 5만원"
    else:
        return "5만원 이상"



def _money_to_krw(money):
    """Google Money 객체를 원화 숫자로 변환. KRW가 아니면 None."""
    if not isinstance(money, dict):
        return None

    currency = money.get("currencyCode")
    if currency != "KRW":
        return None

    try:
        units = float(money.get("units", 0))
        nanos = float(money.get("nanos", 0)) / 1_000_000_000
        return int(round(units + nanos))
    except (TypeError, ValueError):
        return None


def get_google_price_range(place):
    """
    Google Places의 priceRange를 우선 사용한다.
    반환: (start_krw, end_krw) 또는 None
    """
    if not isinstance(place, dict):
        return None

    price_range = place.get("priceRange")
    if not isinstance(price_range, dict):
        return None

    start = _money_to_krw(price_range.get("startPrice"))
    end = _money_to_krw(price_range.get("endPrice"))

    if start is None:
        return None

    return start, end


def price_range_label(start, end):
    if start is None:
        return "가격 정보 없음"

    if end is None:
        return f"{start:,}원 이상"

    return f"{start:,}원 ~ {end:,}원"


def google_price_range_matches(result, selected_ranges):
    """
    Google priceRange의 실제 범위와 사용자가 선택한 가격대가
    겹치는지 확인한다.
    """
    if not selected_ranges:
        return False

    restaurant = result.get("restaurant", result)
    price_range = get_google_price_range(restaurant)

    if price_range is None:
        return False

    start, end = price_range

    # endPrice는 Google 문서상 상한 미만(exclusive)으로 취급한다.
    effective_end = end if end is not None else float("inf")

    allowed_ranges = {
        "under_10000": (0, 10000),
        "10000_20000": (10000, 20000),
        "20000_30000": (20000, 30000),
        "30000_50000": (30000, 50000),
        "over_50000": (50000, float("inf")),
    }

    for key in selected_ranges:
        low, high = allowed_ranges[key]

        # 두 구간이 겹치면 허용
        if effective_end > low and start < high:
            return True

    return False

def format_distance(distance_m):
    if distance_m is None:
        return "정보 없음"
    if distance_m < 1000:
        return f"{distance_m}m"
    return f"{distance_m / 1000:.1f}km"


def format_walking_time(time_sec):
    if time_sec is None:
        return "정보 없음"

    try:
        minutes = max(
            1,
            round(
                float(time_sec)
                / 60
            )
        )
    except (
        TypeError,
        ValueError
    ):
        return "정보 없음"

    if minutes < 60:
        return f"약 {minutes}분"

    hours = minutes // 60
    remaining_minutes = (
        minutes % 60
    )

    if remaining_minutes == 0:
        return f"약 {hours}시간"

    return (
        f"약 {hours}시간 "
        f"{remaining_minutes}분"
    )



def get_price_label(place):
    """
    가격 표시 우선순위:
    1. Google Places priceRange
    2. 실제 리뷰에서 추출한 가격
    3. Google priceLevel
    """
    if not isinstance(place, dict):
        return "가격 정보 없음"

    restaurant = place.get("restaurant", place)

    # 1순위: Google의 실제 가격 범위
    google_range = get_google_price_range(restaurant)
    if google_range:
        return price_range_label(*google_range)

    # 2순위: 리뷰에 적힌 실제 가격
    reviews = place.get("reviews", [])
    review_label = get_price_range_label_from_reviews(reviews)
    if review_label != "가격 정보 없음":
        return review_label

    # 3순위: 상대적 가격 수준
    price_level = (
        restaurant.get("price_level", restaurant.get("priceLevel"))
        if isinstance(restaurant, dict)
        else None
    )

    return PRICE_LEVEL_LABELS.get(
        price_level,
        "가격 정보 없음"
    )


def matches_selected_price_ranges(result, selected_ranges):
    """
    가격 필터 우선순위:
    1. Google priceRange
    2. 리뷰에서 추출한 실제 가격
    3. 가격 정보가 없으면 제외
    """
    if not selected_ranges:
        return False

    restaurant = result.get("restaurant", result)

    if get_google_price_range(restaurant):
        return google_price_range_matches(result, selected_ranges)

    price = get_review_price_value(result.get("reviews", []))
    if price is None:
        return False

    for price_range in selected_ranges:
        if price_range == "under_10000" and price <= 10000:
            return True
        if price_range == "10000_20000" and 10000 < price <= 20000:
            return True
        if price_range == "20000_30000" and 20000 < price <= 30000:
            return True
        if price_range == "30000_50000" and 30000 < price <= 50000:
            return True
        if price_range == "over_50000" and price > 50000:
            return True

    return False

# ======================================
# 🍽️ V41: 장르 판별용 프랜차이즈 사전
# ======================================
# 목적:
# 1) Google primaryType / types를 가장 먼저 신뢰
# 2) Google 장르가 명확하지 않은 경우에만 브랜드명으로 보완
# 3) 둘 다 판별되지 않으면 선택 장르 검색에서는 제외
#
# 아래 목록은 국내 외식 프랜차이즈 중 가맹점 수가 많거나
# 실제 검색에서 자주 만날 가능성이 높은 브랜드를 우선한 1차 대형 사전이다.
# 순서는 대체로 규모가 큰 브랜드를 앞쪽에 두었으며,
# 매칭 자체에는 목록 순서가 영향을 주지 않는다.

FRANCHISE_BY_GENRE = {
    "한식": [
        "본죽&비빔밥", "한솥", "명륜진사갈비", "두찜", "땅스부대찌개",
        "본죽", "고봉민김밥인", "본도시락", "일품양평해장국", "가장맛있는족발",
        "큰맘할매순대국", "죽이야기", "원할머니", "담꾹", "열정국밥",
        "오봉집", "유가네", "마장동고기집", "곤지암할매소머리국밥", "백채김치찌개",
        "덮덮밥", "설동궁찜닭", "아구듬뿍알곤마니", "현대옥", "인생아구찜",
        "신의주찹쌀순대", "정직유부", "순수덮밥", "목구멍", "따띠삼겹",
        "고기듬뿍국물두루치기", "돼지게티", "이화수전통육개장", "조마루감자탕",
        "놀부부대찌개", "팔각도", "완미족발", "하남돼지집", "채선당",
        "한촌설렁탕", "육대장", "황금코다리", "한마음정육식당", "호세야오리바베큐",
        "푸줏간고기도시락", "밥튜브", "김사부의곱창명가", "김선생불닭발",
        "일미리금계찜닭", "무봉리토종순대국", "봉추찜닭", "고기싸롱", "불막열삼",
        "에그폭탄덮밥", "놀부보쌈", "원할머니보쌈", "마왕족발", "족발야시장",
        "보승회관", "순남시래기", "샤브향", "등촌샤브칼국수", "남다른감자탕",
        "삼백집", "새마을식당", "돌배기집", "육쌈냉면", "이바돔감자탕",
        "본설렁탕", "본우리반상", "본가", "박가부대찌개", "놀부",
        "강강술래", "송추가마골", "육전국밥", "장터국밥", "바르다김선생",
        "싸움의고수", "샤브올데이", "편백집", "편편집", "제주은희네해장국",
        "청기와타운", "이차돌", "고반식당", "숙성도", "맛찬들왕소금구이",
        "하이보", "청년고기장수", "육미제당", "고기원칙", "화로상회",
        "팔도실비집", "강남랭겹", "미가옥", "담솥", "솔솥",
        "핵밥", "뜸들이다", "홍대개미", "복호두", "장인한과",
    ],

    "중식": [
        "탕화쿵푸마라탕", "홍콩반점0410", "홍콩반점", "춘리마라탕", "보배반점",
        "탕참탕수육참잘하는집", "소림마라", "이비가짬뽕", "라홍방마라탕",
        "1키로탕수육", "라쿵푸마라탕", "라화쿵부", "마라공방", "짬뽕지존",
        "도야짬뽕", "짬뽕관", "찐하오마라탕", "홍짜장", "몬스터탕수육",
        "라사천마라탕", "홍탕", "오한수우육면가", "쉐프의생안심탕수육",
        "마라순코우", "야미마라탕", "미미관마라탕", "신룽푸마라탕", "샹츠마라",
        "이가네양꼬치", "라와", "요하마라21", "향리원마라탕", "마라홀릭",
        "짬뽕10101", "피슈마라홍탕", "취향마라", "탕수육주는육군짬뽕",
        "샤오바오우육면", "라운지목화", "교동짬뽕", "양도둑", "구들마라탕",
        "마라섬", "리얼제주텐미탕수육", "쑈진즈마라탕", "일일향", "샤오당쟈",
        "1989마라탕", "고불짬뽕", "웍스터", "마라루", "달토끼짬뽕",
        "교동짬뽕1986", "라돌이마라탕", "신마라명가", "짬뽕타임", "차알",
        "쌍팔반점", "리춘시장", "뽕사부", "신마라", "마라킹",
        "마라천향", "마라소림", "마라전설", "마라탕후루", "천유향마라향솥",
        "황금성", "만리장성", "중화가정", "상해루", "취영루",
        "팔진향", "도림", "호우섬", "딤딤섬", "팀호완",
        "크리스탈제이드", "딘타이펑", "송화산시도삭면", "매란방", "중화복춘",
    ],

    "일식": [
        "백소정", "미소야", "긴자료코", "하루엔소쿠", "쿠우쿠우",
        "물회&회덮밥9900원", "무모한초밥", "삼동소바", "배터지는생동까스",
        "미카도스시", "모토이시", "경양카츠", "히노아지", "온센", "오사이초밥",
        "우규", "면식당", "제주쾅쾅돈가스", "후토루", "25센치",
        "카츠루와", "동백카츠", "멘야마쯔리", "돈카춘", "잇쇼타코야끼",
        "후라토식당", "마케집", "마요네즈", "우동야마이루식", "하나돈까스",
        "오늘은새우회", "미스타교자", "야끼니꾸소량", "우리동네참치정육점",
        "엠브로돈까스", "스시노칸도", "스시이안앤", "다이닝야경", "기소야",
        "오레노카츠", "류센소", "상무초밥", "유미카츠", "동경규동",
        "코코이찌방야", "스시로", "아리가또맘마", "멘야하나비", "멘무샤",
        "도쿄스테이크", "온기정", "호호식당", "은행골", "갓덴스시",
        "스시하나", "스시노칸도", "아비꼬", "홍대개미", "역전우동0410",
        "역전우동", "고씨네", "카레공방", "카레오", "정돈",
        "카츠바이콘반", "카츠8", "정돈프리미엄", "멘텐", "멘야산다이메",
        "부타이", "토끼정", "소코아", "미도인", "핵밥",
        "사보텐", "돈돈정", "스시메이진", "고메스퀘어", "다이닝원",
    ],

    "양식": [
        "피나치공", "피자나라치킨공주", "파스타입니다", "슬로우캘리", "쑝쑝돈까스",
        "롤링파스타", "미태리", "도로시파스타", "홍익돈까스", "파스타앤우",
        "파스타에반하다", "돈카츠마켙", "브런치빈", "스테이크존", "코지하우스",
        "파스타예요", "서가앤쿡", "뜨돈", "호미스", "제비파스타&리조또",
        "버텍스", "요녀석", "파스토보이", "투파인드피터", "올리앤",
        "애슐리", "애슐리퀸즈", "빕스", "아웃백", "매드포갈릭",
        "라라코스트", "리미니", "도미노피자", "피자헛", "미스터피자",
        "피자스쿨", "피자마루", "피자에땅", "파파존스", "7번가피자",
        "반올림피자", "청년피자", "피자알볼로", "고피자", "프레드피자",
        "노모어피자", "빅스타피자", "피자먹다", "비스트로피자", "지정환피자",
        "더플레이스", "바비레드", "니뽕내뽕", "뉴욕야시장", "샐러디",
        "샐러디아", "그리너", "샐러드로우", "포케올데이", "피그인더가든",
        "어글리스토브", "매드포갈릭", "플라잉볼", "버거앤프라이즈", "브루클린더버거조인트",
        "다운타우너", "노스트레스버거", "바스버거", "루이스버거", "666버거",
    ],

    "아시아 음식": [
        "미분당", "포케올데이", "노량진의전설미스사이공", "미스사이공",
        "다복향마라탕", "홍대쌀국수", "까몬", "일공공샤브&편백찜", "월미당",
        "베트남노상식당", "오유미당", "사이공본가", "포트리스", "다다하다",
        "도스마스", "하노이별", "쌈촌", "꾸아", "반포식스", "포슈아",
        "반미362", "에머이", "포메인", "포베이", "생어거스틴",
        "아그라", "커리146", "델리커리", "강가", "아그라",
        "타이반쩜", "타이홀릭", "타이투고", "타이익스프레스", "콘타이",
        "퍼틴", "호치민", "땀땀", "효뜨", "을지깐깐",
        "소이연남", "레호이", "굿손", "콴안다오", "포36거리",
        "인더비엣", "사이공리", "사이공핫팟", "포유", "베트남쌀국수미스420",
        "마하차이", "살라댕", "반포식스", "라오삐약", "방콕익스프레스",
        "바나나테이블", "어메이징타이", "부다스벨리", "게방식당", "쿠차라",
        "타코벨", "바토스", "감성타코", "낙원타코", "온더보더",
        "갓잇", "멕시칸라이브그릴", "도스타코스", "타코로코", "타코박스",
    ],

    "치킨": [
        "BBQ", "비비큐", "bhc", "BHC", "교촌치킨",
        "처갓집양념치킨", "굽네치킨", "네네치킨", "페리카나", "멕시카나",
        "호식이두마리치킨", "푸라닭", "노랑통닭", "60계치킨", "자담치킨",
        "또래오래", "가마치통닭", "치킨플러스", "후라이드참잘하는집", "부어치킨",
        "깐부치킨", "치킨마루", "땅땅치킨", "오븐마루", "오꾸닭",
        "티바두마리치킨", "누구나홀딱반한닭", "꾸브라꼬숯불두마리치킨",
        "꾸브라꼬숯불치킨", "순수치킨", "바른치킨", "아라치", "동근이숯불두마리치킨",
        "지코바치킨", "지코바", "맥시칸치킨", "맥시카나", "치킨신드롬",
        "코리엔탈깻잎두마리치킨", "맛닭꼬", "오븐에빠진닭", "오빠닭",
        "둘둘치킨", "장모님치킨", "처갓집", "또봉이통닭", "용천통닭",
        "계동치킨", "장작구이통닭", "보드람치킨", "마니커치킨", "치킨더홈",
        "디디치킨", "치요남치킨", "투존치킨", "치킨과바람피자", "치킨매니아",
        "치킨678", "치킨대학교", "치킨89", "치킨인류", "치킨이즈백",
        "철인7호", "치킨의민족", "치킨갱스터", "치킨마루", "치킨플러스",
        "마마치킨", "삼덕통닭", "수원왕갈비통닭", "오늘통닭", "대구통닭",
        "계림원누룽지통닭구이", "한앤둘치킨", "닭장수후라이드", "아웃닭",
        "치킨뱅이", "치킨캐슬", "코코로치킨", "치킨공방", "치킨선생",
        "치킨파머스", "치킨히어로", "치킨몬스터", "치킨쌀롱", "치킨보이",
        "치킨킹", "치킨하우스", "치킨스토리", "치킨팩토리", "치킨클럽"
    ],

    "분식": [
        "동대문엽기떡볶이", "엽기떡볶이", "신전떡볶이", "청년다방", "죠스떡볶이",
        "감탄떡볶이", "아딸", "두끼", "삼첩분식", "배떡",
        "응급실국물떡볶이", "우리할매떡볶이", "스텔라떡볶이", "신참떡볶이",
        "걸작떡볶이치킨", "떡볶이참잘하는집", "국대떡볶이", "스쿨푸드",
        "김가네", "고봉민김밥인", "바르다김선생", "얌샘김밥", "김밥천국",
        "김밥나라", "김밥일번지", "김밥킹", "리김밥", "마녀김밥",
        "보영만두", "북촌손만두", "명인만두", "장호덕손만두", "신포우리만두",
        "개성손만두", "만두여행", "공씨네주먹밥", "봉구스밥버거", "오니기리와이규동",
        "공수간", "아리가또맘마", "먹쉬돈나", "모범떡볶이", "크앙분식",
        "태리로제떡볶이", "마피아떡볶이", "불스떡볶이", "신불떡볶이", "불떡클럽",
        "또보겠지떡볶이집", "애플하우스", "아차산매운떡볶이", "미미네", "삭",
        "코끼리분식", "나누미떡볶이", "남도분식", "또뽀끼야", "철길떡볶이",
        "달토끼의떡볶이흡입구역", "떡군이네떡볶이", "분식쌀롱", "마성떡볶이",
        "해피치즈스마일", "또또분식", "학교앞분식", "분식문방구", "스쿨스토어",
        "킹콩떡볶이", "올떡볶이", "웰빙김밥", "토마토김밥", "선비꼬마김밥",
        "울산꼬마김밥", "마리짱", "오마뎅", "부산어묵", "고래사어묵",
        "삼진어묵", "미도어묵", "환공어묵", "이가네떡볶이", "상국이네",
        "다리집", "빨봉분식", "수유리우동집", "역전우동0410", "역전우동",
        "봉평메밀", "압구정김밥", "싸다김밥", "오토김밥", "보슬보슬",
        "김선생", "정직유부", "유부부", "유부야", "유부남"
    ],

    "패스트푸드": [
        "맘스터치", "롯데리아", "프랭크버거", "노브랜드버거", "버거킹",
        "맘스피자", "버거리", "왓더버거", "비스트로피자", "퀴즈노스",
        "지정환피자", "맥도날드", "죠샌드위치", "스테프핫도그", "써브웨이",
        "서브웨이", "KFC", "케이에프씨", "파파이스", "쉐이크쉑",
        "쉑쉑", "버거앤프라이즈", "바스버거", "666버거", "뉴욕버거",
        "버거스올마이티", "버거운버거", "힘난다버거", "크라이치즈버거", "고든램지버거",
        "에그드랍", "이삭토스트", "토스트럭", "석봉토스트", "캠토토스트",
        "명랑핫도그", "아리랑핫도그", "청춘핫도그", "뉴욕핫도그앤커피", "감자밭핫도그",
        "피자헛", "도미노피자", "미스터피자", "피자스쿨", "피자마루",
        "파파존스", "반올림피자", "청년피자", "피자알볼로", "고피자",
        "프레드피자", "노모어피자", "빅스타피자", "피자먹다", "7번가피자",
        "봉구스밥버거", "밥버거", "스쿨푸드", "김가네", "한솥",
    ],

    "카페·디저트": [
        "메가엠지씨커피", "메가MGC커피", "메가커피", "컴포즈커피", "이디야커피",
        "이디야", "빽다방", "투썸플레이스", "더벤티", "텐퍼센트스페셜티커피",
        "텐퍼센트커피", "매머드익스프레스", "매머드커피", "하삼동커피", "디저트39",
        "더리터", "카페봄봄", "할리스", "카페만월경", "커피베이",
        "감성커피", "요거프레소", "하이오커피", "달리는커피", "엔제리너스",
        "카페051", "블루샥", "탐앤탐스", "파스쿠찌", "커피빈",
        "폴바셋", "스타벅스", "커피에반하다", "카페게이트", "우지커피",
        "달콤커피", "카페띠아모", "토프레소", "더카페", "카페베네",
        "드롭탑", "커피스미스", "커피명가", "마노핀", "커피니",
        "벌크커피", "읍천리382", "카페인중독", "아마스빈", "공차",
        "팔공티", "차얌", "흑화당", "쥬씨", "쥬스식스",
        "설빙", "카페보니또", "빙달", "요아정", "카페요아정",
        "요거트아이스크림의정석", "요거트월드", "요거트아이스크림", "배스킨라빈스", "나뚜루",
        "하겐다즈", "백미당", "소복", "브알라", "젤라띠젤라띠",
        "파리바게뜨", "뚜레쥬르", "던킨", "크리스피크림", "성심당",
        "브레댄코", "빵장수단팥빵", "로티보이", "앤티앤스", "와플대학",
        "와플칸", "베러먼데이", "카페일리터", "커피마마", "커피홀",
        "토스피아", "샌드리아", "샐러디", "에그드랍", "이삭토스트",
    ],

    "주점·술집": [
        "투다리", "역전할머니맥주1982", "역전할머니맥주", "크라운호프보리장인",
        "크라운호프", "간이역", "펀비어킹", "철길부산집", "김복남맥주",
        "인쌩맥주", "금별맥주", "압구정봉구비어", "봉구비어", "생마차",
        "생활맥주", "까투리", "포차천국", "호맥", "79대포",
        "쏘시지요", "깡우동", "용용선생", "설맥", "팔팔포장마차",
        "한신포차", "백스비어", "달빛맥주", "오늘술집주다방", "1943",
        "포차어게인", "포차끝판왕", "꼬지사께", "꼬치의품격", "노군꼬치",
        "토리고야", "오뎅식당", "오뎅바", "청담이상", "이자카야나무",
        "수작", "무지개맥주", "뉴욕야시장", "롱타임노씨", "브롱스",
        "와바", "비어캐빈", "맥주창고", "맥주바켓", "비어룸",
        "코다차야", "청춘연가", "도쿄시장", "하이카라", "미술관",
        "회장님댁", "구주", "구주도", "인생건어물", "삼구포차",
        "육회바른연어", "육회한연어", "낭만포차", "새마을포차", "옥탑방",
        "진짜맥주", "범맥주", "아트몬스터", "서울브루어리", "맥파이브루잉",
    ],
}

# ======================================
# 🍽️ V45: 점포 수 우선 프랜차이즈 확장 사전
# ======================================
#
# 공정위 2025년도 정보공개서 기반 업종별 가맹점 수 순위를 참고해,
# 실제로 주변 검색에서 만날 가능성이 높은 브랜드부터 보강한다.
#
# 주의:
# - 공정위의 공식 업종 분류와 우리 앱의 사용자 장르는 완전히 같지 않다.
# - 따라서 공식 업종을 기계적으로 복사하지 않고,
#   우리 앱의 10개 장르 의미에 맞는 브랜드만 선별한다.
# - 예: 공식 '서양식'에 들어간 일본 카레/돈카츠 브랜드는
#   우리 앱에서는 일식으로 유지한다.
#
# 아래 목록은 기존 FRANCHISE_BY_GENRE 앞에 합쳐지며,
# 중복 브랜드는 자동 제거된다.

RANKED_FRANCHISE_ADDITIONS = {

    "한식": [
        # 가맹점 수 상위권 추가 확장
        "따띠삼겹",
        "고기듬뿍국물두루치기",
        "돼지게티",
        "이화수전통육개장",
        "조마루감자탕",
        "놀부부대찌개",
        "팔각도",
        "완미족발",
        "하남돼지집",
        "채선당",
        "한촌설렁탕",
        "육대장",
        "황금코다리",
        "한마음정육식당",
        "호세야오리바베큐",
        "푸줏간고기도시락",
        "밥튜브",
        "김사부의곱창명가",
        "김선생불닭발",
        "일미리금계찜닭",
        "무봉리토종순대국",
        "봉추찜닭",
        "고기싸롱",
        "불막열삼",
        "에그폭탄덮밥",
        "육칠이",
        "족발신선생",
        "뚜선장쭈꾸미호",
        "곱분이곱창",
        "킹콩부대찌개",
        "더마니",
        "샤브마니아",
        "미진축산",
        "삼산회관",
        "죽이요",
        "고기극찬",
        "밥꼬콩불",
        "김사부본가갈비찜",
        "제주은희네해장국",
        "구구족",
        "바우네나주곰탕",
        "국물에빠진두루치기",
        "기대만족",
        "밥풀릭스",
        "인생냉면",
        "고기듬뿍대왕비빔밥",
        "인생극장",
        "배고픈덮밥이",
        "도야족발보쌈",
        "최강곱도리",
        "그집곱닭도리탕",
        "박가부대",
        "구름계란덮밥",
        "조선화로닭발",
        "송담추어탕",
        "요달의찜닭",
        "수유리혼밥왕",
        "국밥참맛있는집",

        # 상권에서 자주 보이는 추가 한식 브랜드
        "순대실록",
        "신의주찹쌀순대",
        "육전국밥",
        "강창구찹쌀진순대",
        "담소소사골순대육개장",
        "전주현대옥",
        "양평서울해장국",
        "제주몬트락",
        "부엉이산장",
        "청기와타운",
        "고반식당",
        "고기원칙",
        "고기를품다",
        "고돼지",
        "고기굽는남자",
        "고기꾼김춘배",
        "숙달돼지",
        "육시리",
        "대패상회",
        "고깃리88번지",
        "화로상회",
        "육미제당",
        "청년고기장수",
        "냉삼식당",
        "팔도실비집",
        "연안식당",
        "오징어청춘",
        "인생설렁탕",
        "문래돼지불백",
        "정성순대",
        "밀밭칼국수",
        "장터국밥",
        "소문난순대국",
        "대독장",
        "김치도가",
        "찌개애감동",
        "찌개마을",
        "육수당",
        "명동칼국수",
        "강릉장칼",
        "박용채의대박터진돈까스",
        "담솥",
        "솔솥",
        "온밥",
        "뜸들이다",
        "덮밥장사장",
        "백억덮밥",
        "모두의죽",
        "죽선생",
    ],

    "중식": [
        # 기존 상위권에 이어 가맹점 순위 하위권까지 확장
        "이런이궈",
        "착한쭝식",
        "손오공마라탕",
        "명객양꼬치",
        "역대짬뽕",
        "마차이짬뽕",
        "전설의짬뽕",
        "메이탄",
        "츠츠허허",
        "장수루양꼬치",
        "큐큐면관",
        "아뵤오반점",
        "덕클",
        "중경식객",
        "구복만두",
        "불이아",
        "오리총재",
        "마유유마라탕",
        "그집짬뽕0927",
        "무궁화반점",

        # 국내에서 자주 보이는 중식/마라/양꼬치 브랜드 보강
        "하이디라오",
        "딘타이펑",
        "크리스탈제이드",
        "호우섬",
        "딤딤섬",
        "팀호완",
        "팔진향",
        "취영루",
        "도림",
        "차이797",
        "js가든",
        "js가든웍",
        "신승반점",
        "송화산시도삭면",
        "천천향",
        "마라영웅",
        "마라연구소",
        "마라대국",
        "마라천국",
        "마라신",
        "마라퀸",
        "마라민족",
        "마라선생",
        "마라왕",
        "마라미방",
        "마라공주",
        "마라대장",
        "마라시대",
        "마라명가",
        "마라반점",
        "짬뽕상회",
        "짬뽕의신",
        "짬뽕전문점",
        "교동반점",
        "복성루",
        "지린성",
        "만다복",
        "연경",
        "태화장",
        "공화춘",
        "신발원",
        "일품향",
        "중화문",
        "홍콩대패당",
    ],

    "일식": [
        # 공정위 가맹점 수 순위에서 기존 목록에 없던 브랜드 보강
        "물회&회덮밥9900원",
        "무모한초밥",
        "삼동소바",
        "배터지는생동까스",
        "미카도스시",
        "모토이시",
        "만타스시31",
        "카츠백",
        "이라이타코야끼",
        "타코아찌",
        "토리아에즈",
        "참다랑어막주는집",
        "규카츠정",
        "카레세끼",
        "어부김호권의청년어부",
        "이찌방라멘",
        "라멘선생",
        "남바완돈카츠",
        "탐나종합어시장",
        "우마이타코야끼",
        "여부초밥",
        "저스트텐동",
        "원카츠",
        "히츠지야",
        "산카이이자카야",
        "소노야",
        "큐슈울트라아멘",
        "요미우돈교자",
        "가츠몽",
        "청연",
        "겐로쿠우동",
        "고쿠텐",
        "숯토리",
        "치히로",
        "쿠마키친",
        "로봇초밥마켓",
        "스시화",
        "회가대표초밥24",
        "쇼쿠지",
        "구름카츠",
        "이치류",

        # 추가 주요 일식 체인
        "아비꼬",
        "사보텐",
        "돈돈정",
        "토끼정",
        "소코아",
        "미도인",
        "정돈",
        "정돈프리미엄",
        "카츠8",
        "카츠바이콘반",
        "부타이",
        "멘텐",
        "멘야산다이메",
        "멘야하나비",
        "유타로",
        "코이라멘",
        "아오리의행방불명",
        "스시메이진",
        "고메스퀘어",
        "다이닝원",
        "갓덴스시",
        "은행골",
        "스시로",
        "스시웨이",
        "초밥대통령",
        "스시쿠모",
        "초이다이닝",
        "호호식당",
        "후라토식당",
    ],

    "양식": [
        # 서양식 가맹점 순위 기반 + 우리 앱 장르에 맞는 브랜드만 선별
        "피나치공",
        "파스타입니다",
        "슬로우캘리",
        "롤링파스타",
        "미태리",
        "도로시파스타",
        "파스타앤우",
        "파스타에반하다",
        "브런치빈",
        "스테이크존",
        "코지하우스",
        "파스타예요",
        "서가앤쿡",
        "뜨돈",
        "호미스",
        "제비파스타&리조또",
        "버텍스",
        "요녀석",
        "파스토보이",
        "투파인드피터",
        "올리앤",
        "4242샌드위치",
        "파스타집이야",
        "덕수파스타",
        "벤티버거",
        "류길상피자",
        "파스타를부탁해",
        "파스타9900원",
        "폴라니포케",
        "트루바이",
        "봉대박스파게티",
        "신입파스타",
        "닐리",
        "이태리면가게",
        "루스트플레이스",
        "파스타왔어요",
        "피자플래넷",
        "돈까스BROS",
        "파스타부오노바",
        "파스타어때",
        "뽁식당",
        "샐요뜨",
        "에스엘비",
        "오샐러드",
        "미국버거201",
        "멕시칸라이브그릴",
        "빠레뜨한남",
        "고고함박",
        "가든쿡",
        "피자와일드",
        "올라포케",
        "착한파스타",
        "그랜마스",
        "포시즌키친",
        "와르르파스타",
        "더몰트하우스",
        "달리181",
        "스탠딩스테이크",
        "파스타제작소",
        "뉴욕스테이크",
        "파스타치요",
        "점보파스타",
        "괴짜쉐프파스타",
        "알라보",

        # 피자/패밀리레스토랑/샐러드 체인 보강
        "도미노피자",
        "피자헛",
        "미스터피자",
        "파파존스",
        "피자스쿨",
        "피자마루",
        "피자에땅",
        "반올림피자샵",
        "반올림피자",
        "청년피자",
        "피자알볼로",
        "고피자",
        "프레드피자",
        "노모어피자",
        "빅스타피자",
        "7번가피자",
        "유로코피자",
        "오구쌀피자",
        "피자헤븐",
        "피자빙고",
        "난타5000피자",
        "뽕뜨락피자",
        "피자2001",
        "피자캣",
        "아웃백",
        "빕스",
        "애슐리퀸즈",
        "매드포갈릭",
        "라라코스트",
        "더플레이스",
        "샐러디",
        "그리너",
        "피그인더가든",
        "샐러드로우",
    ],

    "아시아 음식": [
        # 기타 외국식 순위 중 우리 앱의 아시아/외국식 의미에 맞는 항목
        "미분당",
        "포케올데이",
        "노량진의전설미스사이공",
        "미스사이공",
        "홍대쌀국수",
        "까몬",
        "일공공샤브&편백찜",
        "월미당",
        "베트남노상식당",
        "오유미당",
        "사이공본가",
        "포트리스",
        "다다하다",
        "도스마스",
        "하노이별",
        "쌈촌",
        "꾸아",
        "반포식스",
        "포슈아",
        "반미362",
        "에머이",
        "메콩타이",
        "리틀하노이",
        "포시애틀",
        "옥소반",

        # 베트남/태국/인도/멕시칸 등 추가
        "포메인",
        "포베이",
        "호아빈",
        "포몬스",
        "포유",
        "퍼틴",
        "땀땀",
        "효뜨",
        "을지깐깐",
        "소이연남",
        "레호이",
        "콴안다오",
        "인더비엣",
        "사이공리",
        "마하차이",
        "콘타이",
        "타이반쩜",
        "타이홀릭",
        "타이익스프레스",
        "방콕익스프레스",
        "어메이징타이",
        "부다스벨리",
        "아그라",
        "강가",
        "델리커리",
        "커리146",
        "바나나테이블",
        "감성타코",
        "낙원타코",
        "온더보더",
        "갓잇",
        "바토스",
        "도스타코스",
        "타코로코",
        "쿠차라",
        "타코벨",
    ],

    "치킨": [
        # 공정위 가맹점 수 상위권 90위 안쪽 브랜드 보강
        "지코바양념치킨",
        "훌랄라",
        "기영이숯불두마리치킨",
        "보드람치킨",
        "신통치킨",
        "돈치킨",
        "순살몬스터",
        "썬더치킨",
        "가마로강정",
        "순살만공격",
        "알통떡강정",
        "김종구식맛치킨",
        "호치킨",
        "불로만치킨바베큐",
        "본스치킨",
        "다사랑",
        "갓튀긴후라이드",
        "코리안바베큐",
        "오븐에꾸운닭",
        "DK동키치킨",
        "인생닭강정",
        "명가통닭",
        "디디치킨",
        "화평댁닭구이",
        "쌀통닭",
        "냠냠숯불두마리치킨",
        "구도로통닭",
        "1번지통닭",
        "이춘봉치킨",
        "충만치킨",
        "아주커",
        "림스치킨",
        "두레통닭",
        "박군치킨",
        "컬투치킨",
        "칠봉통닭",
        "배무치숯불두마리치킨",
        "스모프치킨",
        "남썬치킨",
        "국제통닭",
        "영계소문옛날통닭",
        "전설의치킨",
        "미쳐버린파닭",
        "봉이치킨",
        "오태식해바라기치킨",
        "청년치킨",
        "88켄터키치킨&떡볶이",
        "홍희통닭",

        # 추가 치킨 체인
        "오꾸닭",
        "맛닭꼬",
        "오븐에빠진닭",
        "아웃닭",
        "계림원누룽지통닭구이",
        "삼덕통닭",
        "수원왕갈비통닭",
        "대구통닭",
        "치킨뱅이",
        "치킨공방",
        "치킨선생",
        "철인7호",
        "치킨인류",
        "치킨의민족",
        "치킨더홈",
        "치킨매니아",
        "투존치킨",
        "순수치킨",
    ],

    "분식": [
        # 공정위 분식 순위에서 기존 목록 누락 브랜드 보강
        "이삭토스트",
        "우리할매떡볶이",
        "선비꼬마김밥",
        "국수나무",
        "기떡찜",
        "장호덕손만두",
        "한신우동",
        "용우동",
        "수유리우동집",
        "애플꼬마김밥",
        "김종구부산어묵",
        "태리로제떡볶이&닭강정",
        "떡볶이참잘하는집",
        "떡참",
        "할머니가래떡볶이",
        "오마뎅",
        "강다짐",
        "모락떡볶이",
        "호시타코야끼",
        "올떡",
        "지지고",
        "달떡볶이",
        "무공돈까스",
        "틈새라면",
        "버무리떡볶이",
        "신떡순신천할매떡볶이",
        "을찌로국물떡볶이",
        "오백국수",
        "뽁떡떡볶이",

        # 추가 분식 체인
        "마성떡볶이",
        "킹콩떡볶이",
        "신불떡볶이",
        "불스떡볶이",
        "마피아떡볶이",
        "크앙분식",
        "해피치즈스마일",
        "빨봉분식",
        "학교앞분식",
        "분식문방구",
        "스쿨스토어",
        "보영만두",
        "북촌손만두",
        "신포우리만두",
        "명인만두",
        "고래사어묵",
        "삼진어묵",
        "미도어묵",
        "이가네떡볶이",
        "상국이네",
        "다리집",
        "싸다김밥",
        "토마토김밥",
        "오토김밥",
        "마녀김밥",
        "보슬보슬",
        "얌샘김밥",
        "정직유부",
    ],

    "패스트푸드": [
        # 실제 점포 수 상위권 브랜드 우선
        "맘스터치",
        "롯데리아",
        "프랭크버거",
        "노브랜드버거",
        "버거킹",
        "맘스피자",
        "버거리",
        "왓더버거",
        "퀴즈노스서브",
        "퀴즈노스",
        "맥도날드",
        "죠샌드위치",
        "스테프핫도그",
        "아띠몽",
        "맘스터치피자앤치킨",
        "석봉토스트",
        "쏘자",
        "점순이호떡",
        "BT버거앤타코",
        "코브라독스",
        "힘난다버거",
        "오지버거",
        "버거운버거",
        "잇샌드",
        "에그셀런트",
        "밀플랜비",

        # 주요 글로벌/국내 브랜드
        "KFC",
        "케이에프씨",
        "파파이스",
        "쉐이크쉑",
        "쉑쉑",
        "써브웨이",
        "서브웨이",
        "에그드랍",
        "명랑핫도그",
        "뉴욕버거",
        "버거앤프라이즈",
        "크라이치즈버거",
        "버거스올마이티",
        "바스버거",
    ],

    "카페·디저트": [
        # 커피 가맹점 수 상위권 추가
        "메가엠지씨커피",
        "메가MGC커피",
        "컴포즈커피",
        "이디야커피",
        "빽다방",
        "투썸플레이스",
        "더벤티",
        "텐퍼센트스페셜티커피",
        "매머드익스프레스",
        "하삼동커피",
        "디저트39",
        "더리터",
        "카페봄봄",
        "할리스",
        "카페만월경",
        "커피베이",
        "감성커피",
        "요거프레소",
        "하이오커피",
        "달리는커피",
        "엔제리너스",
        "카페051",
        "블루샥",
        "탐앤탐스커피",
        "카페게이트",
        "더카페",
        "드롭탑",
        "베러먼데이",
        "청자다방",
        "셀렉토커피",
        "포트캔커피",
        "카페일리터",
        "댄싱컵",
        "카페일분",
        "천씨씨커피",
        "아마스빈",
        "커스텀커피",
        "몬스터커피",
        "토프레소",
        "트리플에이커피",
        "커피마마",
        "발도스커피",
        "만랩커피",
        "모리커피",
        "커피사피엔스",
        "달콤",
        "원유로스페셜티커피",
        "청솔로9",
        "카페인24",
        "커피나인",
        "더치앤빈",
        "커피쿡",
        "영커피",

        # 디저트/제과/빙수/음료 브랜드
        "파리바게뜨",
        "뚜레쥬르",
        "던킨",
        "크리스피크림",
        "공차",
        "팔공티",
        "차얌",
        "쥬씨",
        "설빙",
        "요아정",
        "요거트아이스크림의정석",
        "요거트월드",
        "배스킨라빈스",
        "나뚜루",
        "백미당",
        "브알라",
        "와플대학",
        "와플칸",
        "앤티앤스",
        "로티보이",
        "브레댄코",
        "빵장수단팥빵",
        "커피에반하다",
        "카페베네",
        "파스쿠찌",
        "커피빈",
        "폴바셋",
        "스타벅스",
    ],

    "주점·술집": [
        # 가맹점 수 상위권 확장
        "투다리",
        "역전할머니맥주1982",
        "크라운호프보리장인",
        "간이역",
        "펀비어킹",
        "철길부산집",
        "김복남맥주",
        "인쌩맥주",
        "금별맥주",
        "압구정봉구비어",
        "생마차",
        "생활맥주",
        "까투리",
        "포차천국",
        "호맥",
        "79대포",
        "쏘시지요",
        "깡우동",
        "용용선생",
        "설맥",
        "팔팔포장마차",
        "무지개맥주",
        "고래맥주창고",
        "꼬지사께",
        "별난아재맥주",
        "일일수작",
        "헤즈업",
        "1도씨맥주",
        "한라맥주",
        "달빛경성술집",
        "월간맥주",
        "한남동그집",
        "치어스",
        "청담이상",
        "이태리양조장",
        "오늘와인한잔",
        "하노이맥주밤거리",
        "쉼어묵그리고한잔술",
        "잔잔",
        "전일맥주",
        "동네포차주민",
        "투사랑",
        "2도맥주",
        "탄광맥주",
        "금복주류",
        "밤하늘포차연어육회",
        "구주",
        "일월육일",
        "엘리팝",
        "촌댁맥주",
        "링코",
        "얼맥당",

        # 추가 주요 주점 브랜드
        "한신포차",
        "백스비어",
        "1943",
        "포차끝판왕",
        "오늘술집주다방",
        "노군꼬치",
        "꼬치의품격",
        "도쿄시장",
        "롱타임노씨",
        "브롱스",
        "와바",
        "뉴욕야시장",
        "수작",
        "범맥주",
        "인생건어물",
    ],
}


def _merge_ranked_franchise_additions():
    """
    점포 수 우선 목록을 기존 수동 사전 앞에 합친다.
    같은 장르 안에서는 정규화된 이름 기준으로 중복 제거한다.
    """
    for genre, additions in RANKED_FRANCHISE_ADDITIONS.items():

        original = FRANCHISE_BY_GENRE.get(
            genre,
            []
        )

        merged = []
        seen = set()

        for brand in (
            list(additions)
            + list(original)
        ):
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in seen:
                continue

            seen.add(
                normalized
            )

            merged.append(
                brand
            )

        FRANCHISE_BY_GENRE[
            genre
        ] = merged



_merge_ranked_franchise_additions()


# ======================================
# V47: 복합 프랜차이즈 교차 장르
# ======================================
MULTI_GENRE_FRANCHISE_OVERLAPS = {
    # 피자 + 치킨
    "양식": [
        "피자나라치킨공주",
        "피나치공",
        "굽네치킨",
        "피자와치킨의러브레터",
        "피치월드",
    ],

    "치킨": [
        "피자나라치킨공주",
        "피나치공",
        "굽네치킨",
        "걸작떡볶이치킨",
        "태리로제떡볶이&닭강정",
        "88켄터키치킨&떡볶이",
        "잘만든치킨굿킨",
        "굿킨",
        "피자와치킨의러브레터",
        "피치월드",
    ],

    # 떡볶이/분식 + 치킨/닭강정
    "분식": [
        "걸작떡볶이치킨",
        "태리로제떡볶이&닭강정",
        "88켄터키치킨&떡볶이",
        "잘만든치킨굿킨",
        "굿킨",
    ],

    # 포차형 한식 + 주점
    "한식": [
        "한신포차",
    ],

    "주점·술집": [
        "한신포차",
    ],
}


def _merge_multi_genre_franchises():
    for genre, brands in MULTI_GENRE_FRANCHISE_OVERLAPS.items():
        current = FRANCHISE_BY_GENRE.setdefault(
            genre,
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )
            for brand in current
        }

        for brand in brands:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )

            if normalized in normalized_existing:
                continue

            current.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_multi_genre_franchises()





# ======================================
# V48: 프랜차이즈 추가 확장
# ======================================
# 공정위 2025년도 정보공개서 기반 업종별 가맹점 순위를 참고해
# 기존 V47 사전에 없던 브랜드를 추가 보강한다.
#
# 앱 장르 기준과 공시 업종이 어긋나는 브랜드는
# 우리 앱에서 사용자가 기대할 만한 장르로 재배치한다.

V48_FRANCHISE_ADDITIONS = {
    "중식": [
        "란콰이펑누들",
        "소매점양꼬치",
        "불간짬뽕",
        "짬뽕타운",
        "마라야",
        "노사천마라탕",
        "마라사부",
        "불티나꼬막짬뽕",
    ],

    "일식": [
        "이자카야춘",
        "돈까스튀기는형",
        "이자카야게다",
        "오산조은참치",
        "범카츠",
        "마싰는끼니",
        "BIG EYE 우리동네 참치정육점",
        "코코이찌방야",
    ],

    "양식": [
        "Today Tong Tong",
        "파스타딜리",
        "세컨디포레스트",
        "빈체로",
        "피자다오",
        "훗스테이크",
        "리얼파스타",
        "더맨타코",
        "사생활",
        "명작파스타",
        "샤이바나",
        "낭만장사꾼",
        "moonbowl",
        "피자와치킨의러브레터",
        "피치월드",
    ],

    "치킨": [
        "테트리스찜닭",
        "잘만든치킨굿킨",
        "굿킨",
        "피자와치킨의러브레터",
        "피치월드",
    ],

    "분식": [
        "리틀꼬마김밥",
        "여우애",
        "소소떡볶이",
        "최가네크레이지떡볶이",
        "최배달떡순튀",
        "삼형제김밥",
        "이백장돈가스",
        "생생돈까스",
        "꽈백최선생",
        "마몽로제떡볶이",
        "탄탄면공방",
        "킹스꼬마김밥",
        "연돈튀김덮밥",
        "깨봉이국물떡볶이",
        "청년분식",
        "응큼떡볶이",
        "알촌",
        "오늘애김밥",
        "떡의작품",
        "바푸리",
        "1989역전꼬마김밥",
        "삼청당",
        "채다올김밥",
        "신만용신가네매운떡볶이",
        "신떡",
        "오공김밥",
        "춘하추동",
        "부송국수",
        "잘만든치킨굿킨",
        "굿킨",
    ],

    "카페·디저트": [
        "30 PLUS 82",
        "플러스82",
        "동네커피",
        "우주라이크",
        "핸즈커피",
        "테라커피",
        "바나타이거",
        "마실커피",
        "에이바우트커피",
        "바나프레소",
        "벤티프레소",
        "퐁치커피익스프레스",
        "복고다방",
        "더리터24",
        "아덴블랑제리",
        "바빈스",
        "마일로",
        "마시그래이",
    ],
}


def _merge_v48_franchise_additions():
    for genre, additions in V48_FRANCHISE_ADDITIONS.items():

        current = FRANCHISE_BY_GENRE.setdefault(
            genre,
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )
            for brand in current
        }

        for brand in additions:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in normalized_existing:
                continue

            current.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_v48_franchise_additions()


# ======================================
# V55: 프랜차이즈 사전 추가 확장
# ======================================
#
# 2026-08 확인:
# 공정거래위원회 2025년도 정보공개서를 기반으로 정리된
# 업종별 운영 가맹점 순위에서 기존 사전에 빠진 브랜드를 보강한다.
#
# 단순히 개수만 늘리지 않고 실제 상호명으로 잡힐 가능성이 높은
# 브랜드와 표기 별칭을 우선한다.

V55_FRANCHISE_ADDITIONS = {
    "한식": [
        "오복 오봉집",
        "오복오봉집",
        "오봉집",
        "백채",
        "대박삼겹김치찜&초대박등갈비김치찜",
    ],

    "일식": [
        "동경에서먹었던규동",
        "타코아찌 타코야끼전문점",
        "카레세끼 매운숙성카레",
        "이찌방라멘& 카츠카레",
    ],

    "양식": [
        "오구피자",
        "파파존스피자",
        "빽보이피자",
        "피자스톰",
        "자가제빵 선명희피자",
        "서오릉피자",
        "피자파는집",
        "피자와썹",
        "번쩍피자",
        "PJ피자",
        "피자는 치즈빨",
        "윤검푸드 봉수아피자",
    ],

    "치킨": [
        "비에이치씨",
        "60계",
        "60계치킨",
        "화락바베큐치킨",
        "김종구식맛치킨ㆍ 전기바베큐 옛날통닭",
        "김종구식맛치킨",
        "계림원누릉지통닭구이",
    ],

    "패스트푸드": [
        "움버거앤윙스",
        "세븐패티버거",
        "빌리언박스",
        "켈리토스트카페",
    ],

    "카페·디저트": [
        "백억커피",
        "카페프리헷",
        "봉명동내커피",
    ],

    "주점·술집": [
        "주식회사포차천국",
        "인생건어물맥주",
        "리얼펍",
        "그놈포차",
        "짝태&노가리",
        "시장을 여는 사람들",
        "장미맨숀",
        "가르텐호프앤레스트",
        "풍덕천 두꺼비집",
        "단성무이",
        "700비어",
        "뉴코뮤직타운",
        "간빠이",
        "샵도쿄시장",
        "느린마을양조장",
        "술속의밤",
        "동양맥주",
        "크래프트한스",
        "땡초우동",
        "혜화어묵당",
    ],
}


def _merge_v55_franchise_additions():
    for genre, additions in V55_FRANCHISE_ADDITIONS.items():
        current = FRANCHISE_BY_GENRE.setdefault(
            genre,
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )
            for brand in current
        }

        for brand in additions:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in normalized_existing:
                continue

            current.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_v55_franchise_additions()


# ======================================
# V56: 매장 커버율 중심 프랜차이즈 보강
# ======================================
#
# 2025년도 정보공개서의 가맹점 수 상위권을 다시 대조해서,
# 기존 사전에서 빠져 있거나 앱 장르상 재분류가 필요한 브랜드를 보강한다.
#
# 특히 제과제빵 / 커피 / 아이스크림·빙수 쪽은
# 카페·디저트 검색에서 실제 사용자가 기대하는 브랜드가 많으므로
# 공시 소분류와 무관하게 앱의 "카페·디저트"에 배치한다.

V56_COVERAGE_FRANCHISE_ADDITIONS = {
    "카페·디저트": [
        # 제과·제빵 / 간식
        "던킨도너츠",
        "코코호도",
        "복호두",
        "못난이꽈배기",
        "로띠번",
        "송사부고로케",
        "스트릿츄러스",
        "화이트리에",
        "호두당",
        "호밀호두",
        "성북당 십원빵",
        "성북당십원빵",
        "아이엠도넛",
        "IamDonut",
        "심봉사도로케",
        "하르당",
        "제이델링",

        # 아이스크림 / 요거트 / 탕후루
        "달롱도르요거트아이스크림",
        "달콤왕가탕후루",

        # 커피 상위권의 표기/브랜드 누락 보강
        "THE LITER",
        "THE LITER 24",
        "더리터24",
        "PORT CAN COFFEE",
        "COFFEE COOK",
        "파란만잔",
        "카페보스",
        "CAFE BOSS",
        "와드커피",
        "WAD COFFEE",
        "고더커피",
        "더웨이닝커피",
        "해쉬커피",
        "라바게트",
        "카페루앤비",
        "반달커피",
        "CAFE CANBUS",
        "카페캔버스",
        "NiceCaffeinClub",
        "NCC",
    ],

    "패스트푸드": [
        # 제과제빵 공시 업종이더라도 실제 사용자는 간편식으로 찾는 브랜드
        "명랑시대쌀핫도그",
        "홍루이젠",
    ],

    "양식": [
        # 공시상 기타 외국식이지만 앱 검색 기대상 양식으로 분류
        "또띠아그램",
        "파스타도 식사다",
    ],
}


def _merge_v56_coverage_franchises():
    for genre, additions in V56_COVERAGE_FRANCHISE_ADDITIONS.items():
        current = FRANCHISE_BY_GENRE.setdefault(
            genre,
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~/]+",
                "",
                str(brand).lower()
            )
            for brand in current
        }

        for brand in additions:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~/]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in normalized_existing:
                continue

            current.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_v56_coverage_franchises()




GOOGLE_GENRE_TYPES = {
    # 아래 타입들은 해당 장르로 바로 확정해도 비교적 안전한 타입만 넣는다.
    # dumpling_restaurant / noodle_shop / snack_bar / hot_pot_restaurant /
    # barbecue_restaurant 등은 국적·장르가 애매하므로 여기서 제외한다.

    "한식": {
        "korean_restaurant",
        "korean_barbecue_restaurant",
    },

    "중식": {
        "chinese_restaurant",
        "chinese_noodle_restaurant",
        "cantonese_restaurant",
        "dim_sum_restaurant",
    },

    "일식": {
        "japanese_restaurant",
        "sushi_restaurant",
        "ramen_restaurant",
        "japanese_curry_restaurant",
        "japanese_izakaya_restaurant",
        "tonkatsu_restaurant",
        "yakiniku_restaurant",
        "yakitori_restaurant",
    },

    "양식": {
        "italian_restaurant",
        "french_restaurant",
        "american_restaurant",
        "western_restaurant",
        "european_restaurant",
        "steak_house",
    },

    "아시아 음식": {
        "asian_restaurant",
        "asian_fusion_restaurant",
        "thai_restaurant",
        "vietnamese_restaurant",
        "indian_restaurant",
        "indonesian_restaurant",
        "malaysian_restaurant",
        "filipino_restaurant",
    },

    "치킨": {
        "chicken_restaurant",
        "chicken_wings_restaurant",
    },

    # Google에는 한국식 '분식' 전용 확정 타입이 없다.
    # 따라서 분식은 Google 타입으로 즉시 확정하지 않고
    # 프랜차이즈 사전으로만 보완한다.
    "분식": set(),

    "패스트푸드": {
        "fast_food_restaurant",
        "hamburger_restaurant",
        "hot_dog_restaurant",
        "hot_dog_stand",
        "sandwich_shop",
    },

    "카페·디저트": {
        "cafe",
        "coffee_shop",
        "coffee_stand",
        "bakery",
        "dessert_shop",
        "dessert_restaurant",
        "cake_shop",
        "donut_shop",
        "ice_cream_shop",
        "tea_house",
        "juice_shop",
        "pastry_shop",
    },

    "주점·술집": {
        "bar",
        "pub",
        "cocktail_bar",
        "wine_bar",
        "sports_bar",
        "beer_garden",
        "brewpub",
        "irish_pub",
        "lounge_bar",
    },
}


# 장르를 바로 확정하면 안 되는 타입.
# 후보 검색 힌트로는 쓸 수 있지만 장르 판별 근거로는 사용하지 않는다.
AMBIGUOUS_FOOD_TYPES = {
    "dumpling_restaurant",
    "noodle_shop",
    "snack_bar",
    "hot_pot_restaurant",
    "barbecue_restaurant",
    "pizza_restaurant",
    "bistro",
    "bar_and_grill",
    "gastropub",
    "burrito_restaurant",
    "food_court",
    "restaurant",
}


def normalize_brand_name(name):
    """
    프랜차이즈 이름 비교 전용 정규화.
    기존 clean_name처럼 '점' 글자 자체를 삭제하지 않는다.
    """
    if not name:
        return ""

    name = str(name).lower()

    # 지점명이 붙어도 브랜드 문자열 포함 검사가 가능하도록
    # 공백·기호만 정리한다.
    name = re.sub(r"[\s\-_.,()\[\]{}'\"·ㆍ&]+", "", name)

    return name


_NORMALIZED_FRANCHISE_BY_GENRE = {
    genre: [
        normalize_brand_name(brand)
        for brand in brands
        if normalize_brand_name(brand)
    ]
    for genre, brands in FRANCHISE_BY_GENRE.items()
}


def get_place_name(place):
    return (
        place.get("displayName", {})
        .get("text", "")
    )


def get_google_detected_genres(place):
    """
    primaryType + types로 Google이 명확하게 알려주는 장르들을 반환.
    """
    place_types = set(place.get("types", []) or [])
    primary_type = place.get("primaryType")

    if primary_type:
        place_types.add(primary_type)

    detected = set()

    for genre, google_types in GOOGLE_GENRE_TYPES.items():
        if place_types.intersection(google_types):
            detected.add(genre)

    return detected


def get_franchise_genres(place):
    """
    Google 장르가 불명확할 때만 사용하는 브랜드명 보조 판별.
    """
    normalized_name = normalize_brand_name(
        get_place_name(place)
    )

    if not normalized_name:
        return set()

    detected = set()

    for genre, brands in _NORMALIZED_FRANCHISE_BY_GENRE.items():
        for brand in brands:
            # 너무 짧은 브랜드명이 우연히 다른 상호 안에 들어가는 오탐 방지
            if len(brand) < 3:
                continue

            # 대형 사전에서는 단순 부분문자열 매칭만 사용하면
            # 짧고 일반적인 브랜드명이 다른 상호에 우연히 포함될 수 있다.
            #
            # 1) 완전 일치
            # 2) 브랜드명으로 시작 (예: 교촌치킨강남점)
            # 3) 충분히 긴 브랜드명(5자 이상)만 중간 포함 허용
            is_match = (
                normalized_name == brand
                or normalized_name.startswith(
                    brand
                )
                or (
                    len(brand) >= 5
                    and brand in normalized_name
                )
            )

            if is_match:
                detected.add(genre)
                break

    return detected


def get_explicit_multi_genre_overlaps(place):
    """
    MULTI_GENRE_FRANCHISE_OVERLAPS에 명시한 복합 브랜드만
    여러 장르로 인정한다.

    일반 프랜차이즈 전체가 Google 타입 판정을 뒤집지 않도록
    예외 범위를 복합 브랜드 사전으로 제한한다.
    """
    normalized_name = normalize_brand_name(
        get_place_name(place)
    )

    if not normalized_name:
        return set()

    detected = set()

    for genre, brands in MULTI_GENRE_FRANCHISE_OVERLAPS.items():
        for brand in brands:
            normalized_brand = normalize_brand_name(
                brand
            )

            if not normalized_brand:
                continue

            is_match = (
                normalized_name == normalized_brand
                or normalized_name.startswith(
                    normalized_brand
                )
                or (
                    len(normalized_brand) >= 5
                    and normalized_brand in normalized_name
                )
            )

            if is_match:
                detected.add(
                    genre
                )
                break

    return detected


def matches_selected_genre(place, selected_genre):
    """
    V48 장르 판별 원칙

    1) '전체'는 장르 판별 없이 통과
    2) 명시적 복합 프랜차이즈는 등록된 여러 장르를 모두 허용
    3) 그 외에는 Google primaryType / types의 확정 장르를 우선
    4) Google 확정 장르가 없을 때 일반 프랜차이즈 사전으로 보완
    5) 리뷰/메뉴 텍스트로 장르를 추정하지 않음
    """
    if selected_genre == "전체":
        return True

    # --------------------------------------
    # 1. 명시적 복합 브랜드 예외
    # 예: 피자나라치킨공주 → 양식 + 치킨
    # --------------------------------------
    overlap_genres = get_explicit_multi_genre_overlaps(
        place
    )

    if selected_genre in overlap_genres:
        return True

    # --------------------------------------
    # 2. 일반 장소는 Google의 확정 타입 우선
    # --------------------------------------
    google_genres = get_google_detected_genres(
        place
    )

    if google_genres:
        return selected_genre in google_genres

    # --------------------------------------
    # 3. Google이 확정하지 못했을 때 일반 프랜차이즈 사전
    # --------------------------------------
    franchise_genres = get_franchise_genres(
        place
    )

    return selected_genre in franchise_genres



# ======================================
# 음식점 타입 필터
# ======================================

NON_RESTAURANT_TYPES = {
    "lodging",
    "hotel",
    "resort_hotel",
    "bed_and_breakfast",
    "hostel",
    "motel",
    "inn",
    "guest_house",
}


def is_actual_restaurant(place):
    """
    Google Places가 restaurant로 반환했더라도
    숙박시설 등 음식점이 아닌 장소가 섞이는 경우를 한 번 더 제외한다.
    """
    place_types = set(place.get("types", []) or [])
    primary_type = place.get("primaryType", "")

    if primary_type in NON_RESTAURANT_TYPES:
        return False

    if place_types.intersection(NON_RESTAURANT_TYPES):
        return False

    return True


# ======================================
# V44: 직접 음식 검색 결과의 식음료 장소 재검증
# ======================================

# 국가/메뉴별 *_restaurant 타입은 자동으로 허용하고,
# restaurant가 아닌 식음료 장소 중 실제로 방문 가능한 장소만
# 명시적으로 추가한다.
FOOD_SERVICE_PLACE_TYPES = {
    "restaurant",
    "cafe",
    "coffee_shop",
    "coffee_stand",
    "bakery",
    "bar",
    "pub",
    "wine_bar",
    "cocktail_bar",
    "sports_bar",
    "lounge_bar",
    "beer_garden",
    "brewpub",
    "food_court",
    "dessert_restaurant",
    "dessert_shop",
    "ice_cream_shop",
    "cake_shop",
    "donut_shop",
    "pastry_shop",
    "tea_house",
    "juice_shop",
    "snack_bar",
    "deli",
    "sandwich_shop",
    "hot_dog_stand",
    "confectionery",
    "meal_delivery",
    "meal_takeaway",
    "pizza_delivery",
}


def is_food_service_place(place):
    """
    Text Search 결과가 실제로 먹거나 마시러 갈 수 있는 장소인지
    primaryType + types로 한 번 더 적극적으로 확인한다.

    - *_restaurant 계열이면 통과
    - restaurant / cafe / bakery / bar 등 식음료 타입이면 통과
    - store, supermarket 등만 있는 결과는 통과시키지 않는다.

    이 함수는 '피자인가?' 같은 메뉴 판별을 다시 하는 함수가 아니다.
    메뉴 관련성은 Google Text Search가 담당하고,
    여기서는 '실제 식음료 장소인가?'만 검증한다.
    """
    place_types = set(
        place.get("types", []) or []
    )

    primary_type = place.get(
        "primaryType",
        ""
    )

    if primary_type:
        place_types.add(
            primary_type
        )

    if any(
        place_type.endswith(
            "_restaurant"
        )
        for place_type in place_types
    ):
        return True

    if place_types.intersection(
        FOOD_SERVICE_PLACE_TYPES
    ):
        return True

    return False



# ======================================
# V46: 직접 음식 검색 Nearby 보완 규칙
# ======================================
#
# Text Search 결과만 믿지 않고, 같은 반경의 Nearby Search 결과에서도
# 입력 메뉴와 맞는 식당을 한 번 더 찾아낸다.
#
# 판별 근거:
# 1. Google primaryType / types
# 2. 식당 상호명
# 3. 대표 프랜차이즈 이름
#
# 리뷰/메뉴 텍스트는 사용하지 않는다.


# Google Places Table A의 필터 가능한 실제 타입을 사용한다.
#
# strong_types:
#   타입 자체만으로 입력 메뉴와 강하게 일치한다고 판단 가능.
#
# discovery_types:
#   후보 발견에는 유용하지만 타입 하나만으로 메뉴를 확정하지 않는다.
#   상호명/프랜차이즈/strong type을 다시 확인한 뒤에만 통과.
CUSTOM_QUERY_GOOGLE_TYPE_PLANS = {
    "피자": {
        "aliases": ["피자", "pizza"],
        "strong_types": {
            "pizza_restaurant",
            "pizza_delivery",
        },
        "discovery_types": {
            "chicken_restaurant",
            "chicken_wings_restaurant",
        },
    },
    "초밥": {
        "aliases": ["초밥", "스시", "sushi"],
        "strong_types": {"sushi_restaurant"},
        "discovery_types": {"japanese_restaurant"},
    },
    "스시": {
        "aliases": ["스시", "초밥", "sushi"],
        "strong_types": {"sushi_restaurant"},
        "discovery_types": {"japanese_restaurant"},
    },
    "라멘": {
        "aliases": ["라멘", "ramen"],
        "strong_types": {"ramen_restaurant"},
        "discovery_types": {"noodle_shop", "japanese_restaurant"},
    },
    "돈까스": {
        "aliases": ["돈까스", "돈카츠", "카츠", "tonkatsu"],
        "strong_types": {"tonkatsu_restaurant"},
        "discovery_types": {"japanese_restaurant"},
    },
    "돈카츠": {
        "aliases": ["돈카츠", "돈까스", "카츠", "tonkatsu"],
        "strong_types": {"tonkatsu_restaurant"},
        "discovery_types": {"japanese_restaurant"},
    },
    "스테이크": {
        "aliases": ["스테이크", "steak"],
        "strong_types": {"steak_house"},
        "discovery_types": {"american_restaurant", "western_restaurant"},
    },
    "햄버거": {
        "aliases": ["햄버거", "버거", "burger"],
        "strong_types": {"hamburger_restaurant"},
        "discovery_types": {"fast_food_restaurant"},
    },
    "버거": {
        "aliases": ["버거", "햄버거", "burger"],
        "strong_types": {"hamburger_restaurant"},
        "discovery_types": {"fast_food_restaurant"},
    },
    "타코": {
        "aliases": ["타코", "taco"],
        "strong_types": {"taco_restaurant"},
        "discovery_types": {"mexican_restaurant", "tex_mex_restaurant"},
    },
    "딤섬": {
        "aliases": ["딤섬", "dim sum", "dimsum"],
        "strong_types": {"dim_sum_restaurant"},
        "discovery_types": {"chinese_restaurant"},
    },
    "만두": {
        "aliases": ["만두", "dumpling"],
        "strong_types": {"dumpling_restaurant"},
        "discovery_types": set(),
    },
    "샌드위치": {
        "aliases": ["샌드위치", "sandwich"],
        "strong_types": {"sandwich_shop"},
        "discovery_types": {"deli"},
    },
    "핫도그": {
        "aliases": ["핫도그", "hotdog", "hot dog"],
        "strong_types": {"hot_dog_restaurant", "hot_dog_stand"},
        "discovery_types": {"fast_food_restaurant"},
    },
    "샐러드": {
        "aliases": ["샐러드", "salad"],
        "strong_types": {"salad_shop"},
        "discovery_types": set(),
    },
    "도넛": {
        "aliases": ["도넛", "도너츠", "donut"],
        "strong_types": {"donut_shop"},
        "discovery_types": {"bakery", "dessert_shop"},
    },
    "베이글": {
        "aliases": ["베이글", "bagel"],
        "strong_types": {"bagel_shop"},
        "discovery_types": {"bakery"},
    },
    "케이크": {
        "aliases": ["케이크", "cake"],
        "strong_types": {"cake_shop"},
        "discovery_types": {"dessert_shop", "bakery"},
    },
    "커피": {
        "aliases": ["커피", "coffee"],
        "strong_types": {"coffee_shop", "coffee_stand"},
        "discovery_types": {"cafe", "coffee_roastery"},
    },
    "파스타": {
        "aliases": ["파스타", "pasta"],
        "strong_types": set(),
        "discovery_types": {"italian_restaurant"},
    },
    "쌀국수": {
        "aliases": ["쌀국수", "pho"],
        "strong_types": set(),
        "discovery_types": {"vietnamese_restaurant", "noodle_shop"},
    },
    "마라탕": {
        "aliases": ["마라탕", "마라"],
        "strong_types": set(),
        "discovery_types": {"hot_pot_restaurant", "chinese_restaurant"},
    },
    "샤브샤브": {
        "aliases": ["샤브샤브", "샤브", "shabu"],
        "strong_types": set(),
        "discovery_types": {"hot_pot_restaurant"},
    },
    "카레": {
        "aliases": ["카레", "커리", "curry"],
        "strong_types": {"japanese_curry_restaurant"},
        "discovery_types": {"indian_restaurant"},
    },
    "짜장면": {
        "aliases": ["짜장면", "짜장", "자장면"],
        "strong_types": set(),
        "discovery_types": {"chinese_noodle_restaurant", "chinese_restaurant"},
    },
    "짬뽕": {
        "aliases": ["짬뽕"],
        "strong_types": set(),
        "discovery_types": {"chinese_noodle_restaurant", "chinese_restaurant"},
    },
    "우동": {
        "aliases": ["우동", "udon"],
        "strong_types": set(),
        "discovery_types": {"noodle_shop", "japanese_restaurant"},
    },
    "회": {
        "aliases": ["회", "횟집", "sashimi"],
        "strong_types": set(),
        "discovery_types": {
            "seafood_restaurant",
            "sushi_restaurant",
            "japanese_restaurant",
        },
    },
    "빙수": {
        "aliases": ["빙수"],
        "strong_types": set(),
        "discovery_types": {
            "dessert_restaurant",
            "dessert_shop",
            "ice_cream_shop",
        },
    },
}


# V56: 제과·간식 직접검색용 Google 타입 보완
CUSTOM_QUERY_GOOGLE_TYPE_PLANS.update(
    {
        "호두과자": {
            "aliases": [
                "호두과자",
                "호두",
            ],
            "strong_types": set(),
            "discovery_types": {
                "bakery",
                "dessert_shop",
            },
        },

        "탕후루": {
            "aliases": [
                "탕후루",
            ],
            "strong_types": set(),
            "discovery_types": {
                "dessert_shop",
                "confectionery",
            },
        },

        "요거트아이스크림": {
            "aliases": [
                "요거트아이스크림",
                "요거트 아이스크림",
                "요아정",
            ],
            "strong_types": set(),
            "discovery_types": {
                "ice_cream_shop",
                "dessert_shop",
            },
        },
    }
)



CUSTOM_QUERY_RULES = {
    "피자": {
        "aliases": [
            "피자",
            "pizza",
        ],
        "types": {
            "pizza_restaurant",
        },
        "brands": [
            "피자나라치킨공주",
            "피나치공",
            "도미노피자",
            "피자헛",
            "미스터피자",
            "파파존스",
            "피자스쿨",
            "피자마루",
            "피자에땅",
            "반올림피자샵",
            "반올림피자",
            "청년피자",
            "피자알볼로",
            "고피자",
            "프레드피자",
            "노모어피자",
            "빅스타피자",
            "7번가피자",
            "유로코피자",
            "오구쌀피자",
            "피자헤븐",
            "피자빙고",
            "난타5000피자",
            "뽕뜨락피자",
            "피자2001",
            "피자캣",
            "굽네치킨",
            "피자와치킨의러브레터",
            "피치월드",
        ],
    },

    "초밥": {
        "aliases": [
            "초밥",
            "스시",
            "sushi",
        ],
        "types": {
            "sushi_restaurant",
        },
        "brands": [
            "미카도스시",
            "스시로",
            "갓덴스시",
            "은행골",
            "스시웨이",
            "초밥대통령",
            "스시메이진",
            "무모한초밥",
            "만타스시31",
            "여부초밥",
            "로봇초밥마켓",
            "스시화",
            "회가대표초밥24",
        ],
    },

    "스시": {
        "aliases": [
            "스시",
            "초밥",
            "sushi",
        ],
        "types": {
            "sushi_restaurant",
        },
        "brands": [],
    },

    "라멘": {
        "aliases": [
            "라멘",
            "ramen",
        ],
        "types": {
            "ramen_restaurant",
        },
        "brands": [
            "이찌방라멘",
            "라멘선생",
            "큐슈울트라아멘",
            "멘야산다이메",
            "멘야하나비",
            "코이라멘",
        ],
    },

    "돈까스": {
        "aliases": [
            "돈까스",
            "돈카츠",
            "카츠",
            "tonkatsu",
        ],
        "types": {
            "tonkatsu_restaurant",
        },
        "brands": [
            "사보텐",
            "무공돈까스",
            "박용채의대박터진돈까스",
            "배터지는생동까스",
            "카츠백",
            "남바완돈카츠",
            "원카츠",
            "가츠몽",
            "구름카츠",
            "정돈",
        ],
    },

    "돈카츠": {
        "aliases": [
            "돈카츠",
            "돈까스",
            "카츠",
            "tonkatsu",
        ],
        "types": {
            "tonkatsu_restaurant",
        },
        "brands": [],
    },

    "파스타": {
        "aliases": [
            "파스타",
            "pasta",
        ],
        # 이탈리안 식당은 파스타를 대표 메뉴로 취급하는 경우가 많아
        # Nearby 보완 후보로 허용한다.
        "types": {
            "italian_restaurant",
        },
        "brands": [
            "롤링파스타",
            "미태리",
            "도로시파스타",
            "파스타입니다",
            "파스타앤우",
            "파스타에반하다",
            "파스타예요",
            "제비파스타&리조또",
            "파스토보이",
            "파스타집이야",
            "덕수파스타",
            "파스타를부탁해",
            "파스타9900원",
            "봉대박스파게티",
            "신입파스타",
            "파스타왔어요",
            "파스타부오노바",
            "파스타어때",
            "착한파스타",
            "와르르파스타",
            "파스타제작소",
            "파스타치요",
            "점보파스타",
            "괴짜쉐프파스타",
        ],
    },

    "스테이크": {
        "aliases": [
            "스테이크",
            "steak",
        ],
        "types": {
            "steak_house",
        },
        "brands": [
            "아웃백",
            "스테이크존",
            "스탠딩스테이크",
            "뉴욕스테이크",
        ],
    },

    "햄버거": {
        "aliases": [
            "햄버거",
            "버거",
            "burger",
        ],
        "types": {
            "hamburger_restaurant",
        },
        "brands": [
            "롯데리아",
            "버거킹",
            "맥도날드",
            "맘스터치",
            "프랭크버거",
            "노브랜드버거",
            "버거리",
            "왓더버거",
            "쉐이크쉑",
            "쉑쉑",
            "뉴욕버거",
            "버거앤프라이즈",
            "크라이치즈버거",
            "버거스올마이티",
            "바스버거",
            "힘난다버거",
            "오지버거",
            "버거운버거",
        ],
    },

    "버거": {
        "aliases": [
            "버거",
            "햄버거",
            "burger",
        ],
        "types": {
            "hamburger_restaurant",
        },
        "brands": [],
    },

    "커피": {
        "aliases": [
            "커피",
            "coffee",
        ],
        "types": {
            "coffee_shop",
            "coffee_stand",
            "cafe",
        },
        "brands": [
            "메가엠지씨커피",
            "메가MGC커피",
            "컴포즈커피",
            "이디야커피",
            "빽다방",
            "투썸플레이스",
            "더벤티",
            "스타벅스",
            "커피빈",
            "폴바셋",
            "할리스",
            "엔제리너스",
            "탐앤탐스커피",
            "카페베네",
            "파스쿠찌",
        ],
    },

    "케이크": {
        "aliases": [
            "케이크",
            "cake",
        ],
        "types": {
            "cake_shop",
            "dessert_shop",
        },
        "brands": [],
    },

    "빙수": {
        "aliases": [
            "빙수",
        ],
        "types": set(),
        "brands": [
            "설빙",
        ],
    },

    "도넛": {
        "aliases": [
            "도넛",
            "도너츠",
            "donut",
        ],
        "types": {
            "donut_shop",
        },
        "brands": [
            "던킨",
            "크리스피크림",
        ],
    },

    "쌀국수": {
        "aliases": [
            "쌀국수",
            "pho",
        ],
        "types": {
            "vietnamese_restaurant",
        },
        "brands": [
            "미분당",
            "미스사이공",
            "홍대쌀국수",
            "월미당",
            "베트남노상식당",
            "사이공본가",
            "하노이별",
            "에머이",
            "메콩타이",
            "포메인",
            "포베이",
            "호아빈",
            "포몬스",
            "퍼틴",
            "땀땀",
        ],
    },

    "마라탕": {
        "aliases": [
            "마라탕",
            "마라",
        ],
        # chinese_restaurant 전체를 통과시키면 짜장/짬뽕집이 너무 많이
        # 섞일 수 있으므로 타입만으로는 확정하지 않는다.
        "types": set(),
        "brands": [
            "탕화쿵푸마라탕",
            "라화쿵부",
            "춘리마라탕",
            "손오공마라탕",
            "마유유마라탕",
            "마라영웅",
            "마라연구소",
            "마라대국",
            "마라천국",
            "마라신",
            "마라퀸",
            "마라민족",
            "마라선생",
            "마라왕",
            "마라미방",
            "마라공주",
            "마라대장",
            "마라시대",
            "마라명가",
            "마라반점",
        ],
    },
}


# ======================================
# V55: 직접 메뉴 검색용 프랜차이즈 rescue 확대
# ======================================

V55_CUSTOM_QUERY_BRAND_ADDITIONS = {
    "피자": [
        "오구피자",
        "파파존스피자",
        "빽보이피자",
        "피자스톰",
        "자가제빵 선명희피자",
        "서오릉피자",
        "피자파는집",
        "피자와썹",
        "번쩍피자",
        "PJ피자",
        "피자는 치즈빨",
        "윤검푸드 봉수아피자",
    ],

    "햄버거": [
        "움버거앤윙스",
        "KFC",
        "세븐패티버거",
        "빌리언박스",
    ],

    "커피": [
        "백억커피",
        "카페프리헷",
        "봉명동내커피",
    ],

    "쌀국수": [
        "까몬",
        "오유미당",
        "포트리스",
        "꾸아",
        "반포식스",
        "포슈아",
        "반미362",
        "리틀하노이",
        "포 시애틀",
    ],

    "마라탕": [
        "소림마라",
        "라홍방 마라탕",
        "라쿵푸마라탕",
        "마라공방",
        "찐하오 마라탕",
        "라사천마라탕",
        "홍탕",
        "마라순코우",
        "야미마라탕",
        "미미관마라탕",
        "신룽푸마라탕",
        "샹츠마라",
        "라와",
        "요하마라21",
    ],
}


def _merge_v55_custom_query_brands():
    for query, additions in V55_CUSTOM_QUERY_BRAND_ADDITIONS.items():
        rule = CUSTOM_QUERY_RULES.get(
            query
        )

        if not rule:
            continue

        brands = rule.setdefault(
            "brands",
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )
            for brand in brands
        }

        for brand in additions:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in normalized_existing:
                continue

            brands.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_v55_custom_query_brands()


# ======================================
# V56: 신규 프랜차이즈 직접검색 rescue
# ======================================

V56_CUSTOM_QUERY_BRAND_ADDITIONS = {
    "커피": [
        "THE LITER",
        "THE LITER 24",
        "더리터24",
        "PORT CAN COFFEE",
        "COFFEE COOK",
        "파란만잔",
        "카페보스",
        "CAFE BOSS",
        "와드커피",
        "WAD COFFEE",
        "고더커피",
        "더웨이닝커피",
        "해쉬커피",
        "라바게트",
        "카페루앤비",
        "반달커피",
        "CAFE CANBUS",
        "카페캔버스",
        "NiceCaffeinClub",
        "NCC",
    ],

    "도넛": [
        "던킨",
        "던킨도너츠",
        "크리스피크림",
        "아이엠도넛",
        "IamDonut",
    ],

    "파스타": [
        "파스타도 식사다",
    ],
}


def _merge_v56_custom_query_brands():
    for query, additions in V56_CUSTOM_QUERY_BRAND_ADDITIONS.items():
        rule = CUSTOM_QUERY_RULES.get(
            query
        )

        if not rule:
            continue

        brands = rule.setdefault(
            "brands",
            []
        )

        normalized_existing = {
            re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~/]+",
                "",
                str(brand).lower()
            )
            for brand in brands
        }

        for brand in additions:
            normalized = re.sub(
                r"[\s\-_.,()\[\]{}'\"·ㆍ&~/]+",
                "",
                str(brand).lower()
            )

            if not normalized:
                continue

            if normalized in normalized_existing:
                continue

            brands.append(
                brand
            )

            normalized_existing.add(
                normalized
            )


_merge_v56_custom_query_brands()


# "버거" 검색도 "햄버거"와 같은 프랜차이즈 rescue 목록을 사용한다.
if (
    "버거" in CUSTOM_QUERY_RULES
    and "햄버거" in CUSTOM_QUERY_RULES
):
    CUSTOM_QUERY_RULES[
        "버거"
    ][
        "brands"
    ] = list(
        CUSTOM_QUERY_RULES[
            "햄버거"
        ].get(
            "brands",
            []
        )
    )



# ======================================
# V56: 직접 메뉴 별칭 규칙 추가
# ======================================

CUSTOM_QUERY_RULES.setdefault(
    "샌드위치",
    {
        "aliases": [
            "샌드위치",
            "sandwich",
        ],
        "types": {
            "sandwich_shop",
        },
        "brands": [
            "홍루이젠",
            "서브웨이",
            "퀴즈노스",
            "퀴즈노스서브",
            "죠샌드위치",
        ],
    }
)

CUSTOM_QUERY_RULES.setdefault(
    "핫도그",
    {
        "aliases": [
            "핫도그",
            "hotdog",
            "hot dog",
        ],
        "types": {
            "hot_dog_restaurant",
            "hot_dog_stand",
        },
        "brands": [
            "명랑핫도그",
            "명랑시대쌀핫도그",
            "스테프핫도그",
        ],
    }
)

CUSTOM_QUERY_RULES.setdefault(
    "호두과자",
    {
        "aliases": [
            "호두과자",
            "호두",
        ],
        "types": set(),
        "brands": [
            "코코호도",
            "복호두",
            "호두당",
            "호밀호두",
        ],
    }
)

CUSTOM_QUERY_RULES.setdefault(
    "탕후루",
    {
        "aliases": [
            "탕후루",
        ],
        "types": set(),
        "brands": [
            "달콤왕가탕후루",
        ],
    }
)

CUSTOM_QUERY_RULES.setdefault(
    "요거트아이스크림",
    {
        "aliases": [
            "요거트아이스크림",
            "요거트 아이스크림",
            "요아정",
        ],
        "types": {
            "ice_cream_shop",
        },
        "brands": [
            "카페요아정",
            "요거트아이스크림의 정석",
            "달롱도르요거트아이스크림",
        ],
    }
)



def normalize_custom_query_text(text):
    """
    직접 검색어/상호명 비교용 정규화.
    한글/영문/숫자는 유지하고 공백과 기호만 제거한다.
    """
    if not text:
        return ""

    return re.sub(
        r"[\s\-_.,()\[\]{}'\"·ㆍ&~]+",
        "",
        str(text).lower()
    )


def _find_query_key(query, mapping):
    normalized_query = normalize_custom_query_text(
        query
    )

    if not normalized_query:
        return None

    for key in sorted(
        mapping.keys(),
        key=len,
        reverse=True
    ):
        normalized_key = normalize_custom_query_text(
            key
        )

        if (
            normalized_query == normalized_key
            or normalized_key in normalized_query
        ):
            return key

    return None


def get_custom_query_google_type_plan(query):
    key = _find_query_key(
        query,
        CUSTOM_QUERY_GOOGLE_TYPE_PLANS
    )

    if key is None:
        return None

    return CUSTOM_QUERY_GOOGLE_TYPE_PLANS[
        key
    ]


def get_custom_query_rule(query):
    """
    '화덕피자', '돈까스 맛집'처럼 조금 길게 입력해도
    알려진 핵심 메뉴 규칙을 찾아준다.
    """
    key = _find_query_key(
        query,
        CUSTOM_QUERY_RULES
    )

    if key is None:
        return None

    return CUSTOM_QUERY_RULES[
        key
    ]


def matches_custom_query_locally(place, query):
    """
    Nearby Search 결과가 사용자의 직접 메뉴 검색과 관련 있는지
    Google 타입 + 상호명 + 프랜차이즈 이름으로 확인한다.

    strong type은 타입 자체만으로 통과.
    discovery type은 후보 발견에만 사용하고,
    그것만으로는 메뉴가 맞다고 확정하지 않는다.
    """
    normalized_query = normalize_custom_query_text(
        query
    )

    if not normalized_query:
        return False

    place_name = get_place_name(
        place
    )

    normalized_name = normalize_custom_query_text(
        place_name
    )

    # 1. 입력 문자열이 상호명에 직접 포함
    if (
        len(normalized_query) >= 2
        and normalized_query in normalized_name
    ):
        return True

    rule = get_custom_query_rule(
        query
    )

    type_plan = get_custom_query_google_type_plan(
        query
    )

    # 2. 동의어/영문 표현이 상호명에 포함
    aliases = []

    if rule:
        aliases.extend(
            rule.get(
                "aliases",
                []
            )
        )

    if type_plan:
        aliases.extend(
            type_plan.get(
                "aliases",
                []
            )
        )

    for alias in aliases:
        normalized_alias = normalize_custom_query_text(
            alias
        )

        if (
            len(normalized_alias) >= 2
            and normalized_alias in normalized_name
        ):
            return True

    # 3. strong Google Place Type
    place_types = set(
        place.get(
            "types",
            []
        ) or []
    )

    primary_type = place.get(
        "primaryType",
        ""
    )

    if primary_type:
        place_types.add(
            primary_type
        )

    strong_types = set()

    if rule:
        strong_types.update(
            rule.get(
                "types",
                set()
            )
        )

    if type_plan:
        strong_types.update(
            type_plan.get(
                "strong_types",
                set()
            )
        )

    if place_types.intersection(
        strong_types
    ):
        return True

    # 4. 프랜차이즈 이름
    brands = (
        rule.get(
            "brands",
            []
        )
        if rule
        else []
    )

    for brand in brands:
        normalized_brand = normalize_custom_query_text(
            brand
        )

        if not normalized_brand:
            continue

        if (
            normalized_name == normalized_brand
            or normalized_name.startswith(
                normalized_brand
            )
            or (
                len(normalized_brand) >= 5
                and normalized_brand in normalized_name
            )
        ):
            return True

    return False


# ======================================
# V67: 맛 중심 객관식 100점 추천 점수
# ======================================
#
# 최종 추천 점수 = 100점
#
# Google 평점: 최대 40점
# 리뷰 분석: 최대 60점
#
# 리뷰 60점 배점:
# - 맛: 30점
# - 가격/가성비: 6점
# - 서비스: 6점
# - 분위기: 6점
# - 웨이팅: 6점
# - 청결: 6점
#
# 각 리뷰 항목 점수:
# - 아래 리뷰 종합 분석 대시보드의 0~100 감정 점수를 그대로 사용한다.
# - 항목 점수 = 리뷰 감정 점수 / 100 × 해당 항목 만점
# - 언급이 전혀 없으면 리뷰 감정 점수를 50점(중립)으로 취급한다.
#   · 맛: 15/30점
#   · 나머지 항목: 3/6점
#
# 따라서 화면에 보이는 리뷰 감정 점수와 최종 추천점수에 들어가는
# 항목 점수가 서로 다른 계산을 사용하는 일이 없다.
#
# V68에서는 카드 점수, 상세 점수표, 리뷰 대시보드가 모두
# get_review_sentiment_score()를 동일한 기준으로 사용한다.

SCORE_FORMULA_VERSION = "V72 · Google40(review-confidence) + DashboardSentiment"

SCORE_REVIEW_CATEGORIES = [
    "맛",
    "가격/가성비",
    "서비스",
    "분위기",
    "웨이팅",
    "청결",
]

REVIEW_CATEGORY_MAX_POINTS = {
    "맛": 30.0,
    "가격/가성비": 6.0,
    "서비스": 6.0,
    "분위기": 6.0,
    "웨이팅": 6.0,
    "청결": 6.0,
}


def get_review_category_points(category_scores):
    """
    리뷰 대시보드에 표시되는 0~100 감정 점수를
    최종 추천점수에도 그대로 사용한다.

    예:
    - 맛 77.3/100 -> 77.3% × 30 = 23.2/30
    - 서비스 56.5/100 -> 56.5% × 6 = 3.4/6
    - 정보 없음 -> 50/100 -> 해당 항목 만점의 절반

    이렇게 해서 화면의 리뷰 점수와 추천점수 계산이
    반드시 같은 기준을 사용한다.
    """
    category_scores = category_scores or {}
    points = {}
    sentiment_scores = {}

    for category in SCORE_REVIEW_CATEGORIES:
        data = category_scores.get(category, {}) or {}
        max_point = REVIEW_CATEGORY_MAX_POINTS[category]

        try:
            positive = max(0.0, float(data.get("positive", 0) or 0))
        except (TypeError, ValueError):
            positive = 0.0

        try:
            negative = max(0.0, float(data.get("negative", 0) or 0))
        except (TypeError, ValueError):
            negative = 0.0

        # 리뷰 대시보드와 완전히 동일한 함수/공식을 사용한다.
        sentiment_score = get_review_sentiment_score({
            "positive_score": positive,
            "negative_score": negative,
        })

        # 대시보드의 '정보 없음'은 추천점수에서 50점 중립으로 처리한다.
        if sentiment_score is None:
            effective_sentiment_score = 50.0
        else:
            effective_sentiment_score = float(sentiment_score)

        category_point = (
            effective_sentiment_score
            / 100.0
            * max_point
        )

        sentiment_scores[category] = (
            None if sentiment_score is None
            else round(float(sentiment_score), 1)
        )

        points[category] = round(
            max(0.0, min(max_point, category_point)),
            1
        )

    return points, sentiment_scores


# Google 평점은 평가 수가 너무 적을 때 과신하지 않는다.
# 단, 리뷰가 100개 이상이면 신뢰도 보정을 100%로 두어
# Google 5.0 + 모든 리뷰 카테고리 완벽일 때 100점이 가능하다.
GOOGLE_REVIEW_TRUST_FULL_COUNT = 100
GOOGLE_REVIEW_TRUST_FLOOR = 0.90


def get_google_review_confidence(google_review_count):
    """
    Google 전체 평가 수에 따른 평점 신뢰도 계수.

    - 평가 수가 적어도 Google 평점 비중을 지나치게 깎지 않도록
      최소 90%는 유지한다.
    - 로그 스케일을 사용해 초반 평가 수 증가를 의미 있게 반영한다.
    - 100개 이상이면 1.0으로 고정한다.
    """
    try:
        count = max(0.0, float(google_review_count or 0))
    except (TypeError, ValueError):
        count = 0.0

    if count >= GOOGLE_REVIEW_TRUST_FULL_COUNT:
        return 1.0

    progress = math.log1p(count) / math.log1p(
        GOOGLE_REVIEW_TRUST_FULL_COUNT
    )
    progress = max(0.0, min(1.0, progress))

    return (
        GOOGLE_REVIEW_TRUST_FLOOR
        + (1.0 - GOOGLE_REVIEW_TRUST_FLOOR) * progress
    )


def get_recommendation_score_breakdown(
    google_rating,
    category_scores,
    google_review_count=0,
):
    """
    최종 추천점수를 계산하는 단 하나의 함수.

    Google 평점 40점에는 전체 평가 수에 따른 완만한 신뢰도 보정을
    적용하고, 리뷰 카테고리 60점은 화면의 감정 점수와 동일한 값을 쓴다.
    """
    if google_rating is None:
        return None

    try:
        rating = float(google_rating)
    except (TypeError, ValueError):
        return None

    rating = max(0.0, min(5.0, rating))

    google_base_points = rating / 5.0 * 40.0
    google_review_confidence = get_google_review_confidence(
        google_review_count
    )
    google_points = round(
        google_base_points * google_review_confidence,
        1
    )

    review_points, sentiment_scores = get_review_category_points(
        category_scores
    )
    review_total = round(sum(review_points.values()), 1)
    total = round(google_points + review_total, 1)
    total = max(0.0, min(100.0, total))

    return {
        "version": SCORE_FORMULA_VERSION,
        "google": google_points,
        "google_base": round(google_base_points, 1),
        "google_review_confidence": round(
            google_review_confidence,
            4
        ),
        "categories": review_points,
        "sentiment_scores": sentiment_scores,
        "review_total": review_total,
        "total": total,
    }


def calculate_recommendation_score(
    google_rating,
    category_scores,
    review_count,
    google_review_count=0,
    importance_levels=None
):
    """
    기존 호출부 호환용 래퍼. 실제 계산은
    get_recommendation_score_breakdown() 한 곳에서만 한다.
    """
    breakdown = get_recommendation_score_breakdown(
        google_rating,
        category_scores,
        google_review_count=google_review_count,
    )

    if breakdown is None:
        return None

    return breakdown["total"]


# ======================================
# 화면 - V73 소프트 파스텔 카페 UI
# ======================================

# 전체 스타일
st.markdown(
    """
    <style>
    :root {
        --page-bg-1: #F8F8FD;
        --page-bg-2: #F3F8FB;
        --page-bg-3: #F6FAF7;

        --surface: rgba(255, 255, 255, 0.82);
        --surface-strong: rgba(255, 255, 255, 0.94);

        --lavender: #C8D3F5;
        --lavender-deep: #91A7E8;

        --sky: #C8E2EC;
        --sky-deep: #8FBFD0;

        --mint: #CDE8DE;
        --mint-deep: #8FC6B5;

        --border: #E2E7F1;
        --border-soft: #EBEEF5;

        --text-main: #3F4B61;
        --text-soft: #6D778A;
        --text-muted: #8992A3;
    }

    html,
    body,
    [data-testid="stAppViewContainer"],
    .stApp {
        background:
            radial-gradient(
                circle at 8% 8%,
                rgba(200, 211, 245, 0.34),
                transparent 24%
            ),
            radial-gradient(
                circle at 92% 18%,
                rgba(205, 232, 222, 0.30),
                transparent 25%
            ),
            linear-gradient(
                180deg,
                var(--page-bg-1) 0%,
                var(--page-bg-2) 50%,
                var(--page-bg-3) 100%
            );
        color: var(--text-main);
    }

    .block-container {
        max-width: 1080px;
        padding-top: 1.35rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* ------------------------------
       다크모드 가독성 보정
       ------------------------------ */

    /*
    앱 자체가 밝은 파스텔 배경을 사용하므로
    OS/Streamlit이 다크모드여도 본문 글자는
    어두운 색으로 명시해서 대비가 사라지지 않게 한다.
    */

    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"],
    [data-testid="stExpander"] summary,
    [data-baseweb="tab"],
    [data-baseweb="select"] *,
    [data-baseweb="input"] * {
        color: var(--text-main);
    }

    /* 설명/캡션은 살짝 연하게 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--text-soft) !important;
    }

    /* 입력창 placeholder */
    input::placeholder {
        color: #9AA4B5 !important;
        opacity: 1 !important;
    }

    /* text input 실제 입력값 */
    div[data-baseweb="input"] input {
        color: #46536A !important;
        caret-color: #6E82C4 !important;
    }

    /* selectbox 현재 선택값 */
    div[data-baseweb="select"] {
        color: #46536A !important;
    }

    div[data-baseweb="select"] > div {
        color: #46536A !important;
    }

    /* 팝오버/메뉴 내부도 밝은 카드 + 어두운 글자 */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        color: #46536A !important;
    }

    div[data-baseweb="popover"] * ,
    div[data-baseweb="menu"] * ,
    ul[role="listbox"] * {
        color: #46536A;
    }

    /* 체크박스 라벨 */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] p {
        color: #4E5B71 !important;
    }

    /* 슬라이더 라벨 / 값 / 눈금 */
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] p,
    [data-testid="stSlider"] span {
        color: #4E5B71;
    }

    /* expander 헤더 */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #4E5B71 !important;
        font-weight: 700;
    }

    /* 탭 */
    .stTabs [data-baseweb="tab"] {
        color: #647086 !important;
    }

    .stTabs [aria-selected="true"] {
        color: #4D62A4 !important;
        font-weight: 800;
    }

    /* 일반 secondary / link 버튼 */
    div[data-testid="stLinkButton"] a,
    div[data-testid="stLinkButton"] a *,
    div[data-testid="stPopover"] > button,
    div[data-testid="stPopover"] > button * {
        color: #56647B !important;
    }

    /* primary 버튼만 흰 글자 유지 */
    div.stButton > button[kind="primary"],
    div.stButton > button[kind="primary"] *,
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[kind="primary"]:hover * {
        color: #FFFFFF !important;
    }

    /* alert 내부 텍스트 */
    div[data-testid="stAlert"],
    div[data-testid="stAlert"] * {
        color: #4F5D72;
    }

    /* ------------------------------
       V61: 다크모드 대비 강화
       ------------------------------ */

    /*
    밝은 파스텔 UI에서는 글씨 굵기보다
    '배경과 글자의 명도 대비'가 더 중요하다.
    Streamlit 다크모드가 기본 위젯을 검게 만드는 것도
    아래에서 !important로 밝게 고정한다.
    */

    .stApp {
        color: #344158 !important;
    }

    /* 일반 본문 */
    .stApp p,
    .stApp li,
    .stApp label,
    [data-testid="stMarkdownContainer"] p {
        color: #465268 !important;
        font-weight: 540;
    }

    /* 위젯 이름: 위치, 음식, 맛, 가성비 등 */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] span {
        color: #3D495F !important;
        font-weight: 700 !important;
    }

    /* 설명/캡션: 너무 연하지 않게 */
    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p,
    .section-description {
        color: #687489 !important;
        font-weight: 560 !important;
    }

    .section-title {
        color: #344158 !important;
        font-weight: 850 !important;
    }

    .section-kicker {
        color: #687AB5 !important;
        font-weight: 850 !important;
    }

    /* --------------------------------
       입력창: 다크모드 검정 배경 제거
       -------------------------------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="input"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] {
        background-color: #FBFCFF !important;
        color: #354158 !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border: 1px solid #D5DDEA !important;
        box-shadow: 0 2px 7px rgba(73, 89, 123, 0.035) !important;
    }

    div[data-baseweb="input"] input {
        background-color: transparent !important;
        color: #354158 !important;
        font-weight: 620 !important;
        -webkit-text-fill-color: #354158 !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #7C879A !important;
        opacity: 1 !important;
        font-weight: 500 !important;
        -webkit-text-fill-color: #7C879A !important;
    }

    div[data-baseweb="select"] *,
    div[data-baseweb="select"] span {
        color: #354158 !important;
        font-weight: 620 !important;
        -webkit-text-fill-color: #354158 !important;
    }

    /* select 화살표 */
    div[data-baseweb="select"] svg {
        fill: #66738A !important;
        color: #66738A !important;
    }

    /* --------------------------------
       가격대 / 검색예시 팝오버 버튼
       -------------------------------- */

    div[data-testid="stPopover"] > button {
        background: #F6F8FD !important;
        border: 1px solid #D8E0ED !important;
        color: #46546B !important;
        box-shadow: 0 2px 7px rgba(73, 89, 123, 0.035) !important;
    }

    div[data-testid="stPopover"] > button *,
    div[data-testid="stPopover"] > button p,
    div[data-testid="stPopover"] > button span {
        color: #46546B !important;
        font-weight: 680 !important;
        -webkit-text-fill-color: #46546B !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background: #EEF2FA !important;
        border-color: #BCC9E0 !important;
    }

    /* 열려 있는 팝오버 / select 메뉴 */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background: #FCFDFF !important;
        color: #3F4C63 !important;
    }

    div[data-baseweb="popover"] *,
    div[data-baseweb="menu"] *,
    ul[role="listbox"] * {
        color: #3F4C63 !important;
    }

    /* --------------------------------
       슬라이더
       -------------------------------- */

    [data-testid="stSlider"] p,
    [data-testid="stSlider"] span {
        color: #435067 !important;
        font-weight: 650 !important;
    }

    /*
    Streamlit 버전에 따라 slider thumb/track 구조가 달라질 수 있어
    accent-color도 함께 지정한다.
    */
    [data-testid="stSlider"] {
        accent-color: #8FA5DE !important;
    }

    /* --------------------------------
       취향 칩
       -------------------------------- */

    .filter-chip {
        color: #48566F !important;
        font-weight: 760 !important;
        background: #EDF1FB !important;
        border-color: #D5DFF2 !important;
    }

    /* --------------------------------
       상세 탭 / expander
       -------------------------------- */

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #3F4D64 !important;
        font-weight: 720 !important;
    }

    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"] p {
        color: #59677D !important;
        font-weight: 650 !important;
    }

    .stTabs [aria-selected="true"],
    .stTabs [aria-selected="true"] p {
        color: #4E63A5 !important;
        font-weight: 800 !important;
    }

    /* --------------------------------
       링크 버튼
       -------------------------------- */

    div[data-testid="stLinkButton"] a,
    div[data-testid="stLinkButton"] a * {
        background: #F8FAFE !important;
        color: #46546B !important;
        font-weight: 670 !important;
    }

    /* primary 검색 버튼은 반대로 밝은 글씨 */
    div.stButton > button[kind="primary"],
    div.stButton > button[kind="primary"] *,
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: 800 !important;
    }

    /* ------------------------------
       상단 히어로
       ------------------------------ */

    .app-hero {
        background:
            radial-gradient(
                circle at 84% 20%,
                rgba(255, 255, 255, 0.55),
                transparent 29%
            ),
            linear-gradient(
                135deg,
                #CAD4F4 0%,
                #C9E0EC 52%,
                #CFE8DF 100%
            );
        border: 1px solid rgba(255, 255, 255, 0.72);
        border-radius: 26px;
        padding: 2.15rem 2.3rem;
        margin-bottom: 1.15rem;
        box-shadow:
            0 14px 36px rgba(94, 108, 145, 0.10),
            inset 0 1px 0 rgba(255, 255, 255, 0.56);
        color: #3C4B64;
    }

    .app-hero-badge {
        display: inline-block;
        padding: 0.32rem 0.72rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.48);
        border: 1px solid rgba(255, 255, 255, 0.72);
        color: #66728B;
        font-size: 0.79rem;
        font-weight: 800;
        letter-spacing: 0.025em;
        margin-bottom: 0.7rem;
    }

    .app-hero-title {
        font-size: clamp(2rem, 4vw, 3rem);
        line-height: 1.08;
        font-weight: 850;
        letter-spacing: -0.04em;
        margin: 0;
        color: #35435C;
    }

    .app-hero-subtitle {
        font-size: 1.03rem;
        line-height: 1.65;
        color: #5F6B80;
        margin-top: 0.75rem;
        margin-bottom: 0;
    }

    /* ------------------------------
       섹션
       ------------------------------ */

    .section-kicker {
        font-size: 0.76rem;
        font-weight: 850;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #8794BF;
        margin-bottom: 0.18rem;
    }

    .section-title {
        font-size: 1.28rem;
        font-weight: 820;
        letter-spacing: -0.025em;
        margin-bottom: 0.18rem;
        color: #404C63;
    }

    .section-description {
        font-size: 0.9rem;
        color: #788296;
        margin-bottom: 0.65rem;
    }

    /* ------------------------------
       카드 / 컨테이너
       ------------------------------ */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
        border: 1px solid var(--border);
        background: var(--surface);
        box-shadow:
            0 8px 25px rgba(88, 101, 132, 0.045),
            inset 0 1px 0 rgba(255, 255, 255, 0.72);
        backdrop-filter: blur(7px);
    }

    div[data-testid="stExpander"] {
        border-radius: 14px;
        overflow: hidden;
        border-color: var(--border-soft);
        background: rgba(255, 255, 255, 0.58);
    }

    /* ------------------------------
       입력 / 팝오버
       ------------------------------ */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.86);
        border-color: #E0E6F0;
        border-radius: 12px;
    }

    div[data-testid="stPopover"] > button {
        border-radius: 11px;
        font-size: 0.87rem;
        min-height: 2.25rem;
        padding-left: 0.78rem;
        padding-right: 0.78rem;
        background: rgba(255, 255, 255, 0.76);
        border-color: #DEE5F0;
        color: #5C687E;
    }

    div[data-testid="stPopover"] > button:hover {
        border-color: #C9D4EB;
        background: #F7F9FD;
    }

    /* ------------------------------
       취향 칩
       ------------------------------ */

    .filter-chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin: 0.58rem 0 0.1rem 0;
    }

    .filter-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.34rem 0.66rem;
        border-radius: 999px;
        background: #F0F3FC;
        border: 1px solid #DDE5F7;
        color: #596781;
        font-size: 0.82rem;
        font-weight: 750;
    }

    /* ------------------------------
       결과 카드
       ------------------------------ */

    .result-rank {
        display: inline-block;
        border-radius: 999px;
        padding: 0.29rem 0.64rem;
        font-size: 0.77rem;
        font-weight: 820;
        line-height: 1;
        color: #66728A;
        background: #EEF3FB;
        border: 1px solid #DCE5F4;
        margin-bottom: 0.25rem;
    }

    .winner-rank {
        background: linear-gradient(
            135deg,
            #BCCAF2 0%,
            #BFE1DC 100%
        );
        border: 1px solid rgba(255, 255, 255, 0.58);
        color: #44556D;
        box-shadow: 0 5px 15px rgba(106, 126, 164, 0.11);
    }

    .restaurant-name {
        font-size: 1.28rem;
        line-height: 1.28;
        font-weight: 850;
        letter-spacing: -0.03em;
        margin-top: 0.12rem;
        color: #3E4A60;
    }

    .winner-name {
        font-size: 1.58rem;
    }

    .score-badge {
        display: inline-flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        min-width: 94px;
        padding: 0.38rem 0;
    }

    .score-number {
        font-size: 1.65rem;
        line-height: 1;
        font-weight: 900;
        letter-spacing: -0.04em;
        color: #6277B8;
    }

    .score-label {
        font-size: 0.72rem;
        color: #8992A4;
        margin-top: 0.22rem;
        font-weight: 700;
    }

    .meta-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.55rem;
        margin-top: 0.75rem;
    }

    .meta-item {
        border-radius: 13px;
        padding: 0.64rem 0.72rem;
        background: #F5F7FC;
        border: 1px solid #E9EDF5;
        min-width: 0;
    }

    .meta-label {
        font-size: 0.69rem;
        color: #8A94A5;
        margin-bottom: 0.18rem;
        font-weight: 760;
    }

    .meta-value {
        font-size: 0.91rem;
        font-weight: 800;
        color: #505D73;
        line-height: 1.25;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .address-line {
        margin-top: 0.68rem;
        font-size: 0.83rem;
        color: #7C8698;
        line-height: 1.45;
    }

    .results-heading {
        margin-top: 1.7rem;
        margin-bottom: 0.7rem;
    }

    .results-heading-title {
        font-size: 1.55rem;
        font-weight: 850;
        letter-spacing: -0.035em;
        margin-bottom: 0.22rem;
        color: #3E4A61;
    }

    .results-heading-subtitle {
        font-size: 0.9rem;
        color: #7A8496;
    }

    .detail-summary {
        padding: 0.75rem 0.88rem;
        border-radius: 13px;
        background: linear-gradient(
            135deg,
            #F2F5FD 0%,
            #F1F8F6 100%
        );
        border: 1px solid #E3EAF2;
        margin-bottom: 0.75rem;
        line-height: 1.65;
        color: #566278;
    }

    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        width: 100%;
    }

    .result-title-wrap {
        flex: 1 1 auto;
        min-width: 0;
    }

    .review-card-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.65rem;
        flex-wrap: wrap;
        margin-bottom: 0.15rem;
    }

    .review-card-title,
    .review-card-status {
        font-weight: 800;
        color: #4C5970;
    }

    .review-card-status {
        font-size: 0.86rem;
    }

    /* ------------------------------
       버튼
       ------------------------------ */

    div.stButton > button[kind="primary"] {
        border-radius: 14px;
        min-height: 3rem;
        font-weight: 800;
        font-size: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.52);
        color: white;
        background: linear-gradient(
            135deg,
            #95A8E4 0%,
            #91C5C1 100%
        );
        box-shadow: 0 8px 20px rgba(94, 114, 152, 0.12);
    }

    div.stButton > button[kind="primary"]:hover {
        border-color: rgba(255, 255, 255, 0.70);
        color: white;
        filter: brightness(1.025);
        box-shadow: 0 9px 22px rgba(94, 114, 152, 0.15);
    }

    div[data-testid="stLinkButton"] a {
        border-radius: 12px;
        border-color: #D9E2EF;
        background: rgba(255, 255, 255, 0.72);
    }

    /* ------------------------------
       탭
       ------------------------------ */

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        padding: 0.22rem;
        border-radius: 12px;
        background: #F3F6FB;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 9px;
        padding-left: 0.85rem;
        padding-right: 0.85rem;
    }

    /* ------------------------------
       알림 박스
       ------------------------------ */

    div[data-testid="stAlert"] {
        border-radius: 13px;
        border-color: #DDE6F0;
    }

    /* ------------------------------
       모바일
       ------------------------------ */

    @media (max-width: 700px) {
        .block-container {
            padding-left: 0.8rem;
            padding-right: 0.8rem;
            padding-top: 0.8rem;
        }

        .app-hero {
            padding: 1.55rem 1.35rem;
            border-radius: 21px;
        }

        .meta-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .winner-name {
            font-size: 1.36rem;
        }

        div[data-testid="stPopover"] > button {
            min-height: 2.35rem;
            font-size: 0.84rem;
        }
    }

    /* ======================================================
       V62 FINAL OVERRIDES
       다크모드에서도 검색 위젯이 검게 남지 않도록
       스타일 블록의 가장 마지막에서 강제로 덮어쓴다.
       ====================================================== */

    /* 위치 입력창 전체 */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="input"] > div,
    div[data-testid="stTextInput"] input {
        background: #F9FAFE !important;
        background-color: #F9FAFE !important;
        color: #344158 !important;
        -webkit-text-fill-color: #344158 !important;
        border-color: #D9E1EE !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 1px solid #D9E1EE !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 10px rgba(77, 92, 126, 0.045) !important;
    }

    div[data-testid="stTextInput"] input::placeholder {
        color: #8A95A8 !important;
        -webkit-text-fill-color: #8A95A8 !important;
        opacity: 1 !important;
    }

    /* 음식 선택 selectbox 전체 */
    div[data-testid="stSelectbox"] div[data-baseweb="select"],
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] div[role="combobox"] {
        background: #F9FAFE !important;
        background-color: #F9FAFE !important;
        color: #344158 !important;
        -webkit-text-fill-color: #344158 !important;
        border-color: #D9E1EE !important;
    }

    div[data-testid="stSelectbox"] div[role="combobox"] {
        border: 1px solid #D9E1EE !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 10px rgba(77, 92, 126, 0.045) !important;
    }

    div[data-testid="stSelectbox"] span,
    div[data-testid="stSelectbox"] p {
        color: #344158 !important;
        -webkit-text-fill-color: #344158 !important;
        font-weight: 650 !important;
    }

    div[data-testid="stSelectbox"] svg {
        color: #6C7890 !important;
        fill: #6C7890 !important;
    }

    /* 가격대 / 검색 예시 버튼 */
    div[data-testid="stPopover"] > button {
        background: linear-gradient(
            135deg,
            #F5F7FD 0%,
            #F3F8F8 100%
        ) !important;
        background-color: #F5F7FD !important;
        border: 1px solid #D8E1EE !important;
        color: #4B5870 !important;
        box-shadow: 0 3px 10px rgba(77, 92, 126, 0.04) !important;
    }

    div[data-testid="stPopover"] > button:hover {
        background: #EEF3FA !important;
        border-color: #C6D2E5 !important;
    }

    div[data-testid="stPopover"] > button *,
    div[data-testid="stPopover"] > button p,
    div[data-testid="stPopover"] > button span {
        color: #4B5870 !important;
        -webkit-text-fill-color: #4B5870 !important;
        font-weight: 700 !important;
    }

    /* select / popover가 열렸을 때 메뉴도 밝게 */
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    ul[role="listbox"],
    ul[role="listbox"] li {
        background-color: #FCFDFF !important;
        color: #3E4B62 !important;
    }

    ul[role="listbox"] li:hover {
        background-color: #EEF3FA !important;
    }

    /* 슬라이더도 파스텔 계열로 통일 */
    div[data-baseweb="slider"] [role="slider"] {
        background-color: #91A6DD !important;
        border-color: #91A6DD !important;
        box-shadow: 0 0 0 1px rgba(145, 166, 221, 0.10) !important;
    }

    div[data-baseweb="slider"] [role="slider"]:focus {
        box-shadow: 0 0 0 0.22rem rgba(145, 166, 221, 0.18) !important;
    }

    /* 검색 위젯의 focus도 파스텔 */
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
        border-color: #AEBDE3 !important;
        box-shadow: 0 0 0 0.16rem rgba(174, 189, 227, 0.16) !important;
    }

    /* ======================================================
       V63 - 최종 위젯 테마 보정
       ====================================================== */

    /*
    Streamlit 자체 테마가 dark여도 BaseWeb 위젯이 검게 남지 않도록
    앱 내부 색상 변수와 color-scheme을 밝은 파스텔 기준으로 지정한다.
    */
    [data-testid="stAppViewContainer"],
    .stApp {
        --st-primary-color: #91A6DD;
        --st-background-color: #F8F8FD;
        --st-secondary-background-color: #F5F7FC;
        --st-text-color: #344158;
        --st-border-color: #D9E1EE;
        color-scheme: light !important;
    }

    /* 음식 selectbox - 가능한 BaseWeb 계층을 넓게 지정 */
    div[data-testid="stSelectbox"] [data-baseweb="select"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div > div,
    div[data-testid="stSelectbox"] [role="combobox"],
    div[data-testid="stSelectbox"] [aria-haspopup="listbox"] {
        background: #F9FAFE !important;
        background-color: #F9FAFE !important;
        color: #344158 !important;
        -webkit-text-fill-color: #344158 !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
        border: 1px solid #D9E1EE !important;
        border-radius: 12px !important;
        box-shadow: 0 3px 10px rgba(77, 92, 126, 0.045) !important;
    }

    /* Popover는 button이 wrapper의 직접 자식이 아닐 수 있어 descendant로 지정 */
    div[data-testid="stPopover"] button,
    div[data-testid="stPopover"] button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"],
    button[kind="secondary"] {
        background: linear-gradient(
            135deg,
            #F6F8FD 0%,
            #F2F7F8 100%
        ) !important;
        background-color: #F6F8FD !important;
        border: 1px solid #D8E1EE !important;
        color: #46546B !important;
        -webkit-text-fill-color: #46546B !important;
        box-shadow: 0 3px 10px rgba(77, 92, 126, 0.04) !important;
    }

    div[data-testid="stPopover"] button *,
    button[data-testid="stBaseButton-secondary"] *,
    button[kind="secondary"] * {
        color: #46546B !important;
        -webkit-text-fill-color: #46546B !important;
        font-weight: 700 !important;
    }

    div[data-testid="stPopover"] button:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background: #EEF3FA !important;
        background-color: #EEF3FA !important;
        border-color: #C5D1E5 !important;
    }

    /* 열리는 select / popover 메뉴 */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [data-baseweb="menu"] > div,
    ul[role="listbox"],
    ul[role="listbox"] > li {
        background-color: #FCFDFF !important;
        color: #3E4B62 !important;
    }

    ul[role="listbox"] > li:hover {
        background-color: #EEF3FA !important;
    }

    /* 취향 칩과 검색 버튼 사이를 확실히 띄운다. */
    .search-action-spacer {
        height: 20px;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 0.72rem !important;
            padding-right: 0.72rem !important;
            padding-top: 0.65rem !important;
            padding-bottom: 1.4rem !important;
        }

        .search-action-spacer {
            height: 12px;
        }

        /* Streamlit columns: 휴대폰에서는 한 줄씩 세로 배치 */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 0.65rem !important;
        }

        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 0 !important;
        }

        /* 입력/선택/팝오버/링크가 좁은 화면에서 가로로 넘치지 않게 */
        div[data-testid="stTextInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stPopover"],
        div[data-testid="stLinkButton"],
        div[data-testid="stButton"] {
            width: 100% !important;
            max-width: 100% !important;
        }

        div[data-testid="stPopover"] > button,
        div[data-testid="stLinkButton"] a,
        div[data-testid="stButton"] > button {
            width: 100% !important;
        }

        .app-hero {
            padding: 1.3rem 1.05rem !important;
            border-radius: 18px !important;
            margin-bottom: 0.85rem !important;
        }

        .app-hero-badge {
            font-size: 0.69rem;
            padding: 0.27rem 0.58rem;
            margin-bottom: 0.55rem;
        }

        .app-hero-title {
            font-size: 1.78rem !important;
            line-height: 1.12;
        }

        .app-hero-subtitle {
            font-size: 0.88rem !important;
            line-height: 1.55;
            margin-top: 0.58rem;
        }

        .section-kicker {
            font-size: 0.68rem;
        }

        .section-title {
            font-size: 1.12rem;
        }

        .section-description,
        .results-heading-subtitle {
            font-size: 0.82rem;
            line-height: 1.45;
        }

        .results-heading {
            margin-top: 1.25rem;
            margin-bottom: 0.55rem;
        }

        .results-heading-title {
            font-size: 1.3rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px;
        }

        /* 결과 카드 상단 */
        .result-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.3rem;
        }

        .restaurant-name,
        .winner-name {
            font-size: 1.2rem !important;
            line-height: 1.3;
            overflow-wrap: anywhere;
            word-break: keep-all;
        }

        .result-rank {
            font-size: 0.72rem;
            padding: 0.27rem 0.56rem;
        }

        .score-badge {
            min-width: 0;
            padding: 0.05rem 0 0.12rem;
            flex-direction: row;
            align-items: baseline;
            justify-content: flex-start;
            gap: 0.42rem;
        }

        .score-number {
            font-size: 1.48rem;
        }

        .score-label {
            margin-top: 0;
            font-size: 0.7rem;
        }

        /* 4개 정보는 휴대폰에서 2 x 2 */
        .meta-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 0.42rem;
            margin-top: 0.58rem;
            border-radius: 13px !important;
            padding: 0.11rem !important;
        }

        .meta-item {
            padding: 0.54rem 0.58rem;
            border-radius: 11px;
        }

        .meta-label {
            font-size: 0.64rem;
        }

        .meta-value {
            font-size: 0.84rem;
            white-space: normal;
            overflow: visible;
            text-overflow: clip;
            overflow-wrap: anywhere;
        }

        .address-line {
            margin-top: 0.55rem;
            font-size: 0.78rem;
            overflow-wrap: anywhere;
            word-break: keep-all;
        }

        .detail-summary {
            padding: 0.62rem 0.68rem;
            font-size: 0.86rem;
            line-height: 1.55;
        }

        .review-card-heading {
            align-items: flex-start;
            gap: 0.3rem;
        }

        .review-card-status {
            font-size: 0.8rem;
        }

        /* 탭 3개가 한 화면 안에 들어오도록 */
        .stTabs [data-baseweb="tab-list"] {
            display: flex;
            width: 100%;
            gap: 0.12rem;
            padding: 0.16rem;
        }

        .stTabs [data-baseweb="tab"] {
            flex: 1 1 0;
            min-width: 0;
            justify-content: center;
            padding: 0.5rem 0.15rem;
        }

        .stTabs [data-baseweb="tab"] p {
            font-size: 0.76rem !important;
            white-space: nowrap;
        }

        /* 터치 영역 */
        div[data-testid="stPopover"] button,
        div.stButton > button,
        div[data-testid="stLinkButton"] a {
            min-height: 44px !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stSelectbox"] [role="combobox"] {
            min-height: 44px !important;
        }

        div[data-testid="stPopover"] button {
            font-size: 0.84rem !important;
        }

        /* Expander/Alert도 휴대폰에서 조금 더 컴팩트하게 */
        div[data-testid="stExpander"] summary {
            min-height: 44px;
        }

        div[data-testid="stAlert"] {
            font-size: 0.84rem;
        }
    }


    /* ======================================================
       V73 - SOFT PASTEL CAFE UI
       기능/점수 계산은 건드리지 않고 화면 질감만 보강한다.
       ====================================================== */

    :root {
        --v73-cream: #FFFBF7;
        --v73-blush: #F7DDE7;
        --v73-peach: #F9E6D7;
        --v73-lavender: #E4E0F8;
        --v73-lavender-strong: #B7B0E2;
        --v73-sky: #DCECF5;
        --v73-mint: #DDF0E7;
        --v73-ink: #47475C;
        --v73-soft-ink: #6C6D80;
        --v73-border: rgba(186, 180, 211, 0.24);
    }

    html,
    body,
    [data-testid="stAppViewContainer"],
    .stApp {
        background:
            radial-gradient(circle at 4% 4%, rgba(247, 221, 231, 0.62), transparent 25%),
            radial-gradient(circle at 96% 8%, rgba(228, 224, 248, 0.68), transparent 27%),
            radial-gradient(circle at 88% 88%, rgba(221, 240, 231, 0.62), transparent 29%),
            radial-gradient(circle at 9% 92%, rgba(249, 230, 215, 0.48), transparent 25%),
            linear-gradient(145deg, #FFFDFC 0%, #F9F7FD 42%, #F5FAF9 100%) !important;
        background-attachment: fixed !important;
    }

    ::selection {
        background: #DDD6F2;
        color: #47475C;
    }

    .block-container {
        max-width: 1100px;
    }

    /* ---------- 히어로: 파스텔 구름처럼 겹치는 그라데이션 ---------- */
    .app-hero {
        position: relative;
        overflow: hidden;
        isolation: isolate;
        background:
            radial-gradient(circle at 80% 18%, rgba(255,255,255,0.58), transparent 24%),
            linear-gradient(
                120deg,
                #F6DDE7 0%,
                #E6E2F8 34%,
                #DCEBF5 67%,
                #DDF0E7 100%
            ) !important;
        border: 1px solid rgba(255, 255, 255, 0.84) !important;
        box-shadow:
            0 18px 46px rgba(117, 107, 147, 0.12),
            0 2px 12px rgba(145, 166, 192, 0.07),
            inset 0 1px 0 rgba(255,255,255,0.72) !important;
    }

    .app-hero::before,
    .app-hero::after {
        content: "";
        position: absolute;
        border-radius: 999px;
        pointer-events: none;
        z-index: -1;
        filter: blur(1px);
    }

    .app-hero::before {
        width: 235px;
        height: 235px;
        right: -58px;
        top: -78px;
        background: radial-gradient(circle, rgba(255,255,255,0.72) 0%, rgba(255,255,255,0.12) 58%, transparent 72%);
    }

    .app-hero::after {
        width: 180px;
        height: 180px;
        left: 51%;
        bottom: -118px;
        background: radial-gradient(circle, rgba(249,230,215,0.66) 0%, rgba(249,230,215,0.08) 64%, transparent 74%);
    }

    .app-hero-badge {
        background: rgba(255,255,255,0.55) !important;
        border: 1px solid rgba(255,255,255,0.82) !important;
        color: #6E6882 !important;
        box-shadow: 0 4px 14px rgba(112, 101, 143, 0.06);
        backdrop-filter: blur(8px);
    }

    .app-hero-title {
        color: #49485D !important;
        text-shadow: 0 1px 0 rgba(255,255,255,0.5);
    }

    .app-hero-subtitle {
        color: #68697B !important;
        max-width: 760px;
    }

    /* ---------- 섹션 제목 ---------- */
    .section-kicker {
        color: #9A8FC0 !important;
        letter-spacing: 0.12em;
    }

    .section-title,
    .results-heading-title {
        color: #4A4A5F !important;
    }

    .section-description,
    .results-heading-subtitle {
        color: #77788B !important;
    }

    /* ---------- 큰 카드: 반투명 크림 + 은은한 파스텔 가장자리 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(145deg, rgba(255,255,255,0.82), rgba(255,252,250,0.70)) !important;
        border: 1px solid rgba(255,255,255,0.90) !important;
        outline: 1px solid rgba(190, 182, 213, 0.16);
        box-shadow:
            0 14px 34px rgba(108, 100, 132, 0.075),
            0 3px 10px rgba(132, 151, 164, 0.035),
            inset 0 1px 0 rgba(255,255,255,0.92) !important;
        backdrop-filter: blur(12px) saturate(108%);
    }

    /* 검색 조건 카드는 크림·라벤더·민트가 아주 약하게 섞이게 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.section-title) {
        background:
            radial-gradient(circle at 96% 8%, rgba(228,224,248,0.40), transparent 27%),
            radial-gradient(circle at 4% 96%, rgba(221,240,231,0.32), transparent 25%),
            linear-gradient(145deg, rgba(255,252,249,0.90), rgba(251,250,255,0.84)) !important;
    }

    /* ---------- 입력창 ---------- */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [role="combobox"] {
        background: rgba(255,255,255,0.82) !important;
        border-color: rgba(193, 188, 216, 0.35) !important;
        box-shadow:
            0 5px 14px rgba(108,100,132,0.045),
            inset 0 1px 0 rgba(255,255,255,0.85) !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
        border-color: #B9B1DD !important;
        box-shadow: 0 0 0 0.18rem rgba(183,176,226,0.15) !important;
    }

    /* ---------- 팝오버/보조 버튼 ---------- */
    div[data-testid="stPopover"] button,
    button[data-testid="stBaseButton-secondary"],
    button[kind="secondary"],
    div[data-testid="stLinkButton"] a {
        background:
            linear-gradient(135deg, rgba(250,247,255,0.92), rgba(245,251,248,0.92)) !important;
        border-color: rgba(190,184,213,0.34) !important;
        box-shadow: 0 5px 14px rgba(101, 95, 126, 0.045) !important;
    }

    div[data-testid="stPopover"] button:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    div[data-testid="stLinkButton"] a:hover {
        background: linear-gradient(135deg, #F0ECFA 0%, #EDF7F2 100%) !important;
        border-color: rgba(173,164,205,0.48) !important;
        transform: translateY(-1px);
    }

    /* ---------- 메인 검색 버튼 ---------- */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(
            125deg,
            #B7AFE1 0%,
            #AEBFE6 34%,
            #9CCFD0 67%,
            #A8D6C4 100%
        ) !important;
        border: 1px solid rgba(255,255,255,0.76) !important;
        box-shadow:
            0 11px 24px rgba(126, 119, 166, 0.14),
            inset 0 1px 0 rgba(255,255,255,0.44) !important;
        letter-spacing: -0.01em;
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        filter: saturate(1.04) brightness(1.015);
        box-shadow:
            0 14px 28px rgba(126, 119, 166, 0.18),
            inset 0 1px 0 rgba(255,255,255,0.52) !important;
    }

    /* ---------- 취향/상태 칩 ---------- */
    .filter-chip {
        background: linear-gradient(135deg, #F4EFFB 0%, #EDF7F3 100%) !important;
        border-color: rgba(190,183,216,0.34) !important;
        color: #615F76 !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.72);
    }

    /* ---------- 결과 카드 ---------- */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-header) {
        position: relative;
        background:
            radial-gradient(circle at 94% 6%, rgba(228,224,248,0.26), transparent 24%),
            linear-gradient(145deg, rgba(255,255,255,0.88), rgba(255,250,247,0.76)) !important;
        transition: transform 170ms ease, box-shadow 170ms ease, border-color 170ms ease;
    }

    @media (min-width: 701px) {
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-header):hover {
            transform: translateY(-2px);
            border-color: rgba(181,173,210,0.32) !important;
            box-shadow:
                0 18px 40px rgba(108,100,132,0.10),
                0 5px 13px rgba(132,151,164,0.045),
                inset 0 1px 0 rgba(255,255,255,0.94) !important;
        }
    }

    /* 1위 카드는 살짝 더 특별하게 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.winner-rank) {
        background:
            radial-gradient(circle at 90% 4%, rgba(255,255,255,0.76), transparent 22%),
            radial-gradient(circle at 5% 100%, rgba(249,230,215,0.30), transparent 26%),
            linear-gradient(135deg, rgba(247,235,243,0.90), rgba(238,237,251,0.88) 48%, rgba(231,246,239,0.88)) !important;
        outline-color: rgba(178,166,210,0.26);
        box-shadow:
            0 20px 44px rgba(115,105,146,0.13),
            0 4px 12px rgba(146,160,167,0.05),
            inset 0 1px 0 rgba(255,255,255,0.94) !important;
    }

    .result-rank {
        background: linear-gradient(135deg, #F2EEFA 0%, #EEF6F4 100%) !important;
        border-color: rgba(190,183,216,0.35) !important;
        color: #69667D !important;
    }

    .winner-rank {
        background: linear-gradient(120deg, #EFCFDC 0%, #D8D6F2 48%, #CFE9DE 100%) !important;
        border-color: rgba(255,255,255,0.66) !important;
        color: #5C596D !important;
        box-shadow: 0 6px 16px rgba(113,105,143,0.09) !important;
    }

    .restaurant-name {
        color: #49495D !important;
    }

    .score-badge {
        padding: 0.58rem 0.74rem !important;
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(244,238,251,0.92), rgba(238,248,244,0.90));
        border: 1px solid rgba(190,183,216,0.28);
        box-shadow:
            0 6px 17px rgba(105,98,132,0.055),
            inset 0 1px 0 rgba(255,255,255,0.82);
    }

    .score-number {
        color: #7B73AF !important;
    }

    .score-label {
        color: #858297 !important;
    }

    /* 평점 · 리뷰 · 가격 · 도보 정보는 한 가지 파스텔 톤으로 통일 */
    .meta-item {
        background:
            linear-gradient(145deg, rgba(248,246,253,0.98) 0%, rgba(243,247,252,0.98) 100%) !important;
        border-color: rgba(184,181,210,0.24) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.82),
            0 3px 10px rgba(102,105,137,0.035);
    }

    .meta-label {
        color: #8B86A0 !important;
    }

    .meta-value {
        color: #55566C !important;
    }

    .address-line {
        color: #77778A !important;
    }

    /* ---------- 상세 분석 ---------- */
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.56) !important;
        border-color: rgba(193,187,214,0.24) !important;
    }

    .detail-summary {
        background: linear-gradient(135deg, #F7F2FC 0%, #F1F8F5 52%, #FFF7F2 100%) !important;
        border-color: rgba(193,187,214,0.22) !important;
        color: #626276 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #F2EEFA 0%, #EFF7F4 100%) !important;
        border: 1px solid rgba(193,187,214,0.20);
    }

    .stTabs [data-baseweb="tab"] {
        transition: background 150ms ease, box-shadow 150ms ease;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.80) !important;
        color: #6D67A0 !important;
        box-shadow: 0 3px 10px rgba(107,100,133,0.06);
    }

    /* ---------- 알림 ---------- */
    div[data-testid="stAlert"] {
        background: linear-gradient(135deg, rgba(248,244,253,0.88), rgba(242,249,246,0.88)) !important;
        border-color: rgba(192,185,215,0.24) !important;
        box-shadow: 0 4px 12px rgba(105,99,128,0.035);
    }

    /* ---------- 모바일에서는 장식과 떠오르는 효과를 줄여 안정적으로 ---------- */
    @media (max-width: 700px) {
        html,
        body,
        [data-testid="stAppViewContainer"],
        .stApp {
            background-attachment: scroll !important;
        }

        .app-hero::before {
            width: 150px;
            height: 150px;
            right: -52px;
            top: -52px;
        }

        .app-hero::after {
            width: 125px;
            height: 125px;
            left: 48%;
            bottom: -88px;
        }

        .score-badge {
            padding: 0.42rem 0.58rem !important;
            border-radius: 13px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-header) {
            transform: none !important;
        }

        div.stButton > button[kind="primary"]:hover,
        div[data-testid="stPopover"] button:hover,
        button[data-testid="stBaseButton-secondary"]:hover,
        button[kind="secondary"]:hover,
        div[data-testid="stLinkButton"] a:hover {
            transform: none !important;
        }
    }



    /* ======================================================
       V76 - RICHER DUSTY PASTEL
       V75의 통일감은 유지하고 파스텔 농도만 한 단계 올린다.
       ====================================================== */

    :root {
        --v76-blush: #F0C8D8;
        --v76-peach: #F4D1B9;
        --v76-lavender: #D8D0F3;
        --v76-lavender-strong: #9E93D1;
        --v76-sky: #CBE0F1;
        --v76-mint: #CBE7DA;
        --v76-ink: #424257;
        --v76-soft-ink: #68677D;
    }

    html,
    body,
    [data-testid="stAppViewContainer"],
    .stApp {
        background:
            radial-gradient(circle at 4% 4%, rgba(240, 200, 216, 0.76), transparent 27%),
            radial-gradient(circle at 96% 8%, rgba(216, 208, 243, 0.82), transparent 29%),
            radial-gradient(circle at 88% 88%, rgba(203, 231, 218, 0.76), transparent 31%),
            radial-gradient(circle at 9% 92%, rgba(244, 209, 185, 0.64), transparent 27%),
            linear-gradient(145deg, #FFF9F7 0%, #F5F1FC 44%, #EEF8F5 100%) !important;
    }

    ::selection {
        background: #CEC5EC;
        color: #3F3F54;
    }

    /* 상단 히어로는 눈에 띄되 쨍하지 않게 */
    .app-hero {
        background:
            radial-gradient(circle at 80% 18%, rgba(255,255,255,0.52), transparent 24%),
            linear-gradient(
                120deg,
                #F2CDDC 0%,
                #DCD7F5 34%,
                #CFE4F3 67%,
                #D1EBDD 100%
            ) !important;
        border-color: rgba(255,255,255,0.78) !important;
        box-shadow:
            0 20px 48px rgba(106, 94, 147, 0.16),
            0 3px 14px rgba(123, 151, 181, 0.09),
            inset 0 1px 0 rgba(255,255,255,0.62) !important;
    }

    .app-hero-badge {
        background: rgba(255,255,255,0.62) !important;
        border-color: rgba(255,255,255,0.78) !important;
        color: #625B7B !important;
    }

    .app-hero-title {
        color: #414156 !important;
    }

    .app-hero-subtitle {
        color: #606176 !important;
    }

    .section-kicker {
        color: #8174B5 !important;
    }

    .section-title,
    .results-heading-title {
        color: #434359 !important;
    }

    .section-description,
    .results-heading-subtitle {
        color: #6E6F83 !important;
    }

    /* 큰 카드: 흰색은 유지하되 파스텔 테두리 존재감 강화 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background:
            linear-gradient(145deg, rgba(255,255,255,0.88), rgba(252,247,249,0.80)) !important;
        border-color: rgba(255,255,255,0.86) !important;
        outline-color: rgba(170, 160, 205, 0.26) !important;
        box-shadow:
            0 15px 36px rgba(99, 91, 127, 0.10),
            0 4px 12px rgba(118, 145, 158, 0.055),
            inset 0 1px 0 rgba(255,255,255,0.88) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.section-title) {
        background:
            radial-gradient(circle at 96% 8%, rgba(216,208,243,0.55), transparent 29%),
            radial-gradient(circle at 4% 96%, rgba(203,231,218,0.48), transparent 27%),
            linear-gradient(145deg, rgba(255,248,245,0.94), rgba(247,244,253,0.90)) !important;
    }

    /* 입력창도 살짝 더 보랏빛 */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stSelectbox"] [role="combobox"] {
        background: rgba(255,255,255,0.88) !important;
        border-color: rgba(163, 153, 201, 0.46) !important;
        box-shadow:
            0 5px 14px rgba(93,85,123,0.065),
            inset 0 1px 0 rgba(255,255,255,0.84) !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within,
    div[data-testid="stSelectbox"] div[role="combobox"]:focus-within {
        border-color: #A99DDA !important;
        box-shadow: 0 0 0 0.19rem rgba(156,143,211,0.20) !important;
    }

    div[data-testid="stPopover"] button,
    button[data-testid="stBaseButton-secondary"],
    button[kind="secondary"],
    div[data-testid="stLinkButton"] a {
        background: linear-gradient(135deg, #EEE8FA 0%, #E6F3EE 100%) !important;
        border-color: rgba(161,150,199,0.42) !important;
        color: #57536C !important;
        box-shadow: 0 5px 14px rgba(91,83,120,0.065) !important;
    }

    div[data-testid="stPopover"] button:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[kind="secondary"]:hover,
    div[data-testid="stLinkButton"] a:hover {
        background: linear-gradient(135deg, #E5DCF6 0%, #DCEFE7 100%) !important;
        border-color: rgba(145,132,190,0.58) !important;
    }

    /* 메인 버튼은 기존보다 한 톤 진한 파스텔 */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(
            110deg,
            #A99DDB 0%,
            #9EADE0 30%,
            #91C2D2 62%,
            #96CDB5 100%
        ) !important;
        box-shadow:
            0 12px 26px rgba(105, 95, 153, 0.20),
            inset 0 1px 0 rgba(255,255,255,0.38) !important;
    }

    .filter-chip {
        background: linear-gradient(135deg, #ECE4F8 0%, #E1F1EB 100%) !important;
        border-color: rgba(160,149,199,0.45) !important;
        color: #56536D !important;
    }

    /* 결과 카드도 배경에 아주 약한 보라 기운 */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.result-header) {
        background:
            radial-gradient(circle at 94% 6%, rgba(216,208,243,0.42), transparent 26%),
            linear-gradient(145deg, rgba(255,255,255,0.92), rgba(252,245,247,0.84)) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.winner-rank) {
        background:
            radial-gradient(circle at 90% 4%, rgba(255,255,255,0.68), transparent 22%),
            radial-gradient(circle at 5% 100%, rgba(244,209,185,0.44), transparent 28%),
            linear-gradient(135deg, rgba(242,205,220,0.94), rgba(220,215,245,0.92) 48%, rgba(209,235,221,0.92)) !important;
        outline-color: rgba(153,140,198,0.35) !important;
        box-shadow:
            0 21px 46px rgba(98,87,143,0.17),
            0 5px 14px rgba(118,145,158,0.07),
            inset 0 1px 0 rgba(255,255,255,0.82) !important;
    }

    .result-rank {
        background: linear-gradient(135deg, #E9E2F7 0%, #E1F0EA 100%) !important;
        border-color: rgba(157,145,198,0.48) !important;
        color: #5C5874 !important;
    }

    .winner-rank {
        background: linear-gradient(120deg, #E8BACD 0%, #C9C3ED 48%, #BDE0D0 100%) !important;
        border-color: rgba(255,255,255,0.60) !important;
        color: #514D67 !important;
        box-shadow: 0 7px 18px rgba(93,83,137,0.13) !important;
    }

    .restaurant-name {
        color: #424257 !important;
    }

    .score-badge {
        background: linear-gradient(145deg, #EDE5F9 0%, #E2F1EB 100%) !important;
        border-color: rgba(158,145,199,0.42) !important;
        box-shadow:
            0 7px 18px rgba(91,82,127,0.085),
            inset 0 1px 0 rgba(255,255,255,0.72) !important;
    }

    .score-number {
        color: #695DAA !important;
    }

    .score-label {
        color: #77738E !important;
    }

    /* V78: 이어지는 색 흐름은 유지하되 칸과 칸 사이의 연결부는 끊어서 더 또렷하게 */
    .meta-grid {
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        overflow: visible;
    }

    .meta-item {
        border: 1px solid rgba(255,255,255,0.54) !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.54),
            0 4px 11px rgba(82,78,112,0.05) !important;
        backdrop-filter: blur(5px) saturate(112%);
        -webkit-backdrop-filter: blur(5px) saturate(112%);
        transition: filter 0.18s ease, transform 0.18s ease;
    }

    .meta-grid .meta-item:nth-child(1) {
        background: linear-gradient(135deg, rgba(220,207,243,0.96) 0%, rgba(214,205,241,0.94) 100%) !important;
    }

    .meta-grid .meta-item:nth-child(2) {
        background: linear-gradient(135deg, rgba(216,216,244,0.96) 0%, rgba(208,219,243,0.94) 100%) !important;
    }

    .meta-grid .meta-item:nth-child(3) {
        background: linear-gradient(135deg, rgba(207,223,243,0.96) 0%, rgba(203,231,235,0.94) 100%) !important;
    }

    .meta-grid .meta-item:nth-child(4) {
        background: linear-gradient(135deg, rgba(203,231,235,0.96) 0%, rgba(205,232,216,0.94) 100%) !important;
    }

    .meta-item:hover {
        filter: brightness(1.02);
        transform: translateY(-1px);
    }

    .meta-label {
        color: #736C91 !important;
    }

    .meta-value {
        color: #444459 !important;
    }

    .address-line {
        color: #6C6B7F !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(249,246,253,0.72) !important;
        border-color: rgba(161,149,201,0.36) !important;
    }

    .detail-summary {
        background: linear-gradient(135deg, #EEE6F8 0%, #E3F2EC 52%, #FAE9DE 100%) !important;
        border-color: rgba(159,147,199,0.36) !important;
        color: #56556B !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #E9E1F7 0%, #E0F0EA 100%) !important;
        border-color: rgba(158,146,199,0.34) !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255,255,255,0.86) !important;
        color: #63589E !important;
        box-shadow: 0 4px 12px rgba(91,82,127,0.09) !important;
    }

    div[data-testid="stAlert"] {
        background: linear-gradient(135deg, #EEE7F8 0%, #E3F2EC 100%) !important;
        border-color: rgba(159,147,199,0.34) !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# 히어로
st.markdown(
    """
    <div class="app-hero">
        <div class="app-hero-badge">SMART RESTAURANT PICK</div>
        <div class="app-hero-title">오늘 뭐 먹지?</div>
        <p class="app-hero-subtitle">
            위치와 음식 조건을 고르면 평점, 실제 리뷰, 가격대와 도보 거리까지
            한 번에 분석해서 지금 가기 좋은 맛집을 추천해드려요.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================================
# 가격 필터 상태/콜백
# ======================================

PRICE_RANGES = [
    ("under_10000", "1만원 이하"),
    ("10000_20000", "1만원 ~ 2만원"),
    ("20000_30000", "2만원 ~ 3만원"),
    ("30000_50000", "3만원 ~ 5만원"),
    ("over_50000", "5만원 이상"),
]


def set_all_price_ranges():
    value = st.session_state["price_select_all"]

    for key, _ in PRICE_RANGES:
        st.session_state[f"price_{key}"] = value


def sync_price_select_all():
    all_selected = all(
        st.session_state.get(
            f"price_{key}",
            False
        )
        for key, _ in PRICE_RANGES
    )

    st.session_state["price_select_all"] = all_selected


if "price_initialized" not in st.session_state:
    st.session_state["price_select_all"] = True

    for key, _ in PRICE_RANGES:
        st.session_state[f"price_{key}"] = True

    st.session_state["price_initialized"] = True


def get_price_filter_summary():
    selected_labels = [
        label
        for key, label in PRICE_RANGES
        if st.session_state.get(
            f"price_{key}",
            False
        )
    ]

    if len(selected_labels) == len(PRICE_RANGES):
        return "전체"

    if len(selected_labels) == 1:
        return selected_labels[0]

    if not selected_labels:
        return "선택 안 됨"

    return f"{len(selected_labels)}개 선택"


# ======================================
# 1. 검색 조건
# ======================================

BUILTIN_GENRES = [
    "전체",
    "한식",
    "중식",
    "일식",
    "양식",
    "아시아 음식",
    "치킨",
    "분식",
    "패스트푸드",
    "카페·디저트",
    "주점·술집",
]

with st.container(
    border=True
):
    st.markdown(
        """
        <div class="section-kicker">STEP 1</div>
        <div class="section-title">🔎 검색 조건</div>
        <div class="section-description">
            먹을 장소와 음식 종류, 원하는 가격대를 정해주세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

    location_col, food_col = st.columns(
        [1, 1]
    )

    with location_col:
        location = st.text_input(
            "📍 어디에서 먹을까요?",
            placeholder="예: 강남역, 서울시청",
        )

    with food_col:
        food_choice = st.selectbox(
            "🍽️ 뭐가 먹고 싶나요?",
            BUILTIN_GENRES,
            index=0,
            placeholder=(
                "장르 선택 또는 피자, 마라탕, 초밥 등 직접 입력"
            ),
            accept_new_options=True,
        )

    # V79: 모바일에서 여러 팝오버가 겹쳐 열리는 문제 방지
    # 가격대와 검색 예시를 하나의 팝오버 안 탭으로 통합한다.
    # 따라서 화면에는 떠 있는 검색 메뉴가 최대 하나만 존재한다.
    with st.popover(
        f"💰 가격대 · {get_price_filter_summary()}  ·  💡 검색 도움",
        use_container_width=True,
    ):
        price_tab, example_tab = st.tabs(
            ["💰 가격대", "💡 검색 예시"]
        )

        with price_tab:
            st.checkbox(
                "전체",
                key="price_select_all",
                on_change=set_all_price_ranges,
            )

            for key, label in PRICE_RANGES:
                st.checkbox(
                    label,
                    key=f"price_{key}",
                    on_change=sync_price_select_all,
                )

        with example_tab:
            st.caption(
                "피자 · 파스타 · 스테이크 · 햄버거\n\n"
                "초밥 · 라멘 · 돈까스 · 우동\n\n"
                "마라탕 · 짬뽕 · 짜장면 · 딤섬\n\n"
                "떡볶이 · 김밥 · 순대 · 튀김\n\n"
                "삼겹살 · 갈비 · 국밥 · 냉면\n\n"
                "쌀국수 · 카레 · 타코 · 샤브샤브\n\n"
                "치킨 · 족발 · 곱창 · 회\n\n"
                "빙수 · 케이크 · 베이글 · 커피"
            )
            st.info(
                "목록에 없는 음식도 직접 입력할 수 있어요."
            )


food_choice = (
    food_choice
    or "전체"
).strip()

is_custom_food_query = (
    food_choice
    not in BUILTIN_GENRES
)

food_category = (
    "전체"
    if is_custom_food_query
    else food_choice
)

custom_food_query = (
    food_choice
    if is_custom_food_query
    else ""
)

selected_price_ranges = [
    key
    for key, _ in PRICE_RANGES
    if st.session_state.get(
        f"price_{key}",
        False
    )
]

if not selected_price_ranges:
    st.info(
        "가격대를 하나 이상 선택해주세요."
    )

# 기존 코드 호환용
price_filter = "전체"


# ======================================
# 2. 내부 점수 설정
# ======================================
# 점수 계산 기준은 화면에는 노출하지 않고 내부 계산에만 사용한다.
# 기존 함수 호출부 호환용.
importance_levels = {}
importance_summary = ""


st.markdown(
    '<div class="search-action-spacer"></div>',
    unsafe_allow_html=True,
)


search_button = st.button(
    "🔍 추천 맛집 찾기",
    use_container_width=True,
    type="primary",
    disabled=(
        not selected_price_ranges
    ),
)


# ======================================
# 검색 시작
# ======================================

if search_button:

    if not location:

        st.warning(
            "📍 위치를 먼저 입력해주세요."
        )

    else:

        # ======================================
        # 1. 위치 → 좌표
        # ======================================

        geocode_url = (
            "https://maps.googleapis.com/maps/api/geocode/json"
        )


        geocode_params = {
            "address": location,
            "key": GOOGLE_MAPS_API_KEY,
            "language": "ko",
            "region": "kr"
        }


        try:

            geocode_response = requests.get(
                geocode_url,
                params=geocode_params,
                timeout=15
            )

            geocode_data = (
                geocode_response.json()
            )

        except requests.RequestException:

            st.error(
                "❌ 위치 검색 중 네트워크 오류가 발생했습니다."
            )

            st.stop()


        if geocode_data.get(
            "status"
        ) != "OK":

            st.error(
                "❌ 입력한 위치를 찾지 못했습니다."
            )

            st.stop()


        latitude = (
            geocode_data["results"][0]
            ["geometry"]
            ["location"]
            ["lat"]
        )


        longitude = (
            geocode_data["results"][0]
            ["geometry"]
            ["location"]
            ["lng"]
        )


        st.toast(
            f"📍 {location} 기준으로 맛집을 찾고 있어요.",
            icon="✅",
        )


        # ======================================
        # 2. 주변 음식점
        # ======================================

        places_url = (
            "https://places.googleapis.com/v1/places:searchNearby"
        )

        text_search_url = (
            "https://places.googleapis.com/v1/places:searchText"
        )


        places_headers = {

            "Content-Type":
                "application/json",

            "X-Goog-Api-Key":
                GOOGLE_MAPS_API_KEY,

            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.location,"
                "places.primaryType,"
                "places.types,"
                "places.rating,"
                "places.userRatingCount,"
                "places.priceLevel,"
                "places.priceRange,"
                "places.googleMapsUri"
            )
        }


        # ======================================
        # 음식 장르 → Google Places 검색 타입
        # ======================================

        category_types = {

            "전체": [
                "restaurant"
            ],

            "한식": [
                "korean_restaurant",
                "korean_barbecue_restaurant"
            ],

            "중식": [
                "chinese_restaurant",
                "chinese_noodle_restaurant",
                "cantonese_restaurant",
                "dim_sum_restaurant"
            ],

            "일식": [
                "japanese_restaurant",
                "sushi_restaurant",
                "ramen_restaurant",
                "japanese_curry_restaurant",
                "japanese_izakaya_restaurant",
                "tonkatsu_restaurant",
                "yakiniku_restaurant",
                "yakitori_restaurant"
            ],

            "양식": [
                "italian_restaurant",
                "french_restaurant",
                "american_restaurant",
                "western_restaurant",
                "european_restaurant",
                "steak_house"
            ],

            "아시아 음식": [
                "asian_restaurant",
                "asian_fusion_restaurant",
                "thai_restaurant",
                "vietnamese_restaurant",
                "indian_restaurant",
                "indonesian_restaurant",
                "malaysian_restaurant",
                "filipino_restaurant"
            ],

            "치킨": [
                "chicken_restaurant",
                "chicken_wings_restaurant"
            ],

            # 분식 전용 Google 타입은 없으므로
            # snack_bar는 후보 탐색 힌트로만 사용한다.
            # 최종 분식 판별은 프랜차이즈 사전에서만 확정한다.
            "분식": [
                "snack_bar"
            ],

            "패스트푸드": [
                "fast_food_restaurant",
                "hamburger_restaurant",
                "hot_dog_restaurant",
                "hot_dog_stand",
                "sandwich_shop"
            ],

            "카페·디저트": [
                "cafe",
                "coffee_shop",
                "coffee_stand",
                "bakery",
                "dessert_shop",
                "dessert_restaurant",
                "cake_shop",
                "donut_shop",
                "ice_cream_shop",
                "tea_house",
                "juice_shop",
                "pastry_shop"
            ],

            "주점·술집": [
                "bar",
                "pub",
                "cocktail_bar",
                "wine_bar",
                "sports_bar",
                "beer_garden",
                "brewpub",
                "irish_pub",
                "lounge_bar"
            ]
        }


        selected_types = category_types.get(
            food_category,
            ["restaurant"]
        )


        # ======================================
        # 📍 검색 반경: 현재 범위를 먼저 전부 분석한 뒤 확대
        # ======================================
        # 1차: 1.5km
        # 조건에 맞는 최종 결과가 10개 미만이면
        # 2차: 2.5km, 필요하면 3.0km까지 "새로 발견된 식당"만 추가 분석한다.
        #
        # Google Nearby Search는 한 요청에서 최대 20개까지 반환할 수 있다.
        #
        # 기본 장르:
        # - Nearby POPULARITY 20
        # - Nearby DISTANCE 20
        # → 반경당 최대 40개
        #
        # 직접 메뉴 검색:
        # - Text Search 20
        # - 메뉴 전용 Google Type Nearby 최대 40
        # - 일반 restaurant Nearby 보완 최대 20
        # → 중복 제거 전 반경당 최대 80개
        SEARCH_TARGET_COUNT = 10
        MAX_GENRE_CANDIDATES_PER_RADIUS = 40
        MAX_CUSTOM_CANDIDATES_PER_RADIUS = 80
        search_radii = [1500.0, 2500.0, 3000.0]

        all_price_ranges_selected = all(
            st.session_state.get(f"price_{key}", False)
            for key, _ in PRICE_RANGES
        )

        restaurants = []
        checked_place_ids = set()
        restaurant_results = []

        # V71: Google 리뷰 API를 끝내 불러오지 못한 식당은
        # '리뷰 정보 없음 = 중립'으로 계산하지 않고 추천 순위에서 제외한다.
        # 사용자에게는 검색이 끝난 뒤 제외된 식당 수만 안내한다.
        review_api_error_places = set()

        def fetch_text_search_restaurants(
            query,
            search_radius
        ):
            """
            직접 입력한 음식명(피자/마라탕/초밥 등)은
            Google Text Search (New)로 검색한다.

            locationBias는 원형 반경을 우선 탐색하도록 유도하고,
            아래에서 사용자 중심 실제 반경을 다시 엄격하게 검사한다.
            """
            body = {
                "textQuery": query,
                "pageSize": 20,
                "rankPreference": "RELEVANCE",
                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": latitude,
                            "longitude": longitude
                        },
                        "radius": search_radius
                    }
                },
                "languageCode": "ko",
                "regionCode": "KR"
            }

            try:
                response = requests.post(
                    text_search_url,
                    headers=places_headers,
                    json=body,
                    timeout=20
                )
            except requests.RequestException:
                st.warning(
                    "직접 음식명 Text Search 요청에 네트워크 오류가 있어 "
                    "Nearby 검색 결과로 보완합니다."
                )
                return []

            if response.status_code != 200:
                st.warning(
                    "직접 음식명 Text Search 일부 요청에 실패해 "
                    "Nearby 검색 결과로 보완합니다. "
                    f"(응답 코드 {response.status_code})"
                )
                return []

            return response.json().get(
                "places",
                []
            )


        def get_reviews_for_place(place):
            """
            Google Places 리뷰를 요청하고 결과를 캐시한다.

            place["_reviews_fetch_status"] 값:
            - "ok": 리뷰를 정상적으로 가져옴
            - "no_reviews": 요청은 성공했지만 리뷰가 없음
            - "api_error": 네트워크/API 오류

            V71:
            - 일시적인 네트워크 오류, 429, 5xx는 최대 2회 요청한다.
            - 끝까지 실패하면 api_error로 표시한다.
            - api_error는 이후 추천점수에서 '중립 리뷰'로 계산하지 않는다.
            """
            cached_reviews = place.get("_cached_reviews")

            if cached_reviews is not None:
                return cached_reviews

            preloaded = place.pop(
                "_preloaded_reviews",
                None
            )

            if preloaded is not None:
                place["_cached_reviews"] = preloaded
                place.setdefault(
                    "_reviews_fetch_status",
                    "ok" if preloaded else "no_reviews"
                )
                return preloaded

            place_id = place.get("id")
            place_key = (
                place_id
                or place.get("displayName", {}).get("text")
                or place.get("name")
                or "unknown"
            )

            if not place_id:
                place["_reviews_fetch_status"] = "api_error"
                place["_reviews_fetch_error"] = "missing_place_id"
                place["_cached_reviews"] = []
                review_api_error_places.add(str(place_key))
                return []

            details_url = (
                f"https://places.googleapis.com/v1/places/{place_id}"
            )

            details_headers = {
                "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": "reviews"
            }

            details_params = {
                "languageCode": "ko"
            }

            max_attempts = 2
            retryable_status_codes = {
                429,
                500,
                502,
                503,
                504,
            }
            last_error = "unknown"

            for attempt in range(max_attempts):
                try:
                    details_response = requests.get(
                        details_url,
                        headers=details_headers,
                        params=details_params,
                        timeout=8
                    )

                    if details_response.status_code == 200:
                        reviews = details_response.json().get(
                            "reviews",
                            []
                        )
                        place["_cached_reviews"] = reviews
                        place["_reviews_fetch_status"] = (
                            "ok" if reviews else "no_reviews"
                        )
                        place.pop("_reviews_fetch_error", None)
                        review_api_error_places.discard(str(place_key))
                        return reviews

                    last_error = (
                        f"http_{details_response.status_code}"
                    )

                    should_retry = (
                        details_response.status_code
                        in retryable_status_codes
                        and attempt < max_attempts - 1
                    )

                    if should_retry:
                        time.sleep(0.6 * (attempt + 1))
                        continue

                    break

                except requests.RequestException as exc:
                    last_error = exc.__class__.__name__

                    if attempt < max_attempts - 1:
                        time.sleep(0.6 * (attempt + 1))
                        continue

                except ValueError:
                    # 200 응답이어도 JSON 파싱이 깨진 경우 일시 오류로 취급한다.
                    last_error = "invalid_json"

                    if attempt < max_attempts - 1:
                        time.sleep(0.6 * (attempt + 1))
                        continue

            place["_reviews_fetch_status"] = "api_error"
            place["_reviews_fetch_error"] = last_error
            place["_cached_reviews"] = []
            review_api_error_places.add(str(place_key))
            return []


        def make_review_result(restaurant, reviews):
            # V71~V72 유지: API 실패는 '리뷰가 없는 식당'과 다르다.
            # 실패한 빈 리스트를 중립(리뷰 30/60점)으로 계산하지 않고
            # 이번 추천 순위에서는 제외한다.
            if restaurant.get("_reviews_fetch_status") == "api_error":
                return None

            (
                review_summary,
                food_related_review_count
            ) = summarize_reviews(reviews)

            category_scores = {}

            for category, data in review_summary.items():
                category_scores[category] = {
                    "positive": data.get(
                        "positive_score",
                        0
                    ),
                    "negative": data.get(
                        "negative_score",
                        0
                    ),
                    "result": data.get(
                        "result",
                        "언급 없음"
                    )
                }

            score_breakdown = get_recommendation_score_breakdown(
                restaurant.get("rating"),
                category_scores,
                google_review_count=restaurant.get(
                    "userRatingCount",
                    0
                ),
            )

            # 실제 Google 평점이 없는 식당은 계속 제외
            if score_breakdown is None:
                return None

            recommendation_score = score_breakdown["total"]
            review_category_points = score_breakdown["categories"]
            google_rating_points = score_breakdown["google"]

            return {
                "restaurant": restaurant,
                "reviews": reviews,
                "review_summary": review_summary,
                "food_related_review_count": food_related_review_count,
                "category_scores": category_scores,
                "review_category_points": review_category_points,
                "google_rating_points": google_rating_points,
                "score_breakdown": score_breakdown,
                "recommendation_score": recommendation_score,
                "importance_levels": dict(importance_levels),
                "review_count": len(reviews),
                "review_fetch_status": restaurant.get(
                    "_reviews_fetch_status",
                    "unknown"
                )
            }

        # ======================================
        # ⭐ 리뷰 분석 후보 선정 점수
        # ======================================
        # 최종 추천 점수와 분리한다.
        # 직선거리는 후보 선정에도 넣지 않는다.
        # 위치는 검색 반경 필터로만 사용한다.
        #
        # 후보 우선순위:
        # - Google 평점 65
        # - 전체 평가 수 신뢰도 35
        #
        # 리뷰 분석은 반경별 상위 30곳까지 확인해
        # 후보 선절단으로 생기던 누락을 더 줄인다.
        # API 호출량과 탐색 폭 사이의 균형을 위해 30곳으로 제한한다.
        REVIEW_ANALYSIS_LIMIT_PER_RADIUS = 30

        def candidate_rating_score(rating):
            if rating is None:
                return 0.0
            try:
                return (
                    max(0.0, min(5.0, float(rating)))
                    / 5.0
                    * 65.0
                )
            except (TypeError, ValueError):
                return 0.0

        def candidate_review_count_score(review_count):
            try:
                count = max(0.0, float(review_count or 0))
            except (TypeError, ValueError):
                count = 0.0

            return (
                count / (count + 100.0)
            ) * 35.0

        def calculate_candidate_score(place):
            return round(
                candidate_rating_score(
                    place.get("rating")
                )
                + candidate_review_count_score(
                    place.get("userRatingCount", 0)
                ),
                1
            )

        for radius_index, search_radius in enumerate(search_radii):

            places_by_id = {}

            # ======================================
            # A. 직접 음식 검색: 하이브리드 검색
            #
            # 1) Text Search로 사용자가 입력한 메뉴 자체 검색
            # 2) Nearby restaurant를 인기순/거리순으로 넓게 검색
            # 3) Nearby 후보는 types/상호명/프랜차이즈로
            #    입력 메뉴와 맞는 곳만 추가
            # ======================================
            if is_custom_food_query:

                # ----------------------------------
                # A-1. Text Search
                # ----------------------------------
                text_places = fetch_text_search_restaurants(
                    custom_food_query,
                    search_radius
                )

                for place in text_places:
                    place_id = (
                        place.get("id")
                        or place.get("name")
                    )

                    if not place_id:
                        continue

                    place["_custom_search_source"] = (
                        "text_search"
                    )

                    places_by_id[
                        place_id
                    ] = place

                # ----------------------------------
                # A-2. 메뉴 전용 Google Place Type Nearby
                # ----------------------------------
                type_plan = get_custom_query_google_type_plan(
                    custom_food_query
                )

                type_search_types = set()

                if type_plan:
                    type_search_types.update(
                        type_plan.get(
                            "strong_types",
                            set()
                        )
                    )

                    type_search_types.update(
                        type_plan.get(
                            "discovery_types",
                            set()
                        )
                    )

                if type_search_types:
                    for rank_preference in [
                        "POPULARITY",
                        "DISTANCE",
                    ]:
                        places_body = {
                            "includedTypes": sorted(
                                type_search_types
                            ),
                            "maxResultCount": 20,
                            "rankPreference": rank_preference,
                            "locationRestriction": {
                                "circle": {
                                    "center": {
                                        "latitude": latitude,
                                        "longitude": longitude
                                    },
                                    "radius": search_radius
                                }
                            },
                            "languageCode": "ko"
                        }

                        try:
                            response = requests.post(
                                places_url,
                                headers=places_headers,
                                json=places_body,
                                timeout=20
                            )
                        except requests.RequestException:
                            continue

                        if response.status_code != 200:
                            continue

                        for place in response.json().get(
                            "places",
                            []
                        ):
                            place_id = (
                                place.get("id")
                                or place.get("name")
                            )

                            if not place_id:
                                continue

                            if place_id in places_by_id:
                                continue

                            if not matches_custom_query_locally(
                                place,
                                custom_food_query
                            ):
                                continue

                            place["_custom_search_source"] = (
                                "type_nearby"
                            )

                            places_by_id[
                                place_id
                            ] = place

                # ----------------------------------
                # A-3. 일반 restaurant Nearby 마지막 보완
                # ----------------------------------
                general_rank_preferences = (
                    ["DISTANCE"]
                    if type_search_types
                    else ["POPULARITY", "DISTANCE"]
                )

                for rank_preference in general_rank_preferences:
                    places_body = {
                        "includedTypes": [
                            "restaurant"
                        ],
                        "maxResultCount": 20,
                        "rankPreference": rank_preference,
                        "locationRestriction": {
                            "circle": {
                                "center": {
                                    "latitude": latitude,
                                    "longitude": longitude
                                },
                                "radius": search_radius
                            }
                        },
                        "languageCode": "ko"
                    }

                    try:
                        response = requests.post(
                            places_url,
                            headers=places_headers,
                            json=places_body,
                            timeout=20
                        )
                    except requests.RequestException:
                        continue

                    if response.status_code != 200:
                        continue

                    for place in response.json().get(
                        "places",
                        []
                    ):
                        place_id = (
                            place.get("id")
                            or place.get("name")
                        )

                        if not place_id:
                            continue

                        if place_id in places_by_id:
                            continue

                        if not matches_custom_query_locally(
                            place,
                            custom_food_query
                        ):
                            continue

                        place["_custom_search_source"] = (
                            "general_nearby_rescue"
                        )

                        places_by_id[
                            place_id
                        ] = place

                candidate_limit = (
                    MAX_CUSTOM_CANDIDATES_PER_RADIUS
                )

            # ======================================
            # B. 기본 10개 장르: 기존 Nearby 방식 유지
            # ======================================
            else:

                search_plans = (
                    [
                        (selected_types, "POPULARITY"),
                        (["restaurant"], "DISTANCE"),
                    ]
                    if food_category != "전체"
                    else [
                        (["restaurant"], "POPULARITY"),
                        (["restaurant"], "DISTANCE"),
                    ]
                )

                for search_types, rank_preference in search_plans:

                    places_body = {
                        "includedTypes": search_types,
                        "maxResultCount": 20,
                        "rankPreference": rank_preference,
                        "locationRestriction": {
                            "circle": {
                                "center": {
                                    "latitude": latitude,
                                    "longitude": longitude
                                },
                                "radius": search_radius
                            }
                        },
                        "languageCode": "ko"
                    }

                    try:
                        response = requests.post(
                            places_url,
                            headers=places_headers,
                            json=places_body,
                            timeout=20
                        )
                    except requests.RequestException:
                        continue

                    if response.status_code != 200:
                        continue

                    for place in response.json().get(
                        "places",
                        []
                    ):
                        place_id = (
                            place.get("id")
                            or place.get("name")
                        )

                        if (
                            place_id
                            and place_id not in places_by_id
                        ):
                            places_by_id[
                                place_id
                            ] = place

                candidate_limit = (
                    MAX_GENRE_CANDIDATES_PER_RADIUS
                )

            new_places = list(
                places_by_id.values()
            )[:candidate_limit]

            # --------------------------------------------------
            # ⚠️ 중요: Text Search는 locationBias이므로
            # 지정 반경 밖의 장소가 섞일 가능성이 있다.
            # 따라서 Text Search/Nearby를 합친 뒤 최종적으로
            # "사용자 위치 기준" 반경을 엄격하게 다시 확인한다.
            #
            # 직선거리는 여기서 "검색 범위 포함 여부"만 확인하고,
            # 후보 선정 점수와 최종 추천 점수에는 사용하지 않는다.
            # --------------------------------------------------
            def is_within_original_radius(place, radius_m):
                location = place.get("location", {})
                place_lat = location.get("latitude")
                place_lon = location.get("longitude")

                if place_lat is None or place_lon is None:
                    return False

                lat1 = math.radians(latitude)
                lat2 = math.radians(place_lat)
                dlat = math.radians(place_lat - latitude)
                dlon = math.radians(place_lon - longitude)

                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(lat1)
                    * math.cos(lat2)
                    * math.sin(dlon / 2) ** 2
                )
                c = 2 * math.atan2(
                    math.sqrt(a),
                    math.sqrt(1 - a)
                )

                straight_distance_m = 6371000 * c
                return straight_distance_m <= radius_m

            new_places = [
                place
                for place in new_places
                if is_within_original_radius(
                    place,
                    search_radius
                )
            ]

            # 이미 실제로 조건 확인/리뷰 분석까지 끝낸 장소만 제외한다.
            # 이전 반경에서 후보 상한 때문에 분석하지 못했던 장소는
            # 더 넓은 반경 단계에서 다시 후보가 될 수 있게 남겨둔다.
            new_restaurants = []

            for place in new_places:
                place_id = place.get("id") or place.get("name")

                if not place_id:
                    continue

                if place_id in checked_place_ids:
                    continue

                new_restaurants.append(place)

            # 명백한 비음식점 제거
            new_restaurants = [
                place
                for place in new_restaurants
                if is_actual_restaurant(place)
            ]

            # --------------------------------------
            # V48 직접 음식 검색 재검증
            #
            # Text Search + Nearby 보완 결과 전체에서
            # 상점/마트 등 실제 식음료 장소가 아닌 결과를 제거한다.
            #
            # 메뉴 관련성:
            # - Text Search 결과 → Google 검색 관련성
            # - Type Nearby → Google 세부 타입 + 자체 재검증
            # - 일반 Nearby → 상호명/프랜차이즈/strong type 직접 판별
            #
            # 여기서는 마지막으로 실제 식음료 장소인지 확인한다.
            # --------------------------------------
            if is_custom_food_query:
                new_restaurants = [
                    place
                    for place in new_restaurants
                    if is_food_service_place(
                        place
                    )
                ]

            # --------------------------------------
            # V48 장르 검증
            # primaryType/types → 프랜차이즈 사전
            # --------------------------------------
            if (
                not is_custom_food_query
                and food_category != "전체"
            ):
                new_restaurants = [
                    place
                    for place in new_restaurants
                    if matches_selected_genre(
                        place,
                        food_category
                    )
                ]

            if not new_restaurants:
                continue

            for place in new_restaurants:
                place["_candidate_score"] = calculate_candidate_score(
                    place
                )

            new_restaurants.sort(
                key=lambda place: place.get("_candidate_score", 0.0),
                reverse=True
            )

            # 리뷰 분석 후보를 반경별 최대 30개까지 확인한다.
            # 최종 출력은 여전히 추천 점수 상위 10개다.
            review_candidates = new_restaurants[
                :REVIEW_ANALYSIS_LIMIT_PER_RADIUS
            ]

            restaurants.extend(new_restaurants)

            if is_custom_food_query:
                st.info(
                    f"📍 {search_radius / 1000:.1f}km 범위에서 "
                    f'"{custom_food_query}" 관련 식당 '
                    f"{len(new_restaurants)}곳을 확인했습니다."
                )
            else:
                st.info(
                    f"📍 {search_radius / 1000:.1f}km 범위에서 "
                    f"새 음식점 {len(new_restaurants)}곳을 확인했습니다."
                )

            # --------------------------------------
            # 현재 반경의 가격 조건 확인
            # --------------------------------------
            price_candidates = []
            unknown_price_candidates = []

            if all_price_ranges_selected:
                price_candidates = list(review_candidates)

                for place in review_candidates:
                    place_id = place.get("id") or place.get("name")
                    if place_id:
                        checked_place_ids.add(place_id)

            else:
                for place in review_candidates:
                    place_id = place.get("id") or place.get("name")
                    google_range = get_google_price_range(place)

                    if google_range is not None:
                        if place_id:
                            checked_place_ids.add(place_id)

                        if google_price_range_matches(
                            {"restaurant": place},
                            selected_price_ranges
                        ):
                            price_candidates.append(place)
                    else:
                        unknown_price_candidates.append(place)

                # 가격 정보가 없는 식당은 리뷰에서 가격을 확인한다.
                # "현재 반경을 먼저 충분히 확인한다"는 원칙에 따라
                # 필요한 후보만 자르는 것이 아니라 이번 반경의
                # unknown 후보를 순서대로 확인한다.
                if unknown_price_candidates:
                    st.info(
                        f"💰 가격 정보가 없는 식당 "
                        f"{len(unknown_price_candidates)}곳의 리뷰에서 "
                        "가격 정보를 확인하고 있어요."
                    )

                    for place in unknown_price_candidates:
                        place_id = place.get("id") or place.get("name")
                        candidate_reviews = get_reviews_for_place(place)

                        if place_id:
                            checked_place_ids.add(place_id)

                        candidate_price = get_review_price_value(
                            candidate_reviews
                        )

                        if candidate_price is None:
                            continue

                        temp_result = {
                            "restaurant": place,
                            "reviews": candidate_reviews
                        }

                        if matches_selected_price_ranges(
                            temp_result,
                            selected_price_ranges
                        ):
                            place["_preloaded_reviews"] = candidate_reviews
                            price_candidates.append(place)

            # --------------------------------------
            # 현재 반경에서 조건에 맞는 식당은 모두 리뷰 분석
            # --------------------------------------
            for restaurant in price_candidates:

                result = make_review_result(
                    restaurant,
                    get_reviews_for_place(restaurant)
                )

                if result is None:
                    continue

                # 같은 place_id가 다시 들어오는 것을 방지
                result_id = result["restaurant"].get("id")

                if any(
                    existing["restaurant"].get("id") == result_id
                    for existing in restaurant_results
                ):
                    continue

                restaurant_results.append(result)

            # --------------------------------------
            # 현재 반경을 모두 분석한 뒤에만 확대 여부 결정
            # --------------------------------------
            if len(restaurant_results) >= SEARCH_TARGET_COUNT:
                break

            if radius_index == 0:
                st.info(
                    f"📍 1.5km 안에서 조건에 맞는 추천 식당이 "
                    f"{len(restaurant_results)}곳이라 "
                    "2.5km까지 검색 범위를 넓혀 추가로 찾아볼게요."
                )

        if not restaurants:
            st.warning(
                "주변에서 음식점을 찾지 못했습니다."
            )
            st.stop()

        if not restaurant_results:
            st.warning(
                "선택한 가격대와 평점 조건에 맞는 음식점을 찾지 못했습니다."
            )
            st.stop()

        search_label = (
            f'"{custom_food_query}"'
            if is_custom_food_query
            else food_category
        )

        st.success(
            f"🍴 {search_label} 검색에서 "
            f"추천 후보 {len(restaurant_results)}곳을 찾았습니다."
        )

        # ======================================
        # 🚶 실제 도보 거리 / 예상 시간 계산
        # ======================================
        #
        # 카카오 도보 길찾기 API
        # GET https://dapi.kakao.com/v2/routing/walk
        #
        # TOP10이 확정된 뒤 식당별로 1회씩 요청한다.
        # route_mode = SHORTEST 로 최단 도보 경로를 사용한다.

        def get_walking_route(
            origin_lat,
            origin_lon,
            destination_lat,
            destination_lon
        ):
            """
            카카오 도보 길찾기 API로
            실제 도보 거리(m), 예상 시간(초), 카카오맵 링크를 가져온다.

            API 오류가 나더라도 맛집 검색 전체가 멈추지 않도록
            실패 시 None을 반환한다.
            """
            if not KAKAO_REST_API_KEY:
                return None

            if (
                origin_lat is None
                or origin_lon is None
                or destination_lat is None
                or destination_lon is None
            ):
                return None

            url = (
                "https://dapi.kakao.com"
                "/v2/routing/walk"
            )

            headers = {
                "Authorization": (
                    f"KakaoAK {KAKAO_REST_API_KEY}"
                )
            }

            params = {
                "start_x": str(
                    origin_lon
                ),
                "start_y": str(
                    origin_lat
                ),
                "end_x": str(
                    destination_lon
                ),
                "end_y": str(
                    destination_lat
                ),
                "route_mode": "SHORTEST",
            }

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                if response.status_code != 200:
                    return None

                data = response.json()

                if data.get(
                    "status"
                ) != "OK":
                    return None

                route = data.get(
                    "route",
                    {}
                )

                properties = route.get(
                    "properties",
                    {}
                )

                distance_m = properties.get(
                    "totalDistance"
                )

                time_sec = properties.get(
                    "totalTime"
                )

                landing_url = properties.get(
                    "landingUrl"
                )

                if distance_m is None:
                    return None

                return {
                    "distance_m": int(
                        distance_m
                    ),
                    "time_sec": (
                        int(
                            time_sec
                        )
                        if time_sec is not None
                        else None
                    ),
                    "landing_url": (
                        landing_url
                        if landing_url
                        else None
                    ),
                }

            except (
                requests.RequestException,
                ValueError,
                TypeError
            ):
                return None


        def attach_walking_routes(
            origin_lat,
            origin_lon,
            results
        ):
            """
            최종 TOP10 식당에만 도보 경로 정보를 붙인다.
            후보 전체에 호출하지 않아 API 요청 수를 줄인다.
            """
            for result in results[:10]:
                restaurant = result.get(
                    "restaurant",
                    {}
                )

                location = restaurant.get(
                    "location",
                    {}
                )

                destination_lat = location.get(
                    "latitude"
                )

                destination_lon = location.get(
                    "longitude"
                )

                walking_route = get_walking_route(
                    origin_lat,
                    origin_lon,
                    destination_lat,
                    destination_lon
                )

                if walking_route is None:
                    result[
                        "walking_distance_m"
                    ] = None

                    result[
                        "walking_time_sec"
                    ] = None

                    result[
                        "walking_landing_url"
                    ] = None

                    continue

                result[
                    "walking_distance_m"
                ] = walking_route.get(
                    "distance_m"
                )

                result[
                    "walking_time_sec"
                ] = walking_route.get(
                    "time_sec"
                )

                result[
                    "walking_landing_url"
                ] = walking_route.get(
                    "landing_url"
                )


        # V71~V72 유지: API 오류로 리뷰를 확인하지 못한 식당은
        # 중립 점수를 임의로 주지 않고 이번 순위에서 제외했다는 사실만 안내한다.
        if review_api_error_places:
            st.warning(
                f"Google 리뷰를 불러오지 못한 식당 "
                f"{len(review_api_error_places)}곳은 이번 추천 순위에서 제외했어요. "
                "일시적인 API 오류였다면 잠시 후 다시 검색하면 포함될 수 있어요."
            )

        # ======================================
        # 4. 최종 추천점수 정렬 → TOP 10 확정
        # ======================================

        restaurant_results.sort(
            key=lambda x: (
                x.get("recommendation_score", 0),
                x.get("restaurant", {}).get(
                    "userRatingCount",
                    0
                ) or 0,
                x.get("restaurant", {}).get(
                    "rating",
                    0
                ) or 0,
            ),
            reverse=True
        )

        restaurant_results = (
            restaurant_results[:10]
        )

        # TOP10이 확정된 뒤에만 실제 도보 경로를 계산한다.
        # 후보 전체가 아니라 최대 10개 식당만 호출한다.
        attach_walking_routes(
            latitude,
            longitude,
            restaurant_results
        )


        # ======================================
        # 5. 출력 - V73 소프트 파스텔 카드 UI
        # ======================================

        result_context = (
            custom_food_query
            if is_custom_food_query
            else food_category
        )

        st.markdown(
            (
                '<div class="results-heading">'
                '<div class="section-kicker">RESULT</div>'
                '<div class="results-heading-title">'
                '🍽️ 추천 맛집 TOP 10'
                '</div>'
                '<div class="results-heading-subtitle">'
                f'{html.escape(str(location))} · '
                f'{html.escape(str(result_context))} · '
                f'가격대 {html.escape(get_price_filter_summary())}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        for i, result in enumerate(
            restaurant_results,
            start=1
        ):
            restaurant = result[
                "restaurant"
            ]

            reviews = result.get(
                "reviews",
                []
            )

            review_summary = result.get(
                "review_summary",
                {}
            )

            food_related_review_count = (
                result.get(
                    "food_related_review_count",
                    0
                )
            )

            name = (
                restaurant.get(
                    "displayName",
                    {}
                ).get(
                    "text",
                    "이름 없음"
                )
            )

            address = restaurant.get(
                "formattedAddress",
                "주소 정보 없음"
            )

            rating = restaurant.get(
                "rating"
            )

            rating_count = restaurant.get(
                "userRatingCount",
                0
            )

            maps_url = restaurant.get(
                "googleMapsUri"
            )

            recommendation_score = result.get(
                "recommendation_score",
                0
            )

            price_label = get_price_label(
                result
            )

            walking_distance_label = format_distance(
                result.get(
                    "walking_distance_m"
                )
            )

            walking_time_label = format_walking_time(
                result.get(
                    "walking_time_sec"
                )
            )

            walking_landing_url = result.get(
                "walking_landing_url"
            )

            rating_label = (
                f"{rating:.1f}"
                if isinstance(
                    rating,
                    (int, float)
                )
                else "정보 없음"
            )

            # ------------------------------
            # 카드
            # ------------------------------
            with st.container(
                border=True
            ):
                if i == 1:
                    rank_html = (
                        '<span class="result-rank winner-rank">'
                        '🥇 TOP PICK'
                        '</span>'
                    )
                    name_class = "restaurant-name winner-name"
                elif i == 2:
                    rank_html = (
                        '<span class="result-rank">'
                        '🥈 2위'
                        '</span>'
                    )
                    name_class = "restaurant-name"
                elif i == 3:
                    rank_html = (
                        '<span class="result-rank">'
                        '🥉 3위'
                        '</span>'
                    )
                    name_class = "restaurant-name"
                else:
                    rank_html = (
                        '<span class="result-rank">'
                        f'{i}위'
                        '</span>'
                    )
                    name_class = "restaurant-name"

                st.markdown(
                    (
                        '<div class="result-header">'
                        '<div class="result-title-wrap">'
                        f'{rank_html}'
                        f'<div class="{name_class}">'
                        f'{html.escape(str(name))}'
                        '</div>'
                        '</div>'
                        '<div class="score-badge">'
                        '<div class="score-number">'
                        f'{recommendation_score:.1f}'
                        '</div>'
                        '<div class="score-label">'
                        '추천 점수 / 100'
                        '</div>'
                        '</div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown(
                    (
                        '<div class="meta-grid">'

                        '<div class="meta-item">'
                        '<div class="meta-label">GOOGLE 평점</div>'
                        '<div class="meta-value">'
                        f'⭐ {html.escape(rating_label)}'
                        '</div>'
                        '</div>'

                        '<div class="meta-item">'
                        '<div class="meta-label">리뷰</div>'
                        '<div class="meta-value">'
                        f'💬 {rating_count:,}개'
                        '</div>'
                        '</div>'

                        '<div class="meta-item">'
                        '<div class="meta-label">가격대</div>'
                        '<div class="meta-value">'
                        f'💰 {html.escape(str(price_label))}'
                        '</div>'
                        '</div>'

                        '<div class="meta-item">'
                        '<div class="meta-label">도보</div>'
                        '<div class="meta-value">'
                        f'🚶 {html.escape(str(walking_distance_label))}'
                        f' · {html.escape(str(walking_time_label))}'
                        '</div>'
                        '</div>'

                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown(
                    (
                        '<div class="address-line">'
                        '📍 '
                        f'{html.escape(str(address))}'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

                with st.expander(
                    "상세 분석 보기"
                ):
                    analysis_tab, reviews_tab, route_tab = st.tabs(
                        [
                            "📊 분석",
                            f"📝 리뷰 {len(reviews)}",
                            "🗺️ 길찾기",
                        ]
                    )

                    # --------------------------
                    # 분석 탭
                    # --------------------------
                    with analysis_tab:
                        st.markdown(
                            (
                                '<div class="detail-summary">'
                                f'🍴 <b>음식 관련 리뷰</b> '
                                f'{food_related_review_count}/{len(reviews)}개'
                                '</div>'
                            ),
                            unsafe_allow_html=True,
                        )

                        review_fetch_status = result.get(
                            "review_fetch_status",
                            "unknown"
                        )

                        if review_fetch_status == "api_error":
                            st.warning(
                                "Google 리뷰 정보를 불러오는 중 오류가 발생해 "
                                "리뷰 분석이 제한될 수 있어요."
                            )
                        elif result.get(
                            "review_count",
                            0
                        ) == 0:
                            st.info(
                                "표시 가능한 Google 리뷰 원문이 없어 "
                                "리뷰 분석 정보가 제한적입니다."
                            )

                        st.markdown(
                            "#### 리뷰 종합 분석"
                        )

                        if reviews:
                            render_review_summary_dashboard(
                                review_summary
                            )
                        else:
                            st.info(
                                "분석할 Google 리뷰가 없습니다."
                            )

                    # --------------------------
                    # 리뷰 탭
                    # --------------------------
                    with reviews_tab:
                        if not reviews:
                            st.info(
                                "표시할 Google 리뷰가 없습니다."
                            )

                        for review_number, review in enumerate(
                            reviews,
                            start=1
                        ):
                            review_text = (
                                review.get(
                                    "text",
                                    {}
                                ).get(
                                    "text",
                                    ""
                                )
                            )

                            review_rating = review.get(
                                "rating"
                            )

                            if not review_text:
                                continue

                            analysis = analyze_review(
                                review_text,
                                review_rating
                            )

                            review_head_col, review_tag_col = st.columns(
                                [3, 2],
                                vertical_alignment="center",
                            )

                            with review_head_col:
                                if review_rating is not None:
                                    st.markdown(
                                        f"**리뷰 {review_number} · ⭐ {review_rating}**"
                                    )
                                else:
                                    st.markdown(
                                        f"**리뷰 {review_number}**"
                                    )

                            with review_tag_col:
                                if analysis[
                                    "음식 관련"
                                ]:
                                    st.caption(
                                        "🍴 음식 관련 리뷰"
                                    )
                                else:
                                    st.caption(
                                        "⚪ 음식 관련성 낮음"
                                    )

                            render_review_text(
                                review_text
                            )

                            detected = []

                            for category in REVIEW_RULES.keys():
                                data = analysis[
                                    category
                                ]

                                if (
                                    data["result"]
                                    != "언급 없음"
                                ):
                                    emoji = CATEGORY_EMOJIS[
                                        category
                                    ]

                                    detected.append(
                                        f"{emoji} {category}: "
                                        f"{data['result']}"
                                    )

                            if detected:
                                st.caption(
                                    " · ".join(
                                        detected
                                    )
                                )

                            if review_number < len(
                                reviews
                            ):
                                st.divider()

                    # --------------------------
                    # 길찾기 탭
                    # --------------------------
                    with route_tab:
                        route_col, map_col = st.columns(
                            2
                        )

                        with route_col:
                            st.markdown(
                                f"**🚶 도보 {walking_distance_label}**"
                            )
                            st.caption(
                                f"예상 소요 시간 {walking_time_label}"
                            )

                            if walking_landing_url:
                                st.link_button(
                                    "카카오맵 도보 경로",
                                    walking_landing_url,
                                    use_container_width=True,
                                )
                            else:
                                st.info(
                                    "카카오 도보 경로 정보를 불러오지 못했습니다."
                                )

                        with map_col:
                            st.markdown(
                                "**📍 식당 위치 확인**"
                            )
                            st.caption(
                                "Google 지도에서 상세 위치와 장소 정보를 확인하세요."
                            )

                            if maps_url:
                                st.link_button(
                                    "Google 지도에서 보기",
                                    maps_url,
                                    use_container_width=True,
                                )

