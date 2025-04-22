import streamlit as st
import pandas as pd
import datetime
import json
import os
import requests
import sqlite3 # sqlite DB 사용 시

# API URL 중앙 설정
API_URL = "http://localhost:8000/api/games/"

# sqlite 연결 함수
def load_data_from_sqlite(db_path="db.sqlite3"):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM games_game;"  # 테이블 이름이 games_game인 경우
    df = pd.read_sql_query(query, conn)
    conn.close()

# API를 통해 게임 데이터 불러오기
@st.cache_data
def load_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
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
        df['장르'] = df['장르'].apply(lambda x: ', '.join(x))
        df['언어'] = df['언어'].apply(lambda x: ', '.join(x))
        df["할인율"] = ((df["정가"] - df["할인가"]) / df["정가"] * 100).round(2)
        return df
    else:
        st.error("게임 데이터를 불러오지 못했습니다.")
        return pd.DataFrame()

# 즐겨찾기 저장 함수
def save_favorites():
    with open("data/favorites.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.favorites, f, ensure_ascii=False, indent=2)

# 데이터 및 세션 초기화
if "favorites" not in st.session_state:
    if os.path.exists("data/favorites.json"):
        with open("data/favorites.json", "r", encoding="utf-8") as f:
            st.session_state.favorites = json.load(f)
    else:
        st.session_state.favorites = []

if "selected_game" not in st.session_state:
    st.error("선택된 게임이 없습니다. 메인 페이지에서 게임을 선택해주세요.")
    st.stop()

# 데이터 가져오기 및 게임 선택
df = load_data()
# df = load_data_from_sqlite() # sqlite DB 사용 시
game = df[df["게임이름"] == st.session_state.selected_game].iloc[0]
key = game['게임이름']

# 게임 상세 정보 출력
st.title(f"🎮 {game['게임이름']} 상세 정보")
st.image(game["이미지"], width=300)
st.write(f"**정가:** {game['정가']}원")
st.write(f"**할인가:** {game['할인가']}원")
st.write(f"**할인율:** {game['할인율']}%")
st.write(f"**할인 기간:** {game['할인시작일']} ~ {game['할인종료일']}")
st.write(f"**장르:** {game['장르']}")
st.write(f"**발매일:** {game['발매일']}")
st.write(f"**메이커:** {game['메이커']}")
st.write(f"**플레이 인원수:** {game['플레이인원']}")
st.write(f"**상품 유형:** {game['상품유형']}")
st.write(f"**지원 언어:** {game['언어']}")
st.markdown(f"[🔗 구매 페이지 바로가기]({game['링크']})")

# 즐겨찾기 토글 버튼
if key in st.session_state.favorites:
    if st.button(f"❌ 즐겨찾기 삭제", key=f"unfav_{key}_detail"):
        st.session_state.favorites.remove(key)
        save_favorites()
        st.success(f"{key}을(를) 즐겨찾기에서 삭제했어요!")
else:
    if st.button(f"⭐ 즐겨찾기 추가", key=f"fav_{key}_detail"):
        st.session_state.favorites.append(key)
        save_favorites()
        st.success(f"{key}을(를) 즐겨찾기에 추가했어요!")

# 예시 시각화 그래프 (가상의 가격 추이)
price_data = pd.DataFrame({
    '날짜': pd.date_range(end=datetime.datetime.today(), periods=10),
    '가격': [game["할인가"] + i * 200 for i in range(10)][::-1]
}).set_index("날짜")
st.line_chart(price_data)

# 메인 페이지로 돌아가기
if st.button("⬅ 메인으로 돌아가기"):
    st.switch_page("app.py")
