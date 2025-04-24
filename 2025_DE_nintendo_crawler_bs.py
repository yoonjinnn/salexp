import requests
import sqlite3
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

def format_discount_date(raw_text):
    try:
        dt = datetime.strptime(raw_text.strip(), "%Y/%m/%d %H:%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"[오류] 날짜 변환 실패: {raw_text} → {e}")
        return None

BASE_URL = "https://store.nintendo.co.kr"
LIST_URL_TEMPLATE = BASE_URL + "/all-product?p={page}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# 1. SQLite3 DB 연결 및 테이블 생성
def init_db():
    conn = sqlite3.connect("mainDB.db")
    cur = conn.cursor() 

    cur.execute('''
        CREATE TABLE IF NOT EXISTS game (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            original_price REAL NOT NULL,
            discount_price REAL NOT NULL,
            discount_startdate TEXT,
            discount_enddate TEXT,
            genre TEXT,
            release_date TEXT,
            maker TEXT,
            player_number TEXT,
            product_type TEXT,
            game_language TEXT,
            game_image_url TEXT,
            game_url TEXT,
            collect_date TEXT,
            UNIQUE(game_name, product_type, collect_date)
            )
        ''')
                
    conn.commit()
    
    #for test
    
    #cur.execute("DELETE FROM test_game")
    #conn.commit()
    
    #conn.close()
    return conn



# 2. 각 페이지에서 게임 링크 추출
def get_game_links_from_page(page):
    url = LIST_URL_TEMPLATE.format(page=page)
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"fail: {url} → {e}")
        
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a.product-item-link")
    links = []
    for a in items:
        href = a.get("href")
        if href:
            full_url = BASE_URL + href if href.startswith("/") else href
            links.append(full_url)
    return links

# 3. 전체 페이지 순회하면서 링크 수집
def get_all_game_links(max_pages=10):
    all_links = []
    for page in range(1, max_pages + 1):
        if page%20==0:
            print("page" + str(page) + " link 수집 중 "+str(datetime.now()))
        links = get_game_links_from_page(page)
        if not links:
            return all_links
        all_links.extend(links)
        time.sleep(random.uniform(0.5, 3))  # random delay
    return all_links
    
    ### for test ###
    #links = get_game_links_from_page(1)
    #all_links.extend(links)
    #time.sleep(random.uniform(0.5, 3))  # random delay
    #return all_links

# 4. 상세 페이지에서 게임 정보 수집
def get_game_info(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"fail: {url} → {e}")
    soup = BeautifulSoup(res.text, "html.parser")

    name_tag = soup.find('h1')
    game_name = name_tag.get_text(strip=True)
    
    product_type = 'SWC'

    game_url=res.url
    
    og_image = soup.find("meta", property="og:image")
    if og_image:
        game_image_url = og_image.get("content")
    else:
        game_image_url = None
        
                    
    price_tags = soup.select('span.price')
    if soup.select('span.old-price') and price_tags:
        original_price = soup.select_one('span.old-price span.price-wrapper span.price').text.strip()
        discount_price = price_tags[0].text.strip()
    elif price_tags:
        original_price = discount_price = price_tags[0].text.strip()
    else:
        original_price = discount_price = None
    
    if discount_price == '가격 확인 불가' or original_price == '가격 확인 불가':
        original_price = None
        discount_price = None
        
    discount_start_tag = soup.select_one('span.special-period-start')
    discount_end_tag = soup.select_one('span.special-period-end')
    discount_startdate = format_discount_date(discount_start_tag.text) if discount_start_tag else None
    discount_enddate = format_discount_date(discount_end_tag.text) if discount_end_tag else None

    release_tag = soup.select_one('.product-attribute.release_date .product-attribute-val')
    release_date = release_tag.text.strip() if release_tag else None

    if release_date:    
        try:
            date_obj = datetime.strptime(release_date, "%y.%m.%d")
            release_date = date_obj.strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # 장르
    genre_tag = soup.select_one('.product-attribute.game_category .attribute-item-val')
    genre = genre_tag.text.strip() if genre_tag else None

    # 메이커
    maker_tag = soup.select_one('.product-attribute.publisher .attribute-item-val')
    maker = maker_tag.text.strip() if maker_tag else None

    # 플레이 인원수
    player_tag = soup.select_one('.product-attribute.no_of_players .product-attribute-val')
    player_number = None
    if player_tag:
        text = player_tag.text.strip()
        if '✕' in text:
            player_number = text.split('✕')[1].strip()

    # 지원 언어
    lang_tag = soup.select_one('.product-attribute.supported_languages .attribute-item-val')
    game_language = lang_tag.text.strip() if lang_tag else None

    if '실물 패키지 상품' in soup.text:
        product_type = 'PHC'

    lang_tag = soup.select_one('div.product-attribute.supported_languages > div.product-attribute-val > div.attribute-item-val')
    game_language = lang_tag.text.strip() if lang_tag else None

    collect_date = datetime.now().date()
    
    time.sleep(random.uniform(0.5, 3))  # random delay

    return {
        "game_name": game_name,
        "original_price": original_price,
        "discount_price": discount_price,
        "discount_startdate": discount_startdate,
        "discount_enddate": discount_enddate,
        "genre": genre,
        "release_date": release_date,
        "maker": maker,
        "player_number": player_number,
        "product_type": product_type,
        "game_language": game_language,
        "game_image_url": game_image_url,
        "game_url": game_url,
        "collect_date": collect_date,
    }

