import streamlit as st
import pandas as pd
import requests
import json
import os

API_URL = "http://localhost:8000/api/games/"

@st.cache_data
def load_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
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

        # df["장르"] = df["장르"].fillna("").apply(lambda x: [g.strip() for g in x.split(",")] if x else [])
        # df["언어"] = df["언어"].fillna("").apply(lambda x: [l.strip() for l in x.split(",")] if x else [])
        df["할인율"] = ((df["정가"] - df["할인가"]) / df["정가"] * 100).round(2)
        return df
    else:
        st.error("게임 데이터를 불러오지 못했습니다.")
        return pd.DataFrame()

# 즐겨찾기 불러오기
if os.path.exists("data/favorites.json"):
    with open("data/favorites.json", "r", encoding="utf-8") as f:
        favorites = json.load(f)
else:
    favorites = []

df = load_data()
df = df[df["게임이름"].isin(favorites)]

st.title("⭐ 즐겨찾기 게임 목록")

# 필터 영역
with st.container():
    st.markdown("### 🔍 검색 및 필터")

    row1_col1, row1_col2 = st.columns([3, 3])
    with row1_col1:
        search = st.text_input("게임 이름 검색")
    with row1_col2:
        sort_option = st.selectbox("정렬 기준", ["기본", "할인율 높은 순", "할인가 낮은 순"])

    row2_col1, row2_col2, row2_col3 = st.columns([2, 2, 2])
    with row2_col1:
        genre_options = sorted({g for genres in df["장르"] for g in genres})
        selected_genre = st.multiselect("장르 선택", options=genre_options)
    with row2_col2:
        maker_options = sorted(df["메이커"].dropna().unique())
        selected_maker = st.multiselect("제작사 선택", options=maker_options)
    with row2_col3:
        language_options = sorted({l for langs in df["언어"] for l in langs})
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

# 출력
st.markdown("### 🎯 즐겨찾기 결과")

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
                if pd.notna(row["할인시작일"]) or pd.notna(row["할인종료일"]):
                    start = row["할인시작일"] if pd.notna(row["할인시작일"]) else "?"
                    end = row["할인종료일"] if pd.notna(row["할인종료일"]) else "?"
                    st.write(f"🕒 할인 기간: {start} ~ {end}")

            if st.button("📄 상세 보기", key=f"detail_{row['게임이름']}"):
                st.session_state.selected_game = row["게임이름"]
                st.switch_page("pages/1_details.py")