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
            "player_number": "플레이인원",
            "product_type": "상품유형",
            "game_language": "언어",
            "game_image_url": "이미지",
            "game_url": "링크"
        })
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

if df.empty:
    st.warning("⭐ 즐겨찾기한 게임이 없습니다.")
else:
    with st.container():
        st.markdown("### 🔍 검색 및 필터")
        show_only_discounted = st.checkbox("할인 중인 제품만 보기")
        row1_col1, row1_col2 = st.columns([3, 3])
        with row1_col1:
            search = st.text_input("게임 이름 검색")
        with row1_col2:
            sort_option = st.selectbox("정렬 기준", ["기본", "할인율 높은 순", "가격 낮은 순"])

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
    if show_only_discounted:
        results = results[results["할인율"] > 0]
    if sort_option == "할인율 높은 순":
        results = results.sort_values("할인율", ascending=False)
    elif sort_option == "가격 낮은 순":
        results = results.sort_values("할인가")

    st.markdown("### 🎯 즐겨찾기 결과")

    if results.empty:
        st.warning("🔍 검색 결과가 없습니다.")
    else:
        items_per_page = 9
        if 'page' not in st.session_state:
            st.session_state.page = 1

        total_pages = (len(results) - 1) // items_per_page + 1

        page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
        with page_col1:
            if st.button("⬅ 이전") and st.session_state.page > 1:
                st.session_state.page -= 1
                st.rerun()
        with page_col2:
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>현재 페이지 : {st.session_state.page} / 최대 {total_pages}</div>", unsafe_allow_html=True)
            go_to = st.number_input("페이지 번호로 이동", min_value=1, max_value=total_pages if total_pages > 0 else 1, step=1, value=st.session_state.page if total_pages > 0 else 1, key="goto_input_bm")
            if st.button("이동"):
                if 1 <= go_to <= total_pages:
                    st.session_state.page = go_to
                    st.rerun()
                else:
                    st.error("없는 페이지입니다.")
        with page_col3:
            if st.button("다음 ➡") and st.session_state.page < total_pages:
                st.session_state.page += 1
                st.rerun()

        start = (st.session_state.page - 1) * items_per_page
        end = start + items_per_page
        paged_results = results.iloc[start:end]

        rows = [paged_results.iloc[i:i+3] for i in range(0, len(paged_results), 3)]
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
                        if pd.notna(row["할인종료일"]):
                            try:
                                end_date = pd.to_datetime(row["할인종료일"]).strftime("%Y-%m-%d")
                                st.write(f"🕒 할인 마감일: {end_date}")
                            except:
                                st.write(f"🕒 할인 마감일: {row['할인종료일']}")

                    if st.button("📄 상세 보기", key=f"detail_{row['게임이름']}_{start}"):
                        st.session_state.selected_game = row["게임이름"]
                        st.switch_page("pages/1_details.py")