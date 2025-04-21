import sqlite3

# DB 연결
conn = sqlite3.connect("mainDB.db")
cur = conn.cursor()

# 데이터를 SELECT해서 확인
cur.execute("SELECT * FROM game")  # game 테이블의 모든 데이터 조회
rows = cur.fetchall()

# 조회된 데이터 출력
for row in rows:
    print(row)

# 연결 종료
conn.close()