# 5. DB에 저장
def save_game_to_db(conn, game):  
    if game["game_name"]!=None and game["original_price"]!=None:
        # game_name에 "OLED 모델", "에디션", "세트", "선불", "패키지"가 포함된 행 제거
        exclude_keywords = ['OLED 모델', '에디션', '세트', '선불', '패키지']
        if all(keyword not in game['game_name'] for keyword in exclude_keywords):
            game['original_price'] = int(game['original_price'].replace('₩', '').replace(',', ''))
            game['discount_price'] = int(game['discount_price'].replace('₩', '').replace(',', ''))
            try:
                c = conn.cursor()
                c.execute('''
                    INSERT OR IGNORE INTO game (game_name, original_price, discount_price, discount_startdate, discount_enddate, genre, release_date, maker, player_number, product_type, game_language, game_image_url, game_url, collect_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (game["game_name"], game["original_price"], game["discount_price"], game["discount_startdate"], game["discount_enddate"], game["genre"], game["release_date"], game["maker"], game["player_number"], game["product_type"], game["game_language"], game["game_image_url"], game["game_url"], game["collect_date"]))
                conn.commit()
            except Exception as e:
                print("저장 오류:", e)
        else:
            print(str(game["game_name"])+" 상품명 제외")
    else:
        print(str(game["game_name"])+" "+str(game["original_price"])+"db 오류")

# 6. 전체 실행``
if __name__ == "__main__":
    print("start : " + str(datetime.now()))
    conn = init_db()
    all_links = get_all_game_links()
    print("총 "+str(len(all_links))+"개의 링크 수집")

    for i, link in enumerate(all_links):
        if i==1 or i==2:
            print("get_game_info : " + str(datetime.now()))
        info = get_game_info(link)
        if i==1 or i==2:
            print("save_game_to_db : " + str(datetime.now()))
        save_game_to_db(conn, info)

    conn.close()
    print("end : " + str(datetime.now()))
    

# test time line (6257 sample)
#######################
# [test1] 
# 페이지 링크 가져오기 : random delay 0.5~3
# 세부정보 페이지 접근 : random delay 0
# 전체 작업시간 : 약 50분
# but 일정 페이지부터는 403 Forbidden
#######################
# [test2] 
# 페이지 링크 가져오기 : random delay 0.5~3
# 세부정보 페이지 접근 :  random delay 0.5~3
# 전체 작업시간 : 약 4시간 30분
# 1. start : 2025-04-24 10:52:04.859522
# 2~3. 페이지 링크 가져오기 -> 약 22분 소요
# page20 link 수집 중 2025-04-24 10:54:03.893412
# page40 link 수집 중 2025-04-24 10:55:59.331699
# page60 link 수집 중 2025-04-24 10:57:47.301612
# page80 link 수집 중 2025-04-24 10:59:35.003577
# page100 link 수집 중 2025-04-24 11:01:23.398836
# page120 link 수집 중 2025-04-24 11:03:07.362037
# page140 link 수집 중 2025-04-24 11:05:00.235060
# page160 link 수집 중 2025-04-24 11:06:53.302303
# page180 link 수집 중 2025-04-24 11:08:52.187800
# page200 link 수집 중 2025-04-24 11:10:44.011510
# page220 link 수집 중 2025-04-24 11:12:34.370062
# page240 link 수집 중 2025-04-24 11:14:22.759073
# page260 link 수집 중 2025-04-24 11:16:18.891709
# 4~5 정보 가져오기 및 DB 저장 (첫번째, 두번째만 시간기록) -> 약 4시간 10분 소요
# get_game_info : 2025-04-24 11:16:33.097583
# save_game_to_db : 2025-04-24 11:16:36.160259
# get_game_info : 2025-04-24 11:16:36.168961
# save_game_to_db : 2025-04-24 11:16:39.778025
# 6. end : 2025-04-24 15:23:49.724153