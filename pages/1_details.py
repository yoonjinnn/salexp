import streamlit as st
import pandas as pd
import datetime
import json
import os
import requests
import sqlite3 # sqlite DB 사용 시
import altair as alt

# API URL 중앙 설정
API_URL = "http://localhost:8000/api/games/"

# sqlite 연결 함수
def load_data_from_sqlite(db_path="mainDB.db"):
    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM game;"  # 테이블 이름이 games_game인 경우
    df = pd.read_sql_query(query, conn)
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
            "game_img_url": "이미지",
            "game_url": "링크",
            "collect_date": "수집일"
        })
    
    # 장르와 언어를 리스트로 변환
    df["장르"] = df["장르"].fillna("").apply(lambda x: [g.strip() for g in x.split(",")] if x else [])
    df["언어"] = df["언어"].fillna("").apply(lambda x: [l.strip() for l in x.split(",")] if x else [])

    # 할인율 계산 필드 추가
    df['정가'] = df['정가'].replace(r'[\₩,]', '', regex=True).astype(int)
    df['할인가'] = df['할인가'].replace(r'[\₩,]', '', regex=True).astype(int)
    df['수집일'] = pd.to_datetime(df['수집일'])
    df["할인율"] = ((df["정가"] - df["할인가"]) / df["정가"] * 100).round(2)
    
    conn.close()

    return df

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
#df = load_data()
df = load_data_from_sqlite() # sqlite DB 사용 시
game = df[df["게임이름"] == st.session_state.selected_game].iloc[0]
key = game['게임이름']
#for test
#game = df[df["게임이름"]=='슈퍼 마리오 파티 잼버리'].iloc[0]
#key = '슈퍼 마리오 파티 잼버리'


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


######chart######
game_name = game['게임이름']
product_type = game['상품유형']
genre_list = game['장르']
chart_df=df
for g in genre_list:
    g = str(g)
    g = g.replace('[','').replace("'",'').replace(']','')
    # for str
    #mean = df[df['장르'].str.contains(g)].groupby('수집일')['할인가'].mean().reset_index()
    mean = df[df['장르'].str.contains(g, na=False)].groupby('수집일')['할인가'].mean().reset_index()
    mean.rename(columns={'할인가': f'{g}_mean'}, inplace=True)
    chart_df = pd.merge(chart_df, mean, on='수집일', how='left')
                            
temp_df = chart_df[(chart_df['게임이름'] == game_name) & (chart_df['상품유형'] == product_type)].sort_values(by='수집일')
price_df = temp_df.drop(columns=['게임이름', '할인시작일', '할인종료일', '장르', '발매일', '메이커', '플레이인원', '상품유형', '언어', '이미지', '링크'])
price_df['수집일'] = pd.to_datetime(price_df['수집일']).dt.date.astype(str)
price_df.set_index('수집일', inplace=True)

price_df['max_price'] = price_df['할인가'].max()
price_df['min_price'] = price_df['할인가'].min()
max_price = price_df['할인가'].max().astype(str)
min_price = price_df['할인가'].min().astype(str)

# Streamlit에서 라인 차트를 그리기
price_df = price_df.drop(columns=['할인율'])
st.title("price graph")
st.line_chart(price_df)

plot_df = price_df.reset_index().melt(id_vars='수집일', 
                                      value_vars=['할인가', 'max_price', 'min_price'],
                                      var_name='type', value_name='price')

# Altair 차트 생성
chart = alt.Chart(plot_df).mark_line().encode(
    x=alt.X('수집일:T', axis=alt.Axis(format='%Y-%m-%d', labelAngle=0)),
    y=alt.Y('price:Q', scale=alt.Scale(zero=False)),
    color=alt.Color('type:N', legend=alt.Legend(orient='bottom', title="")),
    strokeDash=alt.condition(
        alt.datum.type == 'discount_price',
        alt.value([1, 0]),  # 실선
        alt.value([4, 4])   # 점선 
    )
).properties(
    title="price graph"
)

st.altair_chart(chart, use_container_width=True)

#price_data = pd.DataFrame({
#    '날짜': pd.date_range(end=datetime.datetime.today(), periods=10),
#    '가격': [game["할인가"] + i * 200 for i in range(10)][::-1]
#}).set_index("날짜")
#st.line_chart(price_data)

# 메인 페이지로 돌아가기
if st.button("⬅ 메인으로 돌아가기"):
    st.switch_page("app.py")
