import sqlite3

conn = sqlite3.connect("mainDB.db")
cur = conn.cursor()

test_sample = {
    "game_name": "모여봐요 동물의 숲",
    "original_price": 64800,
    "discount_price": 64800,
    "discount_startdate": "2025-04-01",
    "discount_enddate": "2025-04-21",
    "genre": "커뮤니케이션",
    "release_date": "2020-03-20",
    "maker": "Nintendo",
    "player_number": "1~4명",
    "product_type": "1",
    "game_language": "한국어, 영어, 스페인어, 프랑스어, 독일어, 이탈리아어, 네덜란드어, 러시아어, 일본어, 중국어",
    "game_image_url": "https://store.nintendo.co.kr/media/catalog/product/cache/3be328691086628caca32d01ffcc430a/f/1/f1715bebde9ecc2e1cecc33e35166cbf87233ae35cc4dd6649645acc3a036696.jpg",
    "game_url": "https://store.nintendo.co.kr/70010000027621"
}

# INSERT OR IGNORE로 중복 방지
cur.execute('''
    INSERT OR IGNORE INTO game (
        game_name, original_price, discount_price,
        discount_startdate, discount_enddate, genre, release_date,
        maker, player_number, product_type, game_language,
        game_image_url, game_url
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (
    test_sample["game_name"],
    test_sample["original_price"],
    test_sample["discount_price"],
    test_sample["discount_startdate"],
    test_sample["discount_enddate"],
    test_sample["genre"],
    test_sample["release_date"],
    test_sample["maker"],
    test_sample["player_number"],
    test_sample["product_type"],
    test_sample["game_language"],
    test_sample["game_image_url"],
    test_sample["game_url"]
))

conn.commit()
conn.close()
print("샘플 게임 데이터가 추가되었습니다!")