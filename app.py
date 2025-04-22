# app.py (메인 페이지)
import streamlit as st
import pandas as pd
import requests
import sqlite3 # sqlite DB 사용 시


# API URL 중앙 설정
API_URL = "http://localhost:8000/api/games/"
API_GENRE_URL = "http://localhost:8000/api/genres/"
API_LANG_URL = "http://localhost:8000/api/languages/"

# sqlite 연결 함수
def load_data_from_sqlite(db_path="db.sqlite3"):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM games_game;"  # 테이블 이름이 games_game인 경우
    df = pd.read_sql_query(query, conn)
    conn.close()

    # 컬럼명 변환 (API에서 변환했던 것처럼)

    return df

# API에서 게임 데이터 로딩 함수
@st.cache_data
def load_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        # API 응답 컬럼명을 한글로 매핑
        df = df.rename(columns={
            "game_name": "게임이름",
            "original_price": "정가",
            "discount_price": "할인가",
            "discount_startdate": "할인시작일",
            "discount_enddate": "할인종료일",
            "genre": "장르",
            "release_date": "발매일",
            "maker": "메이커",
            "play_number": "플레이인원",
            "product_type": "상품유형",
            "game_language": "언어",
            "game_image_url": "이미지",
            "game_url": "링크"
        })

        # # 장르와 언어를 리스트로 변환
        # df["장르"] = df["장르"].fillna("").apply(lambda x: [g.strip() for g in x.split(",")] if x else [])
        # df["언어"] = df["언어"].fillna("").apply(lambda x: [l.strip() for l in x.split(",")] if x else [])

        # 할인율 계산 필드 추가
        df["할인율"] = ((df["정가"] - df["할인가"]) / df["정가"] * 100).round(2)
        return df
    else:
        st.error("게임 데이터를 불러오지 못했습니다.")
        return pd.DataFrame()

@st.cache_data
def load_genres():
    response = requests.get(API_GENRE_URL)
    if response.status_code == 200:
        data = response.json()
        return [g.get('genre_name') for g in data]
    st.error("장르 데이터를 불러오지 못했습니다.")

@st.cache_data
def load_languages():
    response = requests.get(API_LANG_URL)
    if response.status_code == 200:
        data = response.json()
        return [l.get('language') for l in data]
    st.error("언어 데이터를 불러오지 못했습니다.")


# 데이터 로딩
df = load_data()
# df = load_data_from_sqlite() # sqlite DB 사용 시
genre_list = load_genres()
lang_list = load_languages()

# 페이지 헤더
st.title("🎮 닌텐도 게임 가격 비교 및 검색")
st.write("게임 이름으로 검색하거나 장르/제작사로 필터링, 정렬 기준으로 리스트를 재정렬할 수 있어요.")

# 필터 입력을 메인 영역에 표시
with st.container():
    st.markdown("### 🔍 검색 및 필터")
    # 첫 번째 줄: 검색 + 정렬
    row1_col1, row1_col2 = st.columns([3, 3])
    with row1_col1:
        search = st.text_input("게임 이름 검색", placeholder="예: 젤다")
    with row1_col2:
        sort_option = st.selectbox("정렬 기준", ["기본", "할인율 높은 순", "할인가 낮은 순"])

    # 두 번째 줄: 장르 + 제작사 + 언어
    row2_col1, row2_col2, row2_col3 = st.columns([2, 2, 2])
    with row2_col1:
        genre_options = sorted(genre_list)
        selected_genre = st.multiselect("장르 선택", options=genre_options)
    with row2_col2:
        maker_options = sorted(df["메이커"].dropna().unique())
        selected_maker = st.multiselect("제작사 선택", options=maker_options)
    with row2_col3:
        language_options = sorted(lang_list)
        selected_language = st.multiselect("지원 언어 선택", options=language_options)

# 필터 적용
results = df.copy()
if search:
    results = results[results["게임이름"].str.contains(search, case=False, na=False)]
if selected_genre:
    results = results[results["장르"].apply(lambda genres: any(g in genres for g in selected_genre))]
if selected_maker:
    results = results[results["메이커"].isin(selected_maker)]
if selected_language:
    results = results[results["언어"].apply(lambda langs: any(l in langs for l in selected_language))]
if sort_option == "할인율 높은 순":
    results = results.sort_values("할인율", ascending=False)
elif sort_option == "할인가 낮은 순":
    results = results.sort_values("할인가")

# 게임 목록 출력 (3열 카드 배열)
st.markdown("### 🎯 검색 결과")

# 카드 3개 단위로 행 구성
rows = [results.iloc[i:i+3] for i in range(0, len(results), 3)]
for row_group in rows:
    cols = st.columns(3)
    for idx, (_, row) in enumerate(row_group.iterrows()):
        with cols[idx]:
            st.image(row["이미지"], width=180)
            st.write(f"**{row['게임이름']}**")
            if row["정가"] == row["할인가"]:
                st.write(f"💰 정가: {int(row['정가'])}원")
            else:
                st.write(f"💰 할인가: {int(row['할인가'])}원")
                st.write(f"🔥 할인율: {row['할인율']}%")
            # 상세 보기 버튼
            if st.button("📄 상세 보기", key=f"detail_{row['게임이름']}"):
                st.session_state.selected_game = row["게임이름"]
                st.switch_page("pages/1_details.py")

