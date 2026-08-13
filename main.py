```python
import streamlit as st
import requests
from urllib.parse import unquote
from math import radians, sin, cos, sqrt, atan2


# ==========================================
# 기본 설정
# ==========================================

st.set_page_config(
    page_title="AI 맛집 추천",
    page_icon="🍽️"
)

st.title("🍽️ AI 맛집 추천")
st.write(
    "내 주변 음식점을 거리와 모범음식점 정보를 분석하여 추천합니다."
)


# ==========================================
# API 키
# ==========================================

KAKAO_API_KEY = st.secrets["KAKAO_REST_API_KEY"]

PUBLIC_DATA_API_KEY = unquote(
    st.secrets["PUBLIC_DATA_API_KEY"]
)


# ==========================================
# 거리 계산
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c * 1000


# ==========================================
# 거리 점수
# ==========================================

def get_distance_score(distance):

    if distance <= 100:
        return 50
    elif distance <= 300:
        return 40
    elif distance <= 500:
        return 30
    elif distance <= 1000:
        return 20
    else:
        return 10


# ==========================================
# 음식점 이름 정리
# ==========================================

def clean_name(name):

    if not name:
        return ""

    name = name.lower()

    remove_words = [
        " ",
        "점",
        "본점",
        "본관",
        "지점",
        "점포"
    ]

    for word in remove_words:
        name = name.replace(word, "")

    return name


# ==========================================
# 사용자 입력
# ==========================================

location = st.text_input(
    "📍 어디에서 먹을까요?",
    "강남역"
)

food_type = st.selectbox(
    "🍴 어떤 음식을 먹을까요?",
    [
        "전체",
        "한식",
        "중식",
        "일식",
        "양식",
        "치킨",
        "분식",
        "카페"
    ]
)


# ==========================================
# 맛집 찾기
# ==========================================

if st.button("🔍 맛집 찾기"):

    if food_type == "전체":
        query = location
    else:
        query = location + " " + food_type


    # ======================================
    # 1. 검색 위치 찾기
    # ======================================

    address_url = (
        "https://dapi.kakao.com/v2/local/"
        "search/keyword.json"
    )

    kakao_headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}"
    }

    address_params = {
        "query": location,
        "size": 1
    }

    try:

        address_response = requests.get(
            address_url,
            headers=kakao_headers,
            params=address_params,
            timeout=15
        )

    except requests.exceptions.RequestException:

        st.error(
            "❌ 위치 검색 서버에 연결하지 못했습니다."
        )

        st.stop()


    if address_response.status_code != 200:

        st.error("❌ 입력한 위치를 찾지 못했습니다.")

        st.stop()


    address_data = address_response.json()

    address_documents = address_data.get(
        "documents",
        []
    )

    if not address_documents:

        st.error("❌ 검색 결과가 없습니다.")

        st.stop()


    center = address_documents[0]

    center_lat = float(center["y"])
    center_lon = float(center["x"])

    st.success(
        f"📍 {location} 위치를 찾았습니다."
    )


    # ======================================
    # 2. 공공데이터에서 모범음식점 가져오기
    # ======================================

    st.subheader("🏆 모범음식점 데이터 분석 중...")


    # HTTPS 사용
    public_url = (
        "https://apis.data.go.kr/"
        "1741000/excellent_restaurant_info/info"
    )


    public_params = {
        "serviceKey": PUBLIC_DATA_API_KEY,
        "pageNo": "1",
        "numOfRows": "1000",
        "returnType": "JSON"
    }


    excellent_names = set()

    public_data_success = False


    try:

        public_response = requests.get(
            public_url,
            params=public_params,
            timeout=30
        )


        if public_response.status_code == 200:

            try:

                public_data = public_response.json()

                body = public_data.get(
                    "body",
                    {}
                )

                items = body.get(
                    "items",
                    []
                )

                if isinstance(items, dict):

                    items = items.get(
                        "item",
                        []
                    )

                if isinstance(items, dict):

                    items = [items]


                for item in items:

                    name = (
                        item.get("restaurantName")
                        or item.get("RESTAURANT_NM")
                        or item.get("업소명")
                        or item.get("업소명칭")
                        or ""
                    )


                    if name:

                        excellent_names.add(
                            clean_name(name)
                        )


                public_data_success = True


            except Exception:

                public_data_success = False


    except requests.exceptions.ConnectTimeout:

        public_data_success = False


    except requests.exceptions.RequestException:

        public_data_success = False


    # ======================================
    # 공공데이터 결과 표시
    # ======================================

    if public_data_success:

        st.success(
            f"🏆 모범음식점 데이터 {len(excellent_names):,}건 분석 완료"
        )

    else:

        st.warning(
            "⚠️ 현재 공공데이터 서버에 연결하지 못했습니다. "
            "거리 기반 추천을 계속 진행합니다."
        )


    # ======================================
    # 3. 카카오 음식점 검색
    # ======================================

    st.subheader("🍴 주변 음식점")


    restaurant_url = (
        "https://dapi.kakao.com/v2/local/"
        "search/keyword.json"
    )


    restaurant_params = {
        "query": query,
        "x": center_lon,
        "y": center_lat,
        "radius": 2000,
        "size": 10,
        "sort": "distance"
    }


    try:

        restaurant_response = requests.get(
            restaurant_url,
            headers=kakao_headers,
            params=restaurant_params,
            timeout=15
        )

    except requests.exceptions.RequestException:

        st.error(
            "❌ 음식점 검색 서버에 연결하지 못했습니다."
        )

        st.stop()


    if restaurant_response.status_code != 200:

        st.error("❌ 음식점 검색에 실패했습니다.")

        st.write(
            "오류 코드:",
            restaurant_response.status_code
        )

        st.stop()


    restaurant_data = restaurant_response.json()

    restaurants = restaurant_data.get(
        "documents",
        []
    )


    if not restaurants:

        st.warning(
            "검색된 음식점이 없습니다."
        )

        st.stop()


    # ======================================
    # 4. 음식점 점수 계산
    # ======================================

    results = []


    for restaurant in restaurants:

        restaurant_lat = float(
            restaurant["y"]
        )

        restaurant_lon = float(
            restaurant["x"]
        )


        # 실제 거리
        distance = calculate_distance(
            center_lat,
            center_lon,
            restaurant_lat,
            restaurant_lon
        )


        # 거리 점수
        distance_score = get_distance_score(
            distance
        )


        # 모범음식점 여부
        restaurant_name = clean_name(
            restaurant.get(
                "place_name",
                ""
            )
        )


        is_excellent = False


        if public_data_success:

            for excellent_name in excellent_names:

                if (
                    restaurant_name in excellent_name
                    or excellent_name in restaurant_name
                ):

                    is_excellent = True

                    break


        # 모범음식점 점수
        if is_excellent:

            excellent_score = 50

        else:

            excellent_score = 0


        # 최종 점수
        total_score = (
            distance_score
            + excellent_score
        )


        results.append({

            "restaurant": restaurant,

            "distance": distance,

            "distance_score": distance_score,

            "is_excellent": is_excellent,

            "excellent_score": excellent_score,

            "total_score": total_score

        })


    # ======================================
    # 5. 최종점수 높은 순 정렬
    # ======================================

    results.sort(
        key=lambda x: x["total_score"],
        reverse=True
    )


    # ======================================
    # 🥇 오늘의 1위
    # ======================================

    winner = results[0]

    winner_restaurant = winner["restaurant"]


    st.success(
        "🥇 오늘의 추천 맛집"
    )


    st.markdown(
        f"""
        ## 🍽️ {winner_restaurant['place_name']}

        ### ⭐ 최종 추천점수: {winner['total_score']}점

        📏 거리: **{winner['distance']:.0f}m**

        📊 거리 점수: **{winner['distance_score']}점**

        🏆 모범음식점:
        **{"✅ YES" if winner['is_excellent'] else "❌ NO"}**

        🏆 모범음식점 점수:
        **{winner['excellent_score']}점**
        """
    )


    if winner_restaurant.get("place_url"):

        st.link_button(
            "🗺️ 1위 음식점 카카오맵에서 보기",
            winner_restaurant["place_url"]
        )


    st.divider()


    # ======================================
    # 6. 전체 순위
    # ======================================

    st.subheader("🏅 전체 추천 순위")


    for i, result in enumerate(
        results,
        start=1
    ):

        restaurant = result["restaurant"]


        if i == 1:

            medal = "🥇"

        elif i == 2:

            medal = "🥈"

        elif i == 3:

            medal = "🥉"

        else:

            medal = ""


        st.markdown(
            f"""
            ### {medal} {i}위 — {restaurant['place_name']}

            ⭐ 최종점수: **{result['total_score']}점**

            📏 거리: {result['distance']:.0f}m

            📊 거리점수: {result['distance_score']}점

            🏆 모범음식점:
            {"✅" if result['is_excellent'] else "❌"}
            """
        )


        if restaurant.get("road_address_name"):

            st.write(
                "📍",
                restaurant["road_address_name"]
            )


        if restaurant.get("phone"):

            st.write(
                "📞",
                restaurant["phone"]
            )


        if restaurant.get("place_url"):

            st.link_button(
                "🗺️ 카카오맵에서 보기",
                restaurant["place_url"]
            )


        st.divider()
```